import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

with open("prompt.txt", "r") as f:
    CUSTOM_PROMPT = f.read()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

async def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    """Обработчик команды /start."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Ну привет, я Иван Иван. Поболтаем?")

async def respond(update: telegram.Update, context: telegram.ext.CallbackContext):
    """Генерирует ответ с помощью Google AI Gemini Pro, используя промпт."""
    user_message = update.message.text
    prompt = f"{CUSTOM_PROMPT}\n\nПользователь: {user_message}\nБадди:"
    print(f"Received message in chat {update.effective_chat.id}: {prompt}")
    try:
        response = model.generate_content(prompt)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response.text)
    except Exception as e:
        print(f"An error occurred: {e}")
        if hasattr(e, 'message'):
            error_message = e.message
        else:
            error_message = str(e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Произошла ошибка: {error_message}")

def main():
    """Основная функция бота."""
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (filters.ChatType.GROUPS | filters.ChatType.SUPERGROUP | filters.ChatType.PRIVATE), respond))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
