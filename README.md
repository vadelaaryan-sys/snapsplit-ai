
# 🧾 SnapSplit - Receipt & Bill Splitter AI

SnapSplit is a Gemini-powered vision assistant and bill splitter built with Streamlit. Take a photo of a receipt, extract itemized costs, split the bill evenly or by custom names, and send the summary through Email (Gmail SMTP), Telegram Bot, or WhatsApp.

## 🌟 Key Features

1. **Gemini Vision Receipt OCR & Itemization:** Extract the merchant name, subtotal, tax, tip, itemized list, and grand total from receipt images.
2. **Flexible Bill Splitting:** Split totals equally or assign shares to custom person names.
3. **Interactive Gemini Chat:** Ask follow-up questions about the receipt, such as "How much was tax?"
4. **Multi-Channel Action Tool:**
   - **Gmail SMTP:** Send summaries using Python's built-in `smtplib`.
   - **Telegram Bot:** Send summaries to a Telegram chat.
   - **WhatsApp via Twilio:** Send formatted messages through WhatsApp.
   - **Simulated Send Mode:** Test the app without configuring messaging credentials.

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit app

```bash
streamlit run app.py
```

### 3. Open the app

Visit `http://localhost:8501` in your browser.

## 📁 Project Structure

- `app.py` — Streamlit user interface and workflow.
- `prompts.py` — Prompts and digest templates for Gemini Vision.
- `ai_service.py` — Gemini Vision API integration and chat handler.
- `send_action.py` — Gmail, Telegram, and Twilio WhatsApp messaging.
- `requirements.txt` — Python dependencies.

## 🔐 Configuration

Configure your Gemini API key and any optional messaging credentials using Streamlit secrets or environment variables, as supported by your application code.

**Important:** Never commit API keys, passwords, or other secrets to GitHub.