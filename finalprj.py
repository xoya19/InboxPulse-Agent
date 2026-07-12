import streamlit as st
import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from PIL import Image

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class EmailSummary(BaseModel):
    sender: str
    key_deadline: str
    subject: str
    action_required: bool

# --- Functions (Keep these clean) ---
def img_processing(img):
    # Pass the image as an argument here!
    return client.models.generate_content(
        model="gemini-3.5-flash",
        contents=["Summarize this email:", img],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EmailSummary,
        )
    )

def draft_email(sender, topic, tone):
    prompt = f"Draft a {tone} email reply to {sender} regarding {topic}. Keep it under 100 words."
    return client.models.generate_content(model="gemini-3.5-flash", contents=prompt).text

# --- Streamlit UI ---
st.title("InboxPulse Agent")
uploaded_file = st.file_uploader("Upload email screenshot...", type="png")
tone = st.selectbox("Select Tone", ["Formal", "Casual"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Email Screenshot")
    
    if st.button("Analyze & Draft"):
        with st.spinner("Processing..."):
            raw_response = img_processing(img)
            data = json.loads(raw_response.text)
            
            # Show the extraction
            st.write(f"**Sender:** {data['sender']}")
            st.write(f"**Topic:** {data['subject']}")
            
            # Draft the email
            draft = draft_email(data['sender'], data['subject'], tone)
            st.success("Draft Generated!")
            st.text_area("Reply Draft", value=draft, height=200)