
import os
import pandas as pd
import spacy
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'  # टेसरैक्ट एग्जीक्यूटेबल के लिए पाथ जोड़ें।

# इमेज से टेक्स्ट निकालने का फंक्शन।
def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)  # इमेज को खोलें।
        text = pytesseract.image_to_string(img)  # OCR का उपयोग करके टेक्स्ट निकालें।
        return text
    except Exception as e:
        print(f"Error processing {image_path}: {e}")  # यदि कोई त्रुटि हो तो प्रिंट करें।
        return None

# किसी डायरेक्टरी से सभी इमेज फाइल्स का टेक्स्ट निकालने का फंक्शन।
def extract_text_from_directory(directory):
    data = []  # डेटा को स्टोर करने के लिए एक लिस्ट।
    
    for filename in os.listdir(directory):  
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):  # केवल इमेज फाइल्स चुनें।
            file_path = os.path.join(directory, filename)  
            text = extract_text_from_image(file_path)   
            data.append({'file_name': filename, 'extracted_text': text})  
    df = pd.DataFrame(data) 
    return df

# टेक्स्ट से संगठनों (Organizations) के नाम निकालने का फंक्शन।
def extract_organizations(df):
    nlp = spacy.load("en_core_web_sm")  # स्पेसी मॉडल लोड करें।
    org_data = []  # संगठनों के नाम स्टोर करने के लिए लिस्ट।
    
    for index, row in df.iterrows():  # प्रत्येक टेक्स्ट पर लूप लगाएँ।
        if pd.notna(row["extracted_text"]):  # नॉन-नल टेक्स्ट पर कार्य करें।
            doc = nlp(row["extracted_text"])  
            for ent in doc.ents:  
                if ent.label_ == "ORG":  # यदि एंटिटी का प्रकार "ORG" है।
                    org_data.append({'file_name': row['file_name'], 'organization': ent.text})  
    
    return pd.DataFrame(org_data)  # संगठनों को डेटा फ्रेम में स्टोर करें।

# संगठनों के नाम एक फाइल में सेव करने का फंक्शन।
def save_organizations_to_file(df, file_path):
    try:
        with open(file_path, "w") as f:
            for _, row in df.iterrows():
                f.write(f"{row['file_name']}: {row['organization']}\n")
        print(f"Organizations saved to {file_path}") 
    except Exception as e:
        print(f"Error saving file: {e}")  

# मुख्य फंक्शन जो सभी कार्यों को व्यवस्थित करता है।
def main(directory, output_file):
    df = extract_text_from_directory(directory)  
    org_df = extract_organizations(df)  
    save_organizations_to_file(org_df, output_file)  

# यदि यह स्क्रिप्ट डायरेक्ट रूप से चलाई जाए तो इसे निष्पादित करें।
if __name__ == "__main__":
    directory = "path_to_directory"  # उस डायरेक्टरी का पथ जहाँ इमेज फाइल्स मौजूद हैं।
    output_file = "organizations.txt"  # आउटपुट फाइल का नाम।
    main(directory, output_file)  # मुख्य फंक्शन को कॉल करें।