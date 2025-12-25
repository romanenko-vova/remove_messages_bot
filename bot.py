import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.chat.type == 'private':
        info_text = (
            "👋 Привет!\n\n"
            "Этот бот создан для того, чтобы чистить сообщения в чате о том, что кто-то присоединился и вышел из чата.\n\n"
            "Он абсолютно бесплатный. Ничего от вас не требует.\n\n"
            "📋 Как использовать:\n"
            "1. Добавьте бота в администраторы вашей группы\n"
            "2. Дайте ему права на удаление сообщений\n"
            "3. Готово! Бот автоматически будет удалять сообщения о входе/выходе пользователей"
        )
        await update.message.reply_text(info_text)
        logger.info(f"Отправлено приветственное сообщение пользователю {update.effective_user.id}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.chat:
        return
    
    message = update.message
    
    if message.new_chat_members or message.left_chat_member:
        try:
            await message.delete()
            logger.info(f"Удалено сообщение о входе/выходе в чате {message.chat.id}")
        except Exception as e:
            logger.error(f"Ошибка при удалении сообщения: {e}")
            if "message can't be deleted" in str(e).lower():
                logger.warning("Бот не имеет прав на удаление сообщений в этом чате")


def main() -> None:
    logger.info("Запуск бота...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.ALL, handle_message))
    
    logger.info("Бот запущен и готов к работе!")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == '__main__':
    main()

