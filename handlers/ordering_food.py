from typing import List

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InputMediaPhoto, Message, ReplyKeyboardRemove, Update, LabeledPrice, PreCheckoutQuery, \
    FSInputFile

from config_reader import config
from gpt import generate_prediction
from keyboards.simple_row import make_row_keyboard
from random_choice import random_choice

router = Router()

q_types = ["Да", "Задать вопрос заново"]
q_types_correct = ["Да"]
q_types_again = ["Задать вопрос заново"]


class TaroQuestion(StatesGroup):
    payment = State()
    ask_question = State()
    confirm_qustion = State()


cool_dict = {}


async def cmd_taro(message: Message, bot: Bot, state: FSMContext):
    await message.answer(
        text="Оплатите 300 рублей и сможете задать вопрос AI гадалке.",
    )
    chat_id = message.chat.id
    title = "Оплата расклада таро"
    description = "Оплата на за 1 вопрос"
    # select a payload just for you to recognize its the donation from your bot
    payload = "Custom-Payload"
    currency = "rub"
    # price in dollars
    price = 30000
    # price * 100 so as to include 2 decimal points
    prices = [LabeledPrice(label="Оплата", amount=price)]

    await bot.send_invoice(

        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token=config.payment_token,
        currency=currency,
        prices=prices,

    )
    # await state.set_state(OrderFood.payment)


async def pre_checkout_query(pre_checkout: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)


async def successfull_payment(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Оплата прошла успешно. Напиши свой вопрос в чат")
    await state.set_state(TaroQuestion.ask_question)
    # await bot.send_message(message.chat.id, "Your payment has been successfully transferred")


@router.message(TaroQuestion.ask_question)
async def ask_question(message: Message, state: FSMContext):
    print(message.text)
    cool_dict[message.chat.id] = message.text
    # await state.update_data(user_message=message.text)
    # print(state.storage)
    await message.answer(f"Повторю вопрос: {message.text}. Все верно?",
                         reply_markup=make_row_keyboard(q_types)
                         )
    await state.set_state(TaroQuestion.confirm_qustion)


async def send_photos(message: Message, bot: Bot, cards: List[str]):
    folder_path = './cards'
    media_group = []
    for image in cards:
        media_group.append(InputMediaPhoto(media=FSInputFile(folder_path + '/' + image)))
    await bot.send_media_group(message.chat.id, media=media_group)


@router.message(TaroQuestion.confirm_qustion, F.text.in_(q_types_correct))
async def ask_question(message: Message, state: FSMContext, bot: Bot):
    print(message.text)
    await message.answer(f"Отправляю вопрос гадалке")
    user_message = cool_dict.get(message.chat.id, 'Сообщение не найдено.')
    print(user_message)
    cards_names, cards_img = random_choice()
    result = await generate_prediction(user_message, cards_names)
    await send_photos(message, bot, cards_img)

    await bot.send_message(message.chat.id, result, parse_mode="Markdown")
    await state.clear()


@router.message(TaroQuestion.confirm_qustion, F.text.in_(q_types_again))
async def ask_question(message: Message, state: FSMContext):
    print(message.text)
    await message.answer(f"Напиши свой новый вопрос", parse_mode="Markdown"
                         )
    await state.set_state(TaroQuestion.ask_question)
