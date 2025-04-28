import streamlit as st
import tempfile
import os
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import scipy.signal
import pandas as pd
import re
from collections import Counter
from scipy.fftpack import dct
from pydub import AudioSegment
import soundfile as sf
import whisper  # OpenAI's Whisper for speech recognition
import sounddevice as sd
from scipy.io.wavfile import write as write_wav
import time
import queue
import threading

# Set page configuration
st.set_page_config(
    page_title="Speech Recognition & Analysis App",
    page_icon="🎤",
    layout="wide"
)

# Function to extract MS-LFB features as mentioned in the research paper
def extract_ms_lfb(y, sr, n_mels=40, n_fft=512, hop_length=160):
    """
    Extract Mel-Scaled Log Filter Bank (MS-LFB) features.
    """
    # Pre-emphasis filter
    pre_emphasis = 0.97
    y = np.append(y[0], y[1:] - pre_emphasis * y[:-1])
    
    # Compute mel spectrogram
    mel_spectrogram = librosa.feature.melspectrogram(
        y=y, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels
    )
    
    # Convert to log scale (log-mel spectrogram)
    ms_lfb = np.log(mel_spectrogram + 1e-9)
    
    return ms_lfb

# Function to extract MFCC features as mentioned in the research paper
def extract_mfcc(y, sr, n_mfcc=12, n_mels=40, n_fft=512, hop_length=160):
    """
    Extract Mel Frequency Cepstral Coefficients (MFCC) features.
    """
    # Get MS-LFB features
    ms_lfb = extract_ms_lfb(y, sr, n_mels, n_fft, hop_length)
    
    # Apply DCT to get MFCCs
    mfcc = dct(ms_lfb, type=2, axis=0, norm='ortho')[:n_mfcc]
    
    return mfcc

# Function to analyze text based on NLP techniques
def analyze_text(text):
    """
    Analyze the recognized text.
    """
    if not text:
        return None
        
    # Lowercase and split text
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Basic statistics
    word_count = len(words)
    char_count = len(text)
    
    # Word frequency
    word_freq = dict(Counter(words).most_common())
    
    # Command detection (based on common voice commands from the paper)
    commands = ["yes", "no", "up", "down", "left", "right", "on", "off", "stop", "go"]
    detected_commands = [cmd for cmd in commands if cmd in words]
    
    # Sentence analysis
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    sentence_count = len(sentences)
    avg_sentence_length = word_count / max(1, sentence_count)
    
    return {
        "word_count": word_count,
        "char_count": char_count,
        "word_frequency": word_freq,
        "detected_commands": detected_commands,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sentence_length,
    }

# Function to transcribe audio using OpenAI's Whisper with language control
def transcribe_with_whisper(file_path, model_name="base", language="en"):
    """
    Transcribe audio using OpenAI's Whisper model with explicit language control.
    
    Args:
        file_path: Path to the audio file
        model_name: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        language: Language code (e.g., 'en' for English, 'hi' for Hindi)
        
    Returns:
        Transcribed text
    """
    try:
        # Load the model (this will download it the first time)
        model = whisper.load_model(model_name)
        
        # Set options to force specific language and disable translation
        options = {
            "language": language,  # Force specific language
            "task": "transcribe"   # Force transcription (not translation)
        }
        
        # Transcribe the audio with specific options
        result = model.transcribe(file_path, **options)
        
        return result["text"]
    except Exception as e:
        st.error(f"Error transcribing with Whisper: {str(e)}")
        return ""

# Function to record audio from microphone
def record_audio(duration, sample_rate=16000):
    """
    Record audio from microphone for a specified duration.
    
    Args:
        duration: Recording duration in seconds
        sample_rate: Sample rate in Hz
        
    Returns:
        Path to the recorded audio file
    """
    try:
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file_path = temp_file.name
        temp_file.close()
        
        # Record audio
        status_text.text("Recording... Speak now!")
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        
        # Update progress bar during recording
        for i in range(100):
            time.sleep(duration/100)
            progress_bar.progress(i + 1)
        
        sd.wait()  # Wait until recording is finished
        status_text.text("Recording finished!")
        
        # Save recording to file
        write_wav(temp_file_path, sample_rate, recording)
        
        return temp_file_path
    
    except Exception as e:
        st.error(f"Error recording audio: {str(e)}")
        return None

def main():
    st.title("Speech Recognition & Audio Analysis App")
    st.write("Record or upload audio for transcription and detailed analysis.")
    
    # Initialize session state
    if 'recognized_text' not in st.session_state:
        st.session_state.recognized_text = ""
    if 'audio_data' not in st.session_state:
        st.session_state.audio_data = None
    if 'sample_rate' not in st.session_state:
        st.session_state.sample_rate = None
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        whisper_model = st.selectbox(
            "Whisper Model",
            ["tiny", "base", "small", "medium", "large"],
            index=1,  # Default to "base"
            help="Select Whisper model size. Larger models are more accurate but slower."
        )
        
        # Language selection (English and Hindi only)
        language = st.selectbox(
            "Language",
            ["en", "hi"],
            index=0,  # Default to English
            format_func=lambda x: "English" if x == "en" else "Hindi",
            help="Select the language you're speaking (English or Hindi)"
        )
        
        # Recording parameters
        st.subheader("Recording Settings")
        recording_duration = st.slider(
            "Recording Duration (seconds)",
            min_value=1,
            max_value=30,
            value=5,
            help="Set the duration for recording audio from microphone."
        )
        
        sample_rate = st.selectbox(
            "Sample Rate (Hz)",
            [8000, 16000, 22050, 44100],
            index=1,  # Default to 16000 Hz
            help="Higher sample rates provide better quality but larger files."
        )
    
    # Create tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["Record Microphone", "Upload Audio File", "Analysis Results"])
    
    # Microphone recording tab
    with tab1:
        st.header("Record from Microphone")
        st.write(f"Click the button below to record audio in {language.upper()} language from your microphone.")
        
        if st.button("Start Recording", type="primary"):
            try:
                # Record audio
                audio_file_path = record_audio(recording_duration, sample_rate)
                
                if audio_file_path and os.path.exists(audio_file_path):
                    # Load the audio file using librosa for analysis
                    y, sr = librosa.load(audio_file_path, sr=None)
                    
                    # Store data in session state
                    st.session_state.audio_data = y
                    st.session_state.sample_rate = sr
                    
                    # Display audio playback
                    st.audio(audio_file_path)
                    
                    # Transcribe with Whisper using selected language
                    with st.spinner(f"Transcribing with Whisper ({whisper_model} model) in {language.upper()}..."):
                        transcription = transcribe_with_whisper(audio_file_path, model_name=whisper_model, language=language)
                        st.session_state.recognized_text = transcription
                    
                    st.session_state.processed = True
                    
                    # Cleanup temporary file
                    if os.path.exists(audio_file_path):
                        os.remove(audio_file_path)
                    
                    st.success("Processing complete!")
                    
                    # Display the transcribed text
                    st.subheader("Recognized Text:")
                    st.markdown(
                        f"""
                        <div style="background-color: white; color: black; padding: 20px; 
                             border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                            <p style="font-size: 18px; line-height: 1.6;">{st.session_state.recognized_text}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            except Exception as e:
                st.error(f"Error recording or processing audio: {str(e)}")
    
    # File upload tab
    with tab2:
        st.header("Upload Audio File")
        st.write(f"Upload an audio file for transcription in {language.upper()} language and analysis.")
        
        # File uploader
        uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "m4a", "ogg"])
        
        if uploaded_file is not None:
            # Display audio player
            st.audio(uploaded_file)
            
            # Process button
            if st.button("Process Uploaded Audio", type="primary"):
                with st.spinner("Processing audio file..."):
                    try:
                        # Save uploaded file temporarily
                        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            file_path = tmp_file.name
                        
                        # Process based on file type
                        if file_extension == '.mp3' or file_extension == '.m4a' or file_extension == '.ogg':
                            # Convert to WAV for processing
                            try:
                                audio = AudioSegment.from_file(file_path)
                                wav_path = file_path.replace(file_extension, '.wav')
                                audio.export(wav_path, format='wav')
                                # Remove the original temp file
                                os.remove(file_path)
                                file_path = wav_path
                            except Exception as e:
                                st.error(f"Error converting audio file: {str(e)}")
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                                st.stop()
                        
                        # Load the audio file using librosa for analysis
                        y, sr = librosa.load(file_path, sr=None)
                        
                        # Store data in session state
                        st.session_state.audio_data = y
                        st.session_state.sample_rate = sr
                        
                        # Transcribe with Whisper using selected language
                        with st.spinner(f"Transcribing with Whisper ({whisper_model} model) in {language.upper()}..."):
                            transcription = transcribe_with_whisper(file_path, model_name=whisper_model, language=language)
                            st.session_state.recognized_text = transcription
                        
                        st.session_state.processed = True
                        
                        # Cleanup temporary file
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        
                        st.success("Processing complete!")
                        
                        # Display the transcribed text
                        st.subheader("Recognized Text:")
                        st.markdown(
                            f"""
                            <div style="background-color: white; color: black; padding: 20px; 
                                 border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                                <p style="font-size: 18px; line-height: 1.6;">{st.session_state.recognized_text}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    except Exception as e:
                        st.error(f"Error processing audio file: {str(e)}")
                        st.session_state.processed = False
    
    # Analysis results tab
    with tab3:
        st.header("Analysis Results")
        
        # Option to edit the transcription
        if st.session_state.recognized_text:
            st.write("#### Edit Transcription:")
            edited_text = st.text_area(
                "Review and edit the transcription if needed:",
                value=st.session_state.recognized_text,
                height=150
            )
            
            if edited_text != st.session_state.recognized_text:
                if st.button("Update Transcription"):
                    st.session_state.recognized_text = edited_text
                    st.success("Transcription updated!")
                    st.rerun()
            
            # Clear button
            if st.button("Clear Text", key="clear_btn"):
                st.session_state.recognized_text = ""
                st.rerun()
        
        # Analysis section
        if st.session_state.processed and st.session_state.audio_data is not None:
            st.subheader("Audio Analysis")
            
            y = st.session_state.audio_data
            sr = st.session_state.sample_rate
            
            # Create tabs for different analysis types
            analysis_tabs = st.tabs(["Time Domain", "Frequency Domain", "Spectrogram", "MS-LFB", "MFCC"])
            
            with analysis_tabs[0]:
                st.write("### Time Domain Analysis")
                
                # Display waveform
                fig, ax = plt.subplots(figsize=(10, 4))
                times = np.arange(len(y)) / sr
                ax.plot(times, y, color='blue')
                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Amplitude')
                ax.set_title('Audio Waveform')
                ax.grid(True)
                st.pyplot(fig)
                
                # Display statistics
                st.write("#### Waveform Statistics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Duration (s)", f"{len(y)/sr:.2f}")
                with col2:
                    st.metric("Sample Rate", f"{sr} Hz")
                with col3:
                    st.metric("Max Amplitude", f"{np.max(np.abs(y)):.3f}")
                with col4:
                    st.metric("RMS Energy", f"{np.sqrt(np.mean(y**2)):.3f}")
            
            with analysis_tabs[1]:
                st.write("### Frequency Domain Analysis")
                
                # Compute FFT
                n_fft = 2048
                Y = np.abs(np.fft.rfft(y, n_fft))
                freqs = np.fft.rfftfreq(n_fft, 1/sr)
                
                # Plot FFT
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(freqs, Y, color='green')
                ax.set_xlabel('Frequency (Hz)')
                ax.set_ylabel('Magnitude')
                ax.set_title('Frequency Spectrum')
                ax.set_xlim([0, min(sr/2, 8000)])  # Limit to Nyquist or 8kHz
                ax.grid(True)
                st.pyplot(fig)
                
                # Display dominant frequencies
                peak_indices = scipy.signal.find_peaks(Y, height=np.max(Y)*0.1)[0]
                peak_freqs = freqs[peak_indices]
                peak_mags = Y[peak_indices]
                
                # Sort by magnitude
                if len(peak_freqs) > 0:
                    sorted_indices = np.argsort(peak_mags)[::-1]
                    top_peaks = sorted_indices[:min(5, len(sorted_indices))]  # Top 5 peaks
                    
                    st.write("#### Dominant Frequencies")
                    freq_data = {
                        "Frequency (Hz)": [f"{peak_freqs[i]:.1f}" for i in top_peaks if i < len(peak_freqs)],
                        "Magnitude": [f"{peak_mags[i]:.2f}" for i in top_peaks if i < len(peak_mags)]
                    }
                    if freq_data["Frequency (Hz)"]:
                        st.dataframe(pd.DataFrame(freq_data))
                    else:
                        st.info("No dominant frequencies detected.")
            
            with analysis_tabs[2]:
                st.write("### Spectrogram Analysis")
                
                # Compute spectrogram
                fig, ax = plt.subplots(figsize=(10, 4))
                D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
                img = librosa.display.specshow(D, x_axis='time', y_axis='log', ax=ax, sr=sr)
                ax.set_title('Spectrogram')
                fig.colorbar(img, ax=ax, format='%+2.0f dB')
                st.pyplot(fig)
                
                # Energy distribution over time
                st.write("#### Energy Distribution Over Time")
                frame_length = 1024
                hop_length = 512
                energy = np.array([
                    np.sum(np.abs(y[i:i+frame_length]**2)) 
                    for i in range(0, len(y)-frame_length, hop_length)
                ])
                frames = range(len(energy))
                time = librosa.frames_to_time(frames, sr=sr, hop_length=hop_length)
                
                fig, ax = plt.subplots(figsize=(10, 2))
                ax.plot(time, energy, color='orange')
                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Energy')
                ax.set_title('Energy Over Time')
                ax.grid(True)
                st.pyplot(fig)
            
            with analysis_tabs[3]:
                st.write("### MS-LFB Features (Mel-Scaled Log Filter Bank)")
                
                try:
                    # Extract MS-LFB features
                    ms_lfb = extract_ms_lfb(y, sr)
                    
                    # Display MS-LFB features
                    fig, ax = plt.subplots(figsize=(10, 4))
                    img = librosa.display.specshow(
                        ms_lfb, x_axis='time', y_axis='mel', 
                        sr=sr, ax=ax
                    )
                    ax.set_title('MS-LFB Features')
                    fig.colorbar(img, ax=ax, format='%+2.0f')
                    st.pyplot(fig)
                    
                    st.write("""
                    **About MS-LFB:** MS-LFB features measure audio frequency energy directly within the 
                    Mel spectral band space to produce detailed audible frequency maps. They provide 
                    greater information granularity and typically yield better accuracy when processing 
                    disturbed audio signals, as described in the research paper.
                    """)
                except Exception as e:
                    st.error(f"Error computing MS-LFB features: {str(e)}")
            
            with analysis_tabs[4]:
                st.write("### MFCC Features (Mel Frequency Cepstral Coefficients)")
                
                try:
                    # Extract MFCC features
                    mfcc = extract_mfcc(y, sr)
                    
                    # Display MFCC features
                    fig, ax = plt.subplots(figsize=(10, 4))
                    img = librosa.display.specshow(
                        mfcc, x_axis='time', ax=ax
                    )
                    ax.set_title('MFCC Features')
                    fig.colorbar(img, ax=ax, format='%+2.0f')
                    st.pyplot(fig)
                    
                    st.write("""
                    **About MFCC:** MFCC features are derived by applying a Discrete Cosine Transform (DCT) 
                    on MS-LFB data, producing a condensed representation which minimizes redundant information. 
                    The research paper notes that MFCCs offer computational efficiency, though this comes 
                    with the disadvantage that spectrum compression reduces important spectral data.
                    """)
                except Exception as e:
                    st.error(f"Error computing MFCC features: {str(e)}")
        
        # Text analysis section
        if st.session_state.recognized_text:
            st.subheader("Text Analysis")
            
            text_analysis = analyze_text(st.session_state.recognized_text)
            if text_analysis:
                # Create columns for different metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Word Count", text_analysis["word_count"])
                
                with col2:
                    st.metric("Character Count", text_analysis["char_count"])
                
                with col3:
                    st.metric("Sentence Count", text_analysis["sentence_count"])
                
                # Display detected commands if any
                if text_analysis["detected_commands"]:
                    st.write("#### Detected Commands:")
                    st.write(", ".join(text_analysis["detected_commands"]))
                    
                    # Show which commands from the paper were detected
                    st.info("""
                    The detected commands match those from the research paper, which focused on 
                    ten target commands: "yes", "no", "up", "down", "left", "right", "on", "off", "stop", and "go".
                    """)
                
                # Display word frequency
                st.write("#### Word Frequency:")
                
                # Create a bar chart for word frequency
                word_freq = text_analysis["word_frequency"]
                if word_freq:
                    # Sort by frequency and take top 10
                    sorted_freq = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10])
                    
                    fig, ax = plt.subplots(figsize=(10, 4))
                    ax.bar(sorted_freq.keys(), sorted_freq.values(), color='skyblue')
                    ax.set_xlabel('Words')
                    ax.set_ylabel('Frequency')
                    ax.set_title('Word Frequency')
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Also show as a table
                    st.dataframe(pd.DataFrame(list(word_freq.items()), 
                                               columns=['Word', 'Frequency']).sort_values('Frequency', ascending=False))

if __name__ == "__main__":
    main()