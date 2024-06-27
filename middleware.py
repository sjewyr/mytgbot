from typing import Any, Awaitable, Callable, Coroutine, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from logger import Logger
from users.user_repo import UserDAO

class LoginMiddleware(BaseMiddleware):
    def __init__(self, typ):
        self.logger = Logger(__class__.__name__).get_logger()
        self.user_dao = UserDAO()
        self.type = typ
        self.logger.info(f"Login middleware initialized: {self.type}")
    @Logger.log_exception
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Coroutine[Any, Any, Any]:
        if not await self.user_dao.check_user(event.from_user.id):
            if self.type=="message":
                await event.answer("Для просмотра этого контента необходимо зарегистрироваться (/start)")
                self.logger.warning(f"User {event.from_user.id} is not registered")
                return
            else:
                await event.message.answer("Для просмотра этого контента необходимо зарегистрироваться (/start)")
                self.logger.warning(f"User {event.from_user.id} is not registered")
                await event.answer()
                return
        result = await handler(event, data)
        return result
        