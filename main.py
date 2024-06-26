import asyncio
import signal
from settings import Settings
from aiogram import Dispatcher, Bot, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from logger import Logger
from users.user_repo import UserDAO
from aiogram.utils.keyboard import KeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardMarkup, ButtonType



class Game:
    def __init__(self, dp: Dispatcher):
        self.user_dao = UserDAO()
        self.logger = Logger(__class__.__name__).get_logger()
        self.dp = dp
        self.register_handlers()
    def register_handlers(self):
        self.dp.message.register(self.start, CommandStart())
    @Logger.log_exception
    async def start(self, message: types.message.Message):
        self.logger.info(f"Starting user {message.from_user.id}...")
        telegram_id = message.from_user.id
        exists = await self.user_dao.check_user(telegram_id)
        keyboard = InlineKeyboardBuilder()
        keyboard.add(types.InlineKeyboardButton(text="Начать игру", callback_data="start"))
        if exists:
            await message.answer("Вы уже зарегистрированы", reply_markup=keyboard.as_markup())
            self.logger.info(f"User {message.from_user.id} already exists")
            return
        
        await self.user_dao.register_user(telegram_id)
        await message.answer(
            "Привет! Я бот, для игры в simplegame (Название придумаю потом)", reply_markup=keyboard.as_markup()
        )
        self.logger.info(f"User {message.from_user.id} registered")
        


async def main():
    dp = Dispatcher()
    game = Game(dp)
    bot = Bot(token=Settings.token, default=DefaultBotProperties())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logger = Logger("Main").get_logger()
    logger.info("Starting bot")
    asyncio.run(main())
