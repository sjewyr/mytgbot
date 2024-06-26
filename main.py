import asyncio
import signal
from buildings.buildings_repo import BuildingDAO
from settings import Settings
from aiogram import F, Dispatcher, Bot, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from logger import Logger
from users.user_repo import UserDAO
from aiogram.utils.keyboard import KeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardMarkup, ButtonType



class Game:
    def __init__(self, dp: Dispatcher):
        self.user_dao = UserDAO()
        self.building_dao = BuildingDAO()
        self.logger = Logger(__class__.__name__).get_logger()
        self.dp = dp
        self.register_handlers()
        asyncio.create_task(self.currency_ticking())
    def register_handlers(self):
        self.dp.message.register(self.start, CommandStart())
        self.dp.message.register(self.balance, F.text.lower() == "баланс")
        
        self.dp.callback_query.register(self.buildings_list, F.data == "buildings_list")
        self.dp.callback_query.register(self.buy_building, F.data.startswith("buy_"))

    @Logger.log_exception
    async def start(self, message: types.message.Message):
        self.logger.info(f"Starting user {message.from_user.id}...")
        telegram_id = message.from_user.id
        exists = await self.user_dao.check_user(telegram_id)
        keyboard = InlineKeyboardBuilder()
        keyboard.add(types.InlineKeyboardButton(text="Список зданий", callback_data="buildings_list"))
        if exists:
            await message.answer("Вы уже зарегистрированы", reply_markup=keyboard.as_markup())
            self.logger.info(f"User {message.from_user.id} already exists")
            return
        
        await self.user_dao.register_user(telegram_id)
        await message.answer(
            "Привет! Я бот, для игры в simplegame (Название придумаю потом)", reply_markup=keyboard.as_markup()
        )
        self.logger.info(f"User {message.from_user.id} registered")
        
    @Logger.log_exception
    async def buildings_list(self, callback: types.CallbackQuery):
        buildings = await self.building_dao.list_buildings()
        for building in buildings:
            keyboard = InlineKeyboardBuilder()
            keyboard.add(types.InlineKeyboardButton(text=str("Купить"), callback_data=f"buy_{str(building.id)}"))
            await callback.message.answer(str(building.get_info()), reply_markup=keyboard.as_markup())
    
    @Logger.log_exception
    async def buy_building(self, callback: types.CallbackQuery):
        building_id = int(callback.data.split("_")[1])
        if not building_id:
            self.logger.warning("Unrecognizable data in buy building")
        telegram_id = callback.from_user.id
        if await self.user_dao.buy_building(telegram_id, building_id):
            await callback.message.answer(f"Вы купили здание {building_id}")
            self.logger.info(f"User {callback.from_user.id} bought building {building_id}")
        else:
            await callback.message.answer(f"Вы не можете купить здание {building_id}")
            

    @Logger.log_exception
    async def balance(self, message: types.Message):
        user_id = message.from_user.user_id()
        balance = await self.user_dao.get_balance(user_id)
        await message.answer(f"Ваш баланс: {balance}")

    @Logger.log_exception
    async def currency_ticking(self):
        while True:
            await self.user_dao.currency_tick()
            await asyncio.sleep(Settings.currency_tick_interval)


        


async def main():
    dp = Dispatcher()
    game = Game(dp)
    bot = Bot(token=Settings.token, default=DefaultBotProperties())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logger = Logger("Main").get_logger()
    logger.info("Starting bot")
    asyncio.run(main())
