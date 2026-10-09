# 🧾 SnapSplit - Receipt & Bill Splitter AI

SnapSplit is a Gemini-powered vision assistant and bill splitter built with Streamlit. Snap a photo of any receipt, extract itemized costs, split the bill evenly or by custom names, and send the summary directly to Email (Gmail SMTP), Telegram Bot, or WhatsApp with a single click.

---

## 🌟 Key Features

1. **Gemini Vision Receipt OCR & Itemization**: Extract merchant name, subtotal, tax, tip, itemized list, and grand total automatically from messy real-world photos.
2. **Flexible Bill Splitting**: Split totals equally or assign shares across custom person names.
3. **Interactive Gemini Chat**: Ask follow-up questions directly about the receipt ("How much was tax?", "Who ordered drinks?").
4. **Multi-Channel Action Tool**:
   - **Gmail SMTP (Free, Option B)**: Uses Python's built-in `smtplib`.
   - **Telegram Bot (Free, Option C)**: Send digests instantly to any Telegram `chat_id`.
   - **WhatsApp via Twilio (Option A)**: Dispatch formatted messages directly to WhatsApp numbers.
   - **Simulated Send Mode**: Test the app immediately even without API credentials.

---

## 🚀 Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Streamlit App:
   ```bash
   streamlit run app.py
   ```

3. Open your browser at `http://localhost:8501`.

---

## 📁 Project Structure

- `app.py`: Streamlit main user interface and workflow orchestration.
- `prompts.py`: System prompt and digest output templates for Gemini Vision.
- `ai_service.py`: Multi-SDK Gemini Vision API integration and chat handler.
- `send_action.py`: Action dispatcher supporting Gmail SMTP, Telegram Bot API, and Twilio WhatsApp.
- `requirements.txt`: Python package dependencies.
