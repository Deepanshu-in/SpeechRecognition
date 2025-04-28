import os
import sys
import math
import tempfile

try:
    from moviepy.editor import VideoFileClip
except ImportError:
    print("moviepy is required. Install with 'pip install moviepy'")
    sys.exit(1)

try:
    from pydub import AudioSegment
except ImportError:
    print("pydub is required. Install with 'pip install pydub'")
    sys.exit(1)

try:
    import speech_recognition as sr
except ImportError:
    print("SpeechRecognition is required. Install with 'pip install SpeechRecognition'")
    sys.exit(1)

try:
    from transformers import pipeline
except ImportError:
    print("transformers is required. Install with 'pip install transformers'")
    sys.exit(1)


def extract_audio_chunks(video_path, chunk_length_ms=60000):
    """
    Video file se audio extract karo aur usse chunks mein baanto.
    Har audio chunk ke liye file paths ki list return karta hai.
    """
    temp_files = []
    try:
        video = VideoFileClip(video_path)
    except Exception as e:
        raise Exception(f"Error loading video file: {e}")

    if video.audio is None:
        raise Exception("The video file has no audio track.")

    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_audio_filename = temp_audio_file.name
    temp_audio_file.close()
    
    try:
        video.audio.write_audiofile(temp_audio_filename, logger=None)
    except Exception as e:
        raise Exception(f"Error extracting audio: {e}")

    try:
        audio = AudioSegment.from_wav(temp_audio_filename)
    except Exception as e:
        os.remove(temp_audio_filename)
        raise Exception(f"Error loading extracted audio: {e}")

    duration_ms = len(audio)
    num_chunks = math.ceil(duration_ms / chunk_length_ms)

    for i in range(num_chunks):
        start_ms = i * chunk_length_ms
        end_ms = min((i + 1) * chunk_length_ms, duration_ms)
        chunk = audio[start_ms:end_ms]
        chunk_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        chunk_filename = chunk_temp_file.name
        chunk_temp_file.close()
        try:
            chunk.export(chunk_filename, format="wav")
        except Exception as e:
            raise Exception(f"Error exporting audio chunk {i}: {e}")
        temp_files.append(chunk_filename)

    os.remove(temp_audio_filename)
    return temp_files


def transcribe_audio_chunks(chunk_files):
    """
    SpeechRecognition library ka upyog karke har audio chunk ko transcribe karo.
    Combined transcription text return karta hai.
    """
    recognizer = sr.Recognizer()
    combined_text = ""
    for idx, chunk_file in enumerate(chunk_files):
        try:
            with sr.AudioFile(chunk_file) as source:
                audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                combined_text += text + " "
            except sr.UnknownValueError:
                print(f"Warning: No speech detected in chunk {idx}.")
            except sr.RequestError as e:
                print(f"API error in chunk {idx}: {e}. Skipping this chunk.")
        except Exception as e:
            print(f"Error processing chunk {idx}: {e}")
        os.remove(chunk_file)
    return combined_text.strip()


def summarize_text(text):
    """
    Transcription ko teen hisson mein baanto aur transformers summarization pipeline ka use karke har ek ka summary banao.
    Introduction, Main Topics, aur Conclusion ke summary ke saath ek dictionary return karta hai.
    """
    if not text:
        raise Exception("No transcribed text available for summarization.")

    words = text.split()
    total_words = len(words)
    segment_size = total_words // 3 if total_words >= 3 else total_words

    segments = {
        "Introduction": " ".join(words[:segment_size]),
        "Main Topics": " ".join(words[segment_size:2*segment_size]),
        "Conclusion": " ".join(words[2*segment_size:])
    }

    try:
        summarizer = pipeline("summarization")
    except Exception as e:
        raise Exception(f"Error initializing summarization pipeline: {e}")

    structured_summary = {}
    for section, content in segments.items():
        if content.strip():
            try:
                summary = summarizer(content, max_length=130, min_length=30, do_sample=False)
                structured_summary[section] = summary[0]['summary_text']
            except Exception as e:
                structured_summary[section] = f"Error during summarization: {e}"
        else:
            structured_summary[section] = "No content available for summarization."
    return structured_summary


def main():
    """
    Video summarization process chalane ke liye main function.
    Usage:
    python video_summary.py <video_file_path>
    """
    if len(sys.argv) < 2:
        print("Usage: python video_summary.py <video_file_path>")
        sys.exit(1)

    video_path = sys.argv[1]
    if not os.path.exists(video_path):
        print("Error: The specified video file does not exist.")
        sys.exit(1)

    try:
        print("Extracting audio and splitting into chunks...")
        chunk_files = extract_audio_chunks(video_path, chunk_length_ms=60000)
        print(f"Extracted {len(chunk_files)} audio chunks.")
    except Exception as e:
        print(f"Error during audio extraction: {e}")
        sys.exit(1)

    try:
        print("Transcribing audio chunks...")
        transcription = transcribe_audio_chunks(chunk_files)
        if not transcription:
            print("No transcribed text available. Exiting.")
            sys.exit(1)
        print("Transcription complete.")
    except Exception as e:
        print(f"Error during transcription: {e}")
        sys.exit(1)

    try:
        print("Generating structured summary...")
        summary = summarize_text(transcription)
        print("\nStructured Summary:")
        print("\nIntroduction:\n", summary.get("Introduction", ""))
        print("\nMain Topics:\n", summary.get("Main Topics", ""))
        print("\nConclusion:\n", summary.get("Conclusion", ""))
    except Exception as e:
        print(f"Error during summarization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()