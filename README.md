# 📄 Document & Form Assistant

Document & Form Assistant is an AI-powered application that helps users understand documents, notices, forms, timetables, syllabi, and other informational documents.

Users can upload a document image, receive an AI-powered analysis, ask follow-up questions, generate a structured summary, and send the summary to their email.

## ✨ Features

- 👤 Simple user onboarding
- 📄 Upload JPG, JPEG, and PNG documents
- 🤖 AI-powered document analysis using Gemini Vision
- 📌 Extract important information
- 📅 Identify dates and deadlines
- 📎 Identify required documents and materials
- 📝 Explain instructions and next steps
- ✅ Identify eligibility and requirements
- ⚠️ Highlight missing or unclear information
- 💬 Ask follow-up questions about the uploaded document
- 📋 Generate a structured document summary
- 📧 Send the summary through Gmail
- 🔄 Start a new document analysis without restarting the application
- 🎨 Clean white and teal user interface

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- Google GenAI SDK
- Pillow
- Gmail SMTP

## 📁 Project Structure

```text
document-form-assistant/
│
├── app.py
├── prompts.py
├── email_service.py
├── style.css
├── requirements.txt
├── .gitignore
├── README.md
│
├── .streamlit/
│   ├── config.toml
│   ├── secrets.toml
│   └── secrets.toml.example
│
└── venv/