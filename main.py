import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import google.generativeai as genai
from dotenv import load_dotenv
import os
from telegramify_markdown import telegramify

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

with open("prompt.txt", "r") as f:
    CUSTOM_PROMPT = f.read()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

async def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Ну привет, я Иван Иван. Поболтаем?")

async def respond(update: telegram.Update, context: telegram.ext.CallbackContext):
    user_id = update.effective_user.id
    user_message = update.message.text

    history = context.user_data.get(user_id, [])
    history.append({'role': 'user', 'parts': [user_message]})

    messages = [{"role": "model", "parts": [CUSTOM_PROMPT]}]
    messages.extend(history)
    messages.append({"role": "model", "parts": [""]})

    print(f"Received message in chat {update.effective_chat.id} from user {user_id}. Sending history: {messages}")

    try:
        response = model.generate_content(messages)
        response_text = response.text

        formatted_text = await telegramify(response_text)
        response_text_markdown = formatted_text.text

        history.append({'role': 'model', 'parts': [response_text_markdown]})
        context.user_data[user_id] = history

        print(f"Generated response: {response_text_markdown}")
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response_text_markdown,
            parse_mode=telegram.constants.ParseMode.MARKDOWN_V2
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        error_message = str(e)
        if hasattr(e, 'candidates'):
            print(f"Error details: {e.candidates}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Произошла ошибка: {error_message}")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (filters.ChatType.GROUPS | filters.ChatType.SUPERGROUP | filters.ChatType.PRIVATE), respond))
    application.run_polling()

if __name__ == '__main__':
    main()