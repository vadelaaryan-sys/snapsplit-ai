"""
app.py - SnapSplit: Receipt & Expense Tracker / Bill Splitter
Built with Streamlit + Gemini Vision API + Multi-Channel Action Dispatcher
"""

import streamlit as st
from PIL import Image
import pandas as pd
import json
import os

from ai_service import analyze_receipt, chat_about_receipt
from send_action import send_email, send_telegram, send_whatsapp
from prompts import SUMMARY_PROMPT_TEMPLATE

# --- Page Config ---
st.set_page_config(
    page_title="SnapSplit · Receipt & Bill Splitter",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #555555;
        margin-bottom: 20px;
    }
    .card {
        background-color: #f8f9fa;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 15px;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "receipt_image" not in st.session_state:
    st.session_state.receipt_image = None
if "analysis_raw" not in st.session_state:
    st.session_state.analysis_raw = None
if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "people_list" not in st.session_state:
    st.session_state.people_list = ["Alice", "Bob"]

# Helper to read secret safely
def get_secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return os.getenv(key, default)

# --- Sidebar: Configuration & Onboarding ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/receipt.png", width=70)
    st.title("⚙️ Setup & Actions")
    
    # 1. API Keys Section
    st.subheader("1. Gemini API Key")
    default_gemini_key = get_secret("GEMINI_API_KEY", "")
    gemini_api_key = st.text_input("Google Gemini API Key", value=default_gemini_key, type="password", help="Get free key from Google AI Studio (aistudio.google.com)")

    st.markdown("---")
    
    # 2. Action Tool Selection
    st.subheader("2. Choose Action Channel")
    action_channel = st.radio(
        "Where should summaries be sent?",
        ["📧 Email (Gmail)", "💬 Telegram", "📱 WhatsApp"],
        index=0,
        help="Select the destination tool for sending split receipts"
    )
    
    if action_channel == "📧 Email (Gmail)":
        st.info("💡 **Gmail SMTP**: Free & built-in using Python smtplib.")
        recipient_email = st.text_input("Recipient Email", value=get_secret("RECIPIENT_EMAIL", "student@example.com"))
        gmail_address = st.text_input("Sender Gmail Address", value=get_secret("GMAIL_ADDRESS", ""))
        gmail_app_password = st.text_input("Gmail App Password (16-char)", value=get_secret("GMAIL_APP_PASSWORD", ""), type="password")
        
    elif action_channel == "💬 Telegram":
        st.info("💡 **Telegram Bot**: Message @BotFather on Telegram to get a token.")
        telegram_chat_id = st.text_input("Recipient Chat ID", value=get_secret("TELEGRAM_CHAT_ID", ""))
        telegram_bot_token = st.text_input("Telegram Bot Token", value=get_secret("TELEGRAM_BOT_TOKEN", ""), type="password")
        
    elif action_channel == "📱 WhatsApp":
        st.info("💡 **WhatsApp via Twilio**: Uses Twilio sandbox/account API.")
        whatsapp_number = st.text_input("Recipient WhatsApp # (e.g. +14155238886)", value=get_secret("WHATSAPP_TO_NUMBER", ""))
        twilio_sid = st.text_input("Twilio Account SID", value=get_secret("TWILIO_ACCOUNT_SID", ""), type="password")
        twilio_token = st.text_input("Twilio Auth Token", value=get_secret("TWILIO_AUTH_TOKEN", ""), type="password")
        twilio_from = st.text_input("Twilio Sender Number", value=get_secret("TWILIO_FROM_NUMBER", "+14155238886"))

# --- Main App Header ---
st.markdown('<div class="main-title">🧾 SnapSplit</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Snap a receipt 📸 ➔ Gemini Vision parses it 🤖 ➔ Split the bill & send summary to Email/Telegram/WhatsApp 🚀</div>', unsafe_allow_html=True)

# --- Layout: 2 Columns ---
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📸 Step 1: Upload or Snap Receipt")
    
    upload_tab, camera_tab = st.tabs(["📁 File Upload", "📷 Camera"])
    
    uploaded_file = None
    with upload_tab:
        uploaded_file = st.file_uploader("Choose a receipt image", type=["jpg", "jpeg", "png", "webp"])
        
    with camera_tab:
        camera_file = st.camera_input("Take a photo of receipt")
        if camera_file:
            uploaded_file = camera_file

    if uploaded_file:
        img = Image.open(uploaded_file)
        st.session_state.receipt_image = img
        st.image(img, caption="Uploaded Receipt", use_container_width=True)
        
        if st.button("✨ Analyze Receipt with Gemini Vision", type="primary", use_container_width=True):
            if not gemini_api_key:
                st.error("⚠️ Please enter your Gemini API Key in the left sidebar first!")
            else:
                with st.spinner("Analyzing receipt with Gemini Vision..."):
                    try:
                        raw_text, json_data = analyze_receipt(gemini_api_key, img)
                        st.session_state.analysis_raw = raw_text
                        st.session_state.parsed_data = json_data
                        st.success("Receipt analyzed successfully!")
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")

with col_right:
    st.subheader("📊 Step 2: Bill Splitter & Itemization")
    
    if st.session_state.parsed_data or st.session_state.analysis_raw:
        data = st.session_state.parsed_data or {}
        
        merchant = data.get("merchant", "Receipt")
        total_amount = float(data.get("total", 0.0))
        currency = data.get("currency", "$")
        subtotal = float(data.get("subtotal", total_amount))
        tax = float(data.get("tax", 0.0))
        tip = float(data.get("tip", 0.0))
        
        st.markdown(f"""
        <div class="card">
            <h4>🏪 {merchant}</h4>
            <p><strong>Subtotal:</strong> {currency}{subtotal:.2f} | <strong>Tax:</strong> {currency}{tax:.2f} | <strong>Tip:</strong> {currency}{tip:.2f}</p>
            <h3 style="color:#2e7d32; margin:0;">Grand Total: {currency}{total_amount:.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Split Settings
        st.write("##### 👥 People & Split Settings")
        split_mode = st.radio("Split Method", ["Equal Split ⚖️", "Custom Names 🏷️"], horizontal=True)
        
        if split_mode == "Equal Split ⚖️":
            num_people = st.number_input("Number of People", min_value=1, max_value=20, value=2)
            per_person = total_amount / num_people if num_people > 0 else 0
            st.metric("Amount Per Person", f"{currency}{per_person:.2f}")
            split_summary_text = f"Equal split among {num_people} people: {currency}{per_person:.2f} each."
            people_names_str = f"{num_people} people"
        else:
            names_input = st.text_input("Enter names separated by commas", value="Alice, Bob, Charlie")
            names = [n.strip() for n in names_input.split(",") if n.strip()]
            st.session_state.people_list = names
            num_people = len(names)
            per_person = total_amount / num_people if num_people > 0 else 0
            
            st.write("##### Individual Share:")
            for name in names:
                st.write(f"- **{name}**: {currency}{per_person:.2f}")
            split_summary_text = f"Split among {', '.join(names)} ({currency}{per_person:.2f} each)."
            people_names_str = ", ".join(names)

        # Line Items Table if available
        items = data.get("items", [])
        if items:
            with st.expander("📋 View Extracted Line Items"):
                df_items = pd.DataFrame(items)
                st.dataframe(df_items, use_container_width=True)

        st.markdown("---")
        st.subheader("📤 Step 3: Send Action Digest")
        
        # Generate proposed summary text
        proposed_digest = f"""🧾 *SnapSplit Bill Summary*
*Merchant:* {merchant}
*Grand Total:* {currency}{total_amount:.2f}

*Split Details ({split_mode}):*
{split_summary_text}

📌 *Payment Note:* Please send your share via your preferred payment app. Thank you!"""

        digest_text = st.text_area("Preview / Edit Digest Message:", value=proposed_digest, height=140)
        
        if st.button(f"🚀 Send Summary via {action_channel}", type="primary", use_container_width=True):
            if action_channel == "📧 Email (Gmail)":
                if not recipient_email or not gmail_address or not gmail_app_password:
                    st.warning("⚠️ Credentials incomplete. Showing simulated send mode:")
                    st.info(f"💌 [SIMULATED EMAIL SENT TO {recipient_email or 'user@example.com'}]\n\nSubject: Bill Split for {merchant}\n\n{digest_text}")
                else:
                    with st.spinner("Sending email via Gmail SMTP..."):
                        success, msg = send_email(
                            to_address=recipient_email,
                            subject=f"🧾 Bill Split Summary: {merchant}",
                            body=digest_text,
                            gmail_address=gmail_address,
                            gmail_app_password=gmail_app_password
                        )
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                            
            elif action_channel == "💬 Telegram":
                if not telegram_chat_id or not telegram_bot_token:
                    st.warning("⚠️ Credentials incomplete. Showing simulated send mode:")
                    st.info(f"💬 [SIMULATED TELEGRAM SENT TO CHAT ID {telegram_chat_id or '12345678'}]\n\n{digest_text}")
                else:
                    with st.spinner("Sending message via Telegram Bot..."):
                        success, msg = send_telegram(
                            chat_id=telegram_chat_id,
                            text=digest_text,
                            bot_token=telegram_bot_token
                        )
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                            
            elif action_channel == "📱 WhatsApp":
                if not whatsapp_number or not twilio_sid or not twilio_token:
                    st.warning("⚠️ Credentials incomplete. Showing simulated send mode:")
                    st.info(f"📱 [SIMULATED WHATSAPP SENT TO {whatsapp_number or '+14155238886'}]\n\n{digest_text}")
                else:
                    with st.spinner("Sending WhatsApp message via Twilio..."):
                        success, msg = send_whatsapp(
                            to_number=whatsapp_number,
                            text=digest_text,
                            twilio_sid=twilio_sid,
                            twilio_token=twilio_token,
                            twilio_from=twilio_from
                        )
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
    else:
        st.info("👈 Upload a receipt photo on the left and click **Analyze Receipt with Gemini Vision** to get started!")

# --- Interactive Gemini Chat Section ---
st.markdown("---")
st.subheader("💬 Snap & Ask Gemini About Your Receipt")

if st.session_state.receipt_image is None:
    st.caption("Upload a receipt above to unlock interactive Q&A with Gemini Vision!")
else:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_question = st.chat_input("Ask a question about this receipt (e.g. 'How much was the tip?', 'What drinks were ordered?')")
    if user_question:
        if not gemini_api_key:
            st.error("Please enter your Gemini API Key in the left sidebar.")
        else:
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)
                
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        answer = chat_about_receipt(
                            api_key=gemini_api_key,
                            image=st.session_state.receipt_image,
                            chat_history=st.session_state.chat_history[:-1],
                            new_question=user_question
                        )
                        st.markdown(answer)
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    except Exception as err:
                        st.error(f"Chat error: {str(err)}")
