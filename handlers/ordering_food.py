from typing import List

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InputMediaPhoto, Message, ReplyKeyboardRemove, Update, LabeledPrice, PreCheckoutQuery, \
    FSInputFile

from config_reader import config
from gpt import GenerationException, generate_prediction as yandex_prediction
from gpt_gigachat import generate_prediction as sber_prediction
from keyboards.simple_row import make_row_keyboard
from random_choice import tarot_deck

router = Router()

q_types = ["Да", "Задать вопрос заново", "Выбрать таролога"]
q_types_correct = ["Да"]
q_types_again = ["Задать вопрос заново"]
q_types_taro = ["Выбрать таролога"]

generator_types = ["Желтая жрица таро", "Зеленая ведьма"]


class TaroQuestion(StatesGroup):
    payment = State()
    ask_question = State()
    confirm_qustion = State()
    chose_generator = State()


cool_dict = {}


async def cmd_taro(message: Message, bot: Bot, state: FSMContext):
    await message.answer(
        text="Оплатите 300 рублей и сможете задать вопрос AI гадалке.",
    )
    chat_id = message.chat.id
    title = "Оплата расклада таро"
    description = "Оплата позволит вам обратиться к древней жрице"
    payload = "Custom-Payload"
    currency = "rub"
    price = 30000
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


async def pre_checkout_query(pre_checkout: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)


async def successfull_payment(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Оплата прошла успешно. Напиши свой вопрос в чат. \n Гадалка по умолчанию: Потерянная жрица")
    await state.set_state(TaroQuestion.ask_question)


@router.message(TaroQuestion.ask_question)
async def ask_question(message: Message, state: FSMContext):
    cool_dict[message.chat.id] = message.text
    await message.answer(f"Вопрос который задаем гадалке - '{message.text}' Все верно?",
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
    user_message = cool_dict.get(message.chat.id, 'Сообщение не найдено.')
    print(user_message)
    cards = tarot_deck.random_choice(3)
    card_names = [str(card) for card in cards]
    cards_img = list(map(lambda x: x.img_path, cards))
    generator = cool_dict.get(message.chat.username, None)

    match generator:
        case None:
            await message.answer(f"Отправляю вопрос потерянной жрице", reply_markup=ReplyKeyboardRemove())
            try:
                result = await yandex_prediction(user_message, card_names)
            except GenerationException:
                await message.answer("Жрица посчитала данный вопрос неуместным и отказалась отвечать на него. Деньги не будут возвращены")
                await state.clear()
                return
        case "Желтая жрица таро":
            await message.answer(f"Отправляю вопрос желтой жрице", reply_markup=ReplyKeyboardRemove())
            try:
                result = await yandex_prediction(user_message, card_names)
            except GenerationException:
                await message.answer("Жрица посчитала данный вопрос неуместным и отказалась отвечать на него. Деньги не будут возвращены")
                await state.clear()
                return
        case "Зеленая ведьма":
            await message.answer(f"Отправляю вопрос зеленой ведьме", reply_markup=ReplyKeyboardRemove())
            result = await sber_prediction(user_message, card_names)

        case _:
            await message.answer(f"Отправляю вопрос стандартной гадалке" , reply_markup=ReplyKeyboardRemove())
            result = await sber_prediction(user_message, card_names)

    await send_photos(message, bot, cards_img)
    try:
        await bot.send_message(message.chat.id, result, parse_mode="Markdown")
    except TelegramBadRequest:
        await bot.send_message(message.chat.id, result)
    await state.clear()


@router.message(TaroQuestion.confirm_qustion, F.text.in_(q_types_again))
async def ask_question(message: Message, state: FSMContext):
    print(message.text)
    await message.answer(f"Напиши свой новый вопрос", parse_mode="Markdown"
                         )
    await state.set_state(TaroQuestion.ask_question)


@router.message(TaroQuestion.confirm_qustion, F.text.in_(q_types_taro))
async def chose_generator(message: Message, state: FSMContext):
    print(message.text)
    await message.answer(f"Выбери своего таролога", reply_markup=make_row_keyboard(generator_types)
                         )
    await state.set_state(TaroQuestion.chose_generator)


@router.message(TaroQuestion.chose_generator, F.text.in_(generator_types))
async def chose_generator(message: Message, state: FSMContext):
    print(message.text)
    cool_dict[message.chat.username] = message.text
    print(cool_dict)

    await message.answer(f"Подтверждаем выбор. Вопрос который задаем гадалке -  {cool_dict[message.chat.id]}. Все верно?",
                         reply_markup=make_row_keyboard(q_types)
                         )
    await state.set_state(TaroQuestion.confirm_qustion)
