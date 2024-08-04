import asyncio

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from buildings.buildings_repo import BuildingDAO
from celery_tasks import await_check_init, start_user_task
from database import ConnectionManager
from logger import Logger
from middleware import LoginMiddleware
from settings import Settings
from task_manager import TaskManager
from tasks.tasks_repo import TaskStatus, UserTaskDAO
from users.level_rewards import REWARD_DICT
from users.user_repo import UserDAO


class MyBasicKeyboard:
    def __init__(self) -> None:
        self.keyboard = ReplyKeyboardBuilder()
        self.keyboard.add(types.KeyboardButton(text="Список зданий"))
        self.keyboard.add(types.KeyboardButton(text="Статус"))
        self.keyboard.add(types.KeyboardButton(text="Обновить"))
        self.keyboard.add(types.KeyboardButton(text="Престиж"))
        self.keyboard.add(types.KeyboardButton(text="Задачи"))
        self.keyboard.adjust(2, 3)

    def get_keyboard(self):
        res = self.keyboard.as_markup()
        res.resize_keyboard = True
        return res


class Game:
    def __init__(self, dp: Dispatcher):
        self.user_dao = UserDAO()
        self.building_dao = BuildingDAO()
        self.user_task_dao = UserTaskDAO()
        self.task_manager = TaskManager()
        self.logger = Logger(__class__.__name__).get_logger()  # type: ignore[name-defined]
        self.dp = dp
        self.register_handlers()
        asyncio.create_task(self.currency_ticking())

    def register_handlers(self):
        """
        Method to register handlers
        """

        start_router = Router(name="start")
        start_router.message.register(self.start, CommandStart())
        logged_router = Router(name="main")
        logged_router.message.middleware(LoginMiddleware("message"))
        logged_router.callback_query.middleware(LoginMiddleware("callback"))
        logged_router.message.register(self.balance, F.text.lower() == "статус")
        logged_router.message.register(self.update, F.text.lower() == "обновить")
        logged_router.message.register(self.prestige_show, F.text.lower() == "престиж")
        logged_router.message.register(self.tasks_list, F.text.lower() == "задачи")
        logged_router.message.register(
            self.message_buildings_list, F.text.lower() == "список зданий"
        )
        logged_router.callback_query.register(
            self.buildings_list, F.data == "buildings_list"
        )
        logged_router.callback_query.register(
            self.buy_building, F.data.startswith("buy_")
        )
        logged_router.callback_query.register(
            self.start_task, F.data.startswith("task_")
        )
        logged_router.callback_query.register(self.prestige_buy, F.data == "prestige")
        self.dp.include_router(start_router)
        self.dp.include_router(logged_router)

    @Logger.log_exception
    async def start_task(self, callback: types.CallbackQuery):
        task_id = int(callback.data.split("_")[1])
        task = await self.user_task_dao.get_task(callback.from_user.id, task_id)
        can_afford = await self.user_task_dao.can_afford(callback.from_user.id, task_id)
        if can_afford == TaskStatus.NOT_ENOUGH_MONEY:
            await callback.message.answer("У вас недостаточно денег.")
            await callback.answer()
            return
        if can_afford == TaskStatus.INSUFFICIENT_LEVEL:
            await callback.message.answer("Ваш уровень слишком низкий.")
            await callback.answer()
            return
        if can_afford == TaskStatus.ALREADY_EXECUTED:
            active_task_id = await self.user_task_dao.get_active_user_task(
                callback.from_user.id
            )
            active_task = await self.user_task_dao.get_task(
                callback.from_user.id, active_task_id
            )
            await callback.message.answer(
                f"Вы уже выполняете задачу: {active_task.name}"
            )
            await callback.answer()
            return
        await self.user_dao.update_currency(callback.from_user.id, task.cost * (-1))
        await self.user_task_dao.start_task(callback.from_user.id, task_id)
        self.task_manager.apply_with_delay(
            start_user_task,
            delay=task.length * Settings.currency_tick_interval,
            args=(callback.from_user.id, task_id),
            callback=self.callback_for_completed_user_tasks,
            args_for_callback=(callback.from_user.id, task_id, callback),
        )
        self.logger.info(f"Task {task_id} started for user {callback.from_user.id}")
        await callback.message.answer("Задача началась")
        await callback.answer()

    async def callback_for_completed_user_tasks(
        self, res, telegram_id, task_id, callback: types.CallbackQuery
    ):
        await callback.message.answer("Задача выполнена")
        if res:
            await callback.message.answer(
                f"Уровень повышен! Ваша награда: {REWARD_DICT.get(res).to_user()}"
            )
        self.logger.info(f"Task {task_id} completed for user {telegram_id}")

    @Logger.log_exception
    async def tasks_list(self, message: types.Message):
        tasks = await self.user_task_dao.get_tasks(message.from_user.id)
        for task in tasks:
            kb = InlineKeyboardBuilder()
            kb.add(
                types.InlineKeyboardButton(
                    text="Выполнить", callback_data=f"task_{task.id}"
                )
            )
            await message.answer(task.get_info(), reply_markup=kb.as_markup())
        active_task_id = await self.user_task_dao.get_active_user_task(
            message.from_user.id
        )
        if active_task_id:
            active_task = await self.user_task_dao.get_task(
                message.from_user.id, active_task_id
            )
            await message.answer(f"Текущая задача: {active_task.name}")

    @Logger.log_exception
    async def prestige_buy(self, callback: types.CallbackQuery):
        prestige = await self.user_dao.get_prestige(callback.from_user.id)
        cur = await self.user_dao.get_currency(callback.from_user.id)
        if cur < Settings.prestige_formula(prestige):
            await callback.message.answer(
                "У вас недостаточно денег для покупки престижа."
            )
            await callback.answer()
            return
        await self.user_dao.prestige_up(callback.from_user.id)
        await callback.message.answer("Престиж получен")
        await callback.answer()

    @Logger.log_exception
    async def prestige_show(self, message: types.Message):
        prestige = await self.user_dao.get_prestige(message.from_user.id)
        await message.answer(f"Ваш престиж: {prestige}")
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            types.InlineKeyboardButton(text="Престиж", callback_data="prestige")
        )
        await message.answer(
            f"Цена престижа: {Settings.prestige_formula(prestige)}",
            reply_markup=keyboard.as_markup(),
        )

    @Logger.log_exception
    async def update(self, message: types.Message):
        await message.answer(
            "Обновление клавиатуры", reply_markup=MyBasicKeyboard().get_keyboard()
        )
        self.logger.info(f"User {message.from_user.id} updated keyboard")

    @Logger.log_exception
    async def message_buildings_list(self, message: types.Message):
        buildings = await self.building_dao.list_buildings(message.from_user.id)
        for building in buildings:
            keyboard = InlineKeyboardBuilder()
            keyboard.add(
                types.InlineKeyboardButton(
                    text=str("Купить"), callback_data=f"buy_{str(building.id)}"
                )
            )
            await message.answer(
                str(building.get_info()), reply_markup=keyboard.as_markup()
            )

    @Logger.log_exception
    async def start(self, message: types.Message):
        """
        User registration method
        """
        self.logger.info(f"Starting user {message.from_user.id}...")
        telegram_id = message.from_user.id
        exists = await self.user_dao.check_user(telegram_id)
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            types.InlineKeyboardButton(
                text="Список зданий", callback_data="buildings_list"
            )
        )
        if exists:
            await message.answer(
                "Вы уже зарегистрированы", reply_markup=MyBasicKeyboard().get_keyboard()
            )
            self.logger.info(f"User {message.from_user.id} already exists")
            return

        await self.user_dao.register_user(telegram_id)
        await message.answer(
            "Привет! Я бот, для игры в simplegame (Название придумаю потом)",
            reply_markup=MyBasicKeyboard().get_keyboard(),
        )
        self.logger.info(f"User {message.from_user.id} registered")

    @Logger.log_exception
    async def buildings_list(self, callback: types.CallbackQuery):
        buildings = await self.building_dao.list_buildings(callback.from_user.id)
        for building in buildings:
            keyboard = InlineKeyboardBuilder()
            keyboard.add(
                types.InlineKeyboardButton(
                    text=str("Купить"), callback_data=f"buy_{str(building.id)}"
                )
            )
            await callback.message.answer(
                str(building.get_info()), reply_markup=keyboard.as_markup()
            )
        await callback.answer()

    @Logger.log_exception
    async def buy_building(self, callback: types.CallbackQuery):
        building_id = int(callback.data.split("_")[1])
        self.logger.info(
            f"User {callback.from_user.id} wants to buy building {building_id}"
        )
        if not building_id:
            self.logger.warning("Unrecognizable data in buy building")
        telegram_id = callback.from_user.id
        if await self.user_dao.buy_building(telegram_id, building_id):
            await callback.message.answer(
                f"Вы купили здание {await self.building_dao.get_building_name(building_id)}"
            )
            new_status = await self.user_dao.get_currency_status(telegram_id)
            await callback.message.answer(
                f"Ваш баланс: {new_status[0]}$ + ({new_status[1]}$\мин)"
            )
            self.logger.info(
                f"User {callback.from_user.id} bought building {building_id}"
            )
        else:
            await callback.message.answer(
                f"Вы не можете купить здание {await self.building_dao.get_building_name(building_id)}"
            )

        await callback.answer()

    @Logger.log_exception
    async def balance(self, message: types.Message):
        user_id = message.from_user.id
        balance, income = await self.user_dao.get_currency_status(user_id)
        level, exp, max_exp = await self.user_dao.get_level(user_id)
        await message.answer(f"Ваш баланс: {balance}$ + ({income}$\мин)")
        await message.answer(f"Ваш уровень: {level} [{exp}/{max_exp}]")

    @Logger.log_exception
    async def currency_ticking(self):
        while True:
            await self.user_dao.currency_tick()
            await asyncio.sleep(Settings.currency_tick_interval)


async def main():
    check = await ConnectionManager().check_database()
    if not check:
        logger.fatal("Database is not initialized; Shutting down.")
        return
    logger.info("Database is initialized")
    dp = Dispatcher()
    Game(dp)
    bot = Bot(token=Settings.token, default=DefaultBotProperties())
    logger.info("TaskManager started")
    tasks = TaskManager()
    try:
        task = tasks.apply_with_delay(await_check_init)
        logger.info("Task system initialition checking...")
        assert tasks.wait(task)
    except Exception as e:
        logger.fatal(f"Task system failed to initialize: {e}")
        return

    await dp.start_polling(bot)


if __name__ == "__main__":
    logger = Logger("Main").get_logger()
    logger.info("Starting bot")
    asyncio.run(main())
