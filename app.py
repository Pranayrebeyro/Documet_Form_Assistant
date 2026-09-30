import streamlit as st
from google import genai
from google.genai import types

from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
)

from email_service import send_email


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Document & Form Assistant",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ==================================================
# LOAD CUSTOM CSS
# ==================================================

try:
    with open("style.css", "r", encoding="utf-8") as css_file:
        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True,
        )
except FileNotFoundError:
    pass


# ==================================================
# CONFIGURATION
# ==================================================

MODEL_NAME = "gemini-3.5-flash"

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]


# ==================================================
# GEMINI CLIENT
# ==================================================

@st.cache_resource
def get_gemini_client():
    return genai.Client(
        api_key=GEMINI_API_KEY
    )


gemini_client = get_gemini_client()


# ==================================================
# CREATE GEMINI CHAT
# ==================================================

def create_chat():
    return gemini_client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        ),
    )


# ==================================================
# SESSION STATE
# ==================================================

if "name" not in st.session_state:
    st.session_state.name = ""

if "email" not in st.session_state:
    st.session_state.email = ""

if "onboarding_complete" not in st.session_state:
    st.session_state.onboarding_complete = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    st.session_state.chat = None

if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False

if "document_name" not in st.session_state:
    st.session_state.document_name = ""

if "summary" not in st.session_state:
    st.session_state.summary = None


# ==================================================
# NEW DOCUMENT
# ==================================================

def start_new_document():

    st.session_state.document_uploaded = False

    st.session_state.document_name = ""

    st.session_state.summary = None

    st.session_state.chat = create_chat()

    st.session_state.messages = [
        {
            "role": "assistant",
            "kind": "text",
            "content": WELCOME_MESSAGE_TEMPLATE.format(
                name=st.session_state.name
            ),
        }
    ]


# ==================================================
# APPLICATION HEADER
# ==================================================

st.markdown(
"""<div class="app-header">
<div class="app-logo">📄</div>
<div class="app-title">
Document &amp; Form
<span class="app-title-accent">Assistant</span>
</div>
<div class="app-subtitle">
Upload a document, understand the important details,
ask questions, and send the summary to your email.
</div>
</div>""",
unsafe_allow_html=True,
)


# ==================================================
# ONBOARDING
# ==================================================

if not st.session_state.onboarding_complete:

    st.markdown(
"""<div class="welcome-card">
<div class="welcome-title">👋 Welcome</div>
<div class="welcome-description">
Before we begin, tell me your name and
the email address where you want to receive
document summaries.
</div>
</div>""",
unsafe_allow_html=True,
    )

    st.write("")


    # --------------------------------------------------
    # NAME
    # --------------------------------------------------

    name = st.text_input(
        "Your Name",
        placeholder="Enter your name",
        key="onboarding_name",
    )


    # --------------------------------------------------
    # EMAIL
    # --------------------------------------------------

    email = st.text_input(
        "Email Address",
        placeholder="example@gmail.com",
        key="onboarding_email",
    )


    # --------------------------------------------------
    # CONTINUE
    # --------------------------------------------------

    if st.button(
        "Continue  →",
        type="primary",
        use_container_width=True,
    ):

        if not name.strip():

            st.error(
                "Please enter your name."
            )

        elif not email.strip():

            st.error(
                "Please enter your email address."
            )

        elif "@" not in email.strip():

            st.error(
                "Please enter a valid email address."
            )

        else:

            st.session_state.name = name.strip()

            st.session_state.email = email.strip()

            st.session_state.onboarding_complete = True

            st.session_state.chat = create_chat()

            st.session_state.messages = [
                {
                    "role": "assistant",
                    "kind": "text",
                    "content": WELCOME_MESSAGE_TEMPLATE.format(
                        name=st.session_state.name
                    ),
                }
            ]

            st.rerun()

    st.stop()


# ==================================================
# USER WELCOME
# ==================================================

st.markdown(
f"""<div class="user-welcome">
Welcome, {st.session_state.name}! 👋
</div>""",
unsafe_allow_html=True,
)


# ==================================================
# CURRENT DOCUMENT
# ==================================================

if st.session_state.document_uploaded:

    col1, col2 = st.columns([4, 1])

    with col1:

        st.markdown(
f"""<div class="document-card">
<span class="document-icon">📄</span>
<span>
<strong>Current document</strong><br>
{st.session_state.document_name}
</span>
</div>""",
unsafe_allow_html=True,
        )

    with col2:

        if st.button(
            "＋ New",
            use_container_width=True,
        ):

            start_new_document()

            st.rerun()


# ==================================================
# CHAT HISTORY
# ==================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message(
            "user",
            avatar="👤",
        ):

            st.write(
                message["content"]
            )

    elif message["role"] == "assistant":

        with st.chat_message(
            "assistant",
            avatar="🤖",
        ):

            st.write(
                message["content"]
            )


# ==================================================
# CHAT INPUT
# ==================================================

prompt = st.chat_input(
    "Ask a question or upload a document...",
    accept_file=True,
    file_type=[
        "jpg",
        "jpeg",
        "png",
    ],
)


# ==================================================
# HANDLE INPUT
# ==================================================

if prompt:

    user_text = prompt.text.strip()

    uploaded_file = None

    if prompt.files:
        uploaded_file = prompt.files[0]


    # ==================================================
    # DOCUMENT UPLOAD
    # ==================================================

    if uploaded_file is not None:

        photo_bytes = uploaded_file.getvalue()

        mime_type = uploaded_file.type

        st.session_state.document_uploaded = True

        st.session_state.document_name = (
            uploaded_file.name
        )

        st.session_state.summary = None


        # --------------------------------------------------
        # SHOW UPLOAD
        # --------------------------------------------------

        with st.chat_message(
            "user",
            avatar="👤",
        ):

            st.markdown(
f"""<div class="upload-message">
📎 <strong>{uploaded_file.name}</strong>
</div>""",
unsafe_allow_html=True,
            )

            st.image(
                photo_bytes,
                caption=uploaded_file.name,
                use_container_width=True,
            )

            if user_text:
                st.write(user_text)


        # --------------------------------------------------
        # SAVE USER MESSAGE
        # --------------------------------------------------

        user_message = (
            f"Uploaded document: {uploaded_file.name}"
        )

        if user_text:
            user_message += (
                f"\n\nQuestion: {user_text}"
            )

        st.session_state.messages.append(
            {
                "role": "user",
                "kind": "image",
                "content": user_message,
            }
        )


        # ==================================================
        # GEMINI VISION
        # ==================================================

        with st.chat_message(
            "assistant",
            avatar="🤖",
        ):

            with st.spinner(
                "Analyzing your document..."
            ):

                try:

                    image_part = types.Part.from_bytes(
                        data=photo_bytes,
                        mime_type=mime_type,
                    )


                    # ------------------------------------------
                    # ANALYSIS PROMPT
                    # ------------------------------------------

                    if user_text:

                        analysis_prompt = (
                            "Analyze the uploaded document "
                            "carefully and answer the user's "
                            "question.\n\n"
                            f"User question:\n{user_text}\n\n"
                            "After answering the question, "
                            "provide relevant document information "
                            "using clear headings and bullet points."
                        )

                    else:

                        analysis_prompt = """
Analyze this uploaded document carefully.

Create a clear, structured analysis using these
sections when the information is available:

📄 DOCUMENT TYPE

🎯 PURPOSE

📌 IMPORTANT INFORMATION

📅 DATES & DEADLINES

📎 REQUIRED DOCUMENTS / MATERIALS

📝 INSTRUCTIONS / NEXT STEPS

✅ ELIGIBILITY / REQUIREMENTS

⚠️ MISSING OR UNCLEAR INFORMATION

Important rules:

- Only use information visible in the document.
- Do not invent information.
- Do not guess missing dates or requirements.
- If something is unclear, explicitly say so.
- Keep the explanation concise and easy to understand.
"""


                    # ------------------------------------------
                    # GEMINI REQUEST
                    # ------------------------------------------

                    response = (
                        gemini_client.models.generate_content(
                            model=MODEL_NAME,
                            contents=[
                                image_part,
                                analysis_prompt,
                            ],
                            config=types.GenerateContentConfig(
                                system_instruction=SYSTEM_PROMPT
                            ),
                        )
                    )


                    # ------------------------------------------
                    # RESPONSE
                    # ------------------------------------------

                    if response.text:

                        answer = response.text.strip()

                        st.write(answer)

                        st.session_state.summary = answer

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "kind": "text",
                                "content": answer,
                            }
                        )

                    else:

                        st.error(
                            "Gemini did not return a response."
                        )


                except Exception as error:

                    st.error(
                        f"Gemini error: {error}"
                    )


    # ==================================================
    # FOLLOW-UP QUESTION
    # ==================================================

    elif user_text:

        with st.chat_message(
            "user",
            avatar="👤",
        ):

            st.write(user_text)


        st.session_state.messages.append(
            {
                "role": "user",
                "kind": "text",
                "content": user_text,
            }
        )


        # --------------------------------------------------
        # DOCUMENT CHECK
        # --------------------------------------------------

        if not st.session_state.document_uploaded:

            answer = (
                "Please upload a document first. "
                "Once you upload it, I can answer "
                "questions about that document."
            )

            with st.chat_message(
                "assistant",
                avatar="🤖",
            ):

                st.write(answer)


            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "kind": "text",
                    "content": answer,
                }
            )


        else:

            if st.session_state.chat is None:
                st.session_state.chat = create_chat()


            with st.chat_message(
                "assistant",
                avatar="🤖",
            ):

                with st.spinner(
                    "Thinking..."
                ):

                    try:

                        response = (
                            st.session_state.chat.send_message(
                                user_text
                            )
                        )


                        if response.text:

                            answer = response.text.strip()

                            st.write(answer)

                            st.session_state.messages.append(
                                {
                                    "role": "assistant",
                                    "kind": "text",
                                    "content": answer,
                                }
                            )

                        else:

                            st.error(
                                "Gemini did not return a response."
                            )


                    except Exception as error:

                        st.error(
                            f"Gemini error: {error}"
                        )


# ==================================================
# SUMMARY
# ==================================================

if st.session_state.document_uploaded:

    st.divider()

    st.markdown(
"""<div class="section-heading">
📋 Document Summary
</div>""",
unsafe_allow_html=True,
    )


    if st.session_state.summary:

        st.markdown(
"""<div class="summary-header">
<span>✨</span>
<span>AI-generated document analysis</span>
</div>""",
unsafe_allow_html=True,
        )

        st.write(
            st.session_state.summary
        )


        # ==================================================
        # EMAIL
        # ==================================================

        st.divider()

        st.markdown(
"""<div class="section-heading">
📧 Send Summary
</div>""",
unsafe_allow_html=True,
        )

        st.markdown(
f"""<div class="email-info">
The summary will be sent to
<strong>{st.session_state.email}</strong>.
</div>""",
unsafe_allow_html=True,
        )


        if st.button(
            "📧  Send Summary to Email",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Sending summary to your email..."
            ):

                success, message = send_email(
                    to_address=st.session_state.email,
                    subject=(
                        "Document Summary - "
                        "Document & Form Assistant"
                    ),
                    body=st.session_state.summary,
                )


            if success:

                st.success(
                    "Summary sent successfully! "
                    "Check your email. 📧"
                )

            else:

                st.error(
                    f"Couldn't send the summary: {message}"
                )


    else:

        st.info(
            "Upload a document to generate its summary."
        )


# ==================================================
# FOOTER
# ==================================================

st.markdown(
"""<div class="app-footer">
<span>Document &amp; Form Assistant</span>
<span>•</span>
<span>Powered by Gemini AI</span>
</div>""",
unsafe_allow_html=True,
)