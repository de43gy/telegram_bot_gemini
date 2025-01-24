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
    """Генерирует ответ с помощью Google AI Gemini Pro, используя историю диалога."""
    user_id = update.effective_user.id
    user_message = update.message.text

    # Получаем историю из context.user_data или создаем новую
    history = context.user_data.get(user_id, [])

    # Добавляем текущее сообщение пользователя в историю в формате Gemini API
    history.append({'role': 'user', 'parts': [user_message]})

    # Ограничиваем длину истории, если нужно (модель сама обрежет старые сообщения, если лимит будет превышен)
    # history = history[-MAX_HISTORY_LENGTH:]

    # Формируем запрос к модели с историей
    messages = [{"role": "model", "parts": [CUSTOM_PROMPT]}]
    messages.extend(history)
    messages.append({"role": "model", "parts": [""]})  # Пустое сообщение от модели для обозначения конца промпта

    print(f"Received message in chat {update.effective_chat.id} from user {user_id}. Sending history: {messages}")

    try:
        response = model.generate_content(messages)
        response_text = response.text

        # Добавляем ответ модели в историю
        history.append({'role': 'model', 'parts': [response_text]})

        # Обновляем историю в context.user_data
        context.user_data[user_id] = history

        print(f"Generated response: {response_text}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

    except Exception as e:
        print(f"An error occurred: {e}")
        error_message = str(e)
        if hasattr(e, 'candidates'):
            print(f"Error details: {e.candidates}")
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
