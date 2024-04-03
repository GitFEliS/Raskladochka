import asyncio
import logging

from aiogram import Bot, Dispatcher, F
# Дополнительный импорт для раздела про стратегии FSM
# from aiogram.fsm.strategy import FSMStrategy
# from aiogram.types import ContentType
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# файл config_reader.py можно взять из репозитория
# пример — в первой главе
from config_reader import config
from handlers import common, ordering_food
from handlers.ordering_food import cmd_taro, pre_checkout_query, successfull_payment


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Если не указать storage, то по умолчанию всё равно будет MemoryStorage
    # Но явное лучше неявного =]
    dp = Dispatcher(storage=MemoryStorage())
    # Для выбора другой стратегии FSM:
    # dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
    bot = Bot(config.bot_token.get_secret_value())
    dp.message.register(cmd_taro, Command(commands="taro"))
    dp.pre_checkout_query.register(pre_checkout_query)
    dp.message.register(successfull_payment, F.successful_payment)
    dp.include_routers(common.router, ordering_food.router)
    # сюда импортируйте ваш собственный роутер для напитков

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
