import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, ChatMemberHandler, filters, ContextTypes

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('httpx')
logger.setLevel(logging.WARNING)

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.chat.type == 'private':
        bot_username = context.bot.username
        info_text = (
            "👋 Привет!\n\n"
            "Этот бот создан для того, чтобы чистить сообщения в чате о том, что кто-то присоединился, вышел или был исключен из чата.\n\n"
            "Он абсолютно бесплатный. Ничего от вас не требует.\n\n"
            "📋 Как использовать:\n"
            "1. Нажмите кнопку ниже, чтобы добавить бота в группу\n"
            "2. После добавления сделайте бота администратором\n"
            "3. Дайте ему право на удаление сообщений\n"
            "4. Готово! Бот автоматически будет удалять сообщения о входе/выходе/исключении"
        )
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "➕ Добавить в группу",
                    url=f"https://t.me/{bot_username}?startgroup="
                ),
            ]
        ])
        
        await update.message.reply_text(info_text, reply_markup=keyboard)



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.chat:
        return
    
    message = update.message
    
    try:
        await message.delete()
    except Exception:
        pass


async def handle_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.chat_member or not update.message:
        return
    
    chat_member = update.chat_member
    old_status = chat_member.old_chat_member.status
    new_status = chat_member.new_chat_member.status
    
    if old_status != new_status and (new_status == "kicked" or new_status == "left"):
        try:
            await update.message.delete()
        except Exception:
            pass


def main() -> None:
    logger.info("Запуск бота...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS | 
        filters.StatusUpdate.LEFT_CHAT_MEMBER, 
        handle_message
    ))
    application.add_handler(ChatMemberHandler(handle_chat_member, ChatMemberHandler.CHAT_MEMBER))
    
    logger.info("Бот запущен и готов к работе!")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == '__main__':
    main()

