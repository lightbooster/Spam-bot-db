import logging, phonenumbers

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import TOKEN

import keyboard as kb

import message_generator as mg

from bot_sql_api import SpamDB

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)

dp = Dispatcher(bot, storage=MemoryStorage())

bd = SpamDB(auto_save=True)

@dp.message_handler(commands=["help"])
async def start(massage: types.Message):
    await massage.answer('This bot is a database with "bad" numbers. Enter /start to start or /reviews to check your reviews.')

@dp.message_handler(commands=["start"])
async def start(massage: types.Message):
    await bot.send_photo(massage.chat.id, open("img/spamy.png", "rb"))
    await massage.answer(mg.create_hi_string()[0])
    await massage.answer(mg.create_hi_string()[1])

@dp.message_handler(commands=["reviews"])
async def reviews(massage: types.Message):
    reviews = bd.find_personal_reviews(types.User.get_current().id)
    if reviews == -1:
        await massage.answer("You have no reviews.")
    else:
        for rv in range(len(reviews)):
            dell_or_edit_inkd = InlineKeyboardMarkup()
            dell_or_edit_inkd.add(InlineKeyboardButton("Delete", callback_data=kb.call_back.new(edit_or_del = "del",
                                                                                                numb = reviews[rv][3])),
                                  InlineKeyboardButton("Edit", callback_data=kb.call_back.new(edit_or_del="edit",
                                                                                              numb=reviews[rv][3])))
            await massage.answer(str(reviews[rv][0]) + " " + str(reviews[rv][1]) + " " + str(reviews[rv][2]), reply_markup=dell_or_edit_inkd)

@dp.callback_query_handler()
async def callback(callback_query: types.CallbackQuery):
    data = str(callback_query.data).split(sep=":")
    if data[0] == "rew":
        if data[1] == "del":
            await callback_query.answer("This review deleted.")
            await callback_query.message.answer("This review deleted.")
            bd.delete_review(int(data[2]))
            bd.save()
        if data[1] == "edit":
            await callback_query.answer("Please enter new comment.")
            await callback_query.message.answer(mg.create_need_comment_string())
            state = dp.current_state(chat=types.Chat.get_current().id, user=types.User.get_current().id)
            await state.update_data(rew_id = int(data[2]))
            await state.set_state("Edit")

@dp.message_handler(state="Edit")
async def Edit(massage: types.Message):
    state = dp.current_state(chat=types.Chat.get_current().id, user=types.User.get_current().id)
    data = await state.get_data()
    bd.update_review((data["rew_id"], massage.text))
    bd.save()
    await massage.answer(mg.create_thank_update_string())
    await state.set_state(None)


@dp.message_handler(state="Comment")
async def Comment(massage: types.Message):
    state = dp.current_state(chat=types.Chat.get_current().id, user=types.User.get_current().id)
    data = await state.get_data()
    bd.insert_review((data["number"], data["bad_class"], massage.text, types.User.get_current().id))
    bd.save()
    await massage.answer(mg.create_thank_reply_string())
    await state.set_state(None)

@dp.message_handler(state="Review")
async def Review(massage: types.Message):
    bad_class = -1
    if massage.text == "Spam":
        bad_class = 0
    elif massage.text == "Fraud":
        bad_class = 1
    elif massage.text == "Threats":
        bad_class = 3
    elif massage.text == "Advertisement":
        bad_class = 4
    else:
        bad_class = 5 # other
    await massage.answer(mg.create_need_comment_string(), reply_markup=types.ReplyKeyboardRemove())
    state = dp.current_state(chat=types.Chat.get_current().id, user=types.User.get_current().id)
    await state.set_state("Comment")
    await state.update_data(bad_class=bad_class)

@dp.message_handler(state="Number")
async def Number(massage: types.Message):
    if massage.text == "Reply":
        await massage.answer(mg.create_choose_class_string(), reply_markup=kb.class_kb)
        state = dp.current_state(chat=types.Chat.get_current().id, user=types.User.get_current().id)
        await state.set_state("Review")
    elif massage.text == "Continue checking":
        await massage.answer("Ok", reply_markup=types.ReplyKeyboardRemove())
        state = dp.current_state(chat=types.Chat.get_current().id, user=types.User.get_current().id)
        await state.set_state(None)

@dp.message_handler()
async def work(massage: types.Message):
    try:
        number = phonenumbers.parse(massage.text)
        data = bd.find_phone(str(number.country_code) + str(number.national_number))
        if data != -1:
            bd_data = bd.find_reviews(data[0])
            await bot.send_photo(massage.chat.id, open("img/spamy_attention.png", "rb"))
            await massage.answer(mg.create_attention_message("+" + data[1], data[3], (set(map(lambda x: x[0], bd_data))),
                                                             data[2],
                                                             bd_data)
                                                            , reply_markup=kb.review_or_continue_kb)
        else:
            await bot.send_photo(massage.chat.id, open("img/spamy_ok.png", "rb"))
            await massage.answer(mg.create_ok_message("+" + str(number.country_code) + str(number.national_number)),
                                 reply_markup=kb.review_or_continue_kb)
        state = dp.current_state(chat=types.Chat.get_current().id, user=types.User.get_current().id)
        await state.set_state("Number")
        await state.update_data(number=str(number.country_code) + str(number.national_number))
    except:
        await massage.answer("Invalid number")


def main():
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    main()
