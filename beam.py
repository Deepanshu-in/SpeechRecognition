import streamlit as st
from PIL import Image
import pytesseract
import os

# Tesseract ko configure karna (yadi aap Windows par hain)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def main():
    st.title("Image to Text Extractor")
    
    uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg", "bmp", "gif", "tiff"])
    
    if uploaded_file is not None:
        try:
            # Image ko open karna
            image = Image.open(uploaded_file)
            
            # Image ko display karna
            st.image(image, caption='Uploaded Image', use_column_width=True)
            
            # OCR ke madhyam se text extract karna
            extracted_text = pytesseract.image_to_string(image)
            
            # Extracted text ka preview dena
            st.subheader("Extracted Text")
            st.text_area("Preview", extracted_text, height=200)
            
            # Output file ka naam lene ke liye input
            output_filename = st.text_input("Enter output file name (without extension)", "output")
            
            if st.button("Save as .txt"):
                # Text ko .txt file me save karna
                with open(f"{output_filename}.txt", "w", encoding='utf-8') as text_file:
                    text_file.write(extracted_text)
                st.success(f"Text successfully saved as {output_filename}.txt")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()