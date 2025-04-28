import streamlit as st
import pandas as pd
from datetime import datetime

class TaskManager:
    def __init__(self):
        # यदि "tasks" session_state में नहीं है, तो इसे एक खाली सूची से इनिशियलाइज़ करें
        if "tasks" not in st.session_state:
            st.session_state.tasks = []  
        
        self.tasks = st.session_state.tasks  # सत्र स्थिति से टास्क सूची प्राप्त करें
        self.setup_ui()  # UI सेटअप को कॉल करें
    
    def setup_ui(self):
        st.title("📝 टास्क मैनेजमेंट सिस्टम")  # टाइटल सेट करें
        
        # टास्क जोड़ने के लिए फॉर्म बनाएं
        with st.form("task_form"):
            title = st.text_input("📌 शीर्षक")  # टास्क का शीर्षक
            desc = st.text_area("📝 विवरण")  # टास्क का विवरण
            priority = st.selectbox("⚡ प्राथमिकता", ["उच्च", "मध्यम", "निम्न"])  # प्राथमिकता सेलेक्ट करें
            deadline = st.date_input("📅 समय सीमा")  # समय सीमा चुनें
            category = st.text_input("📂 श्रेणी")  # श्रेणी इनपुट करें
            submit = st.form_submit_button("➕ टास्क जोड़ें")  # टास्क जोड़ने का बटन
            
            if submit:
                self.add_task(title, desc, priority, deadline, category)  # टास्क जोड़ने का फंक्शन कॉल करें
        
        # यदि टास्क उपलब्ध हैं, तो उन्हें टेबल में दिखाएं
        if self.tasks:
            df = pd.DataFrame(self.tasks)  # डेटा को DataFrame में बदलें
            df = df.sort_values(by="deadline")  # समय सीमा के अनुसार सॉर्ट करें
            st.write("### 🗂️ आपकी टास्क लिस्ट")
            st.dataframe(df)  # टास्क को टेबल के रूप में दिखाएं
            
            # टास्क हटाने का ऑप्शन दें
            task_to_delete = st.selectbox("🗑️ हटाने के लिए टास्क चुनें", df["title"].tolist() if not df.empty else [])
            if st.button("❌ टास्क हटाएं") and task_to_delete:
                self.delete_task(task_to_delete)  # टास्क हटाने का फंक्शन कॉल करें

    def add_task(self, title, desc, priority, deadline, category):
        """नया टास्क जोड़ने के लिए फंक्शन"""
        if not title or not deadline:
            st.error("⚠️ शीर्षक और समय सीमा आवश्यक हैं!")  # यदि कोई आवश्यक फील्ड खाली है तो त्रुटि संदेश दिखाएं
            return
        
        # टास्क को सत्र स्थिति में जोड़ें
        self.tasks.append({
            "title": title,
            "desc": desc,
            "priority": priority,
            "deadline": deadline.strftime("%Y-%m-%d"),  # समय सीमा को स्ट्रिंग में बदलें
            "category": category
        })
        
        st.session_state.tasks = self.tasks  # सत्र स्थिति अपडेट करें
        st.success("✅ टास्क सफलतापूर्वक जोड़ी गई!")  # सफलता संदेश दिखाएं

    def delete_task(self, title):
        """चयनित टास्क को हटाने के लिए फंक्शन"""
        self.tasks = [task for task in self.tasks if task["title"] != title]  # सूची से टास्क हटाएं
        st.session_state.tasks = self.tasks  # सत्र स्थिति अपडेट करें
        st.success("🗑️ टास्क सफलतापूर्वक हटाई गई!")  # सफलता संदेश दिखाएं

# यदि यह स्क्रिप्ट मुख्य फाइल के रूप में चलाई जा रही है, तो TaskManager क्लास को इनिशियलाइज़ करें
if __name__ == "__main__":
    TaskManager()