from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import callback_data

review_or_continue_kb = ReplyKeyboardMarkup(resize_keyboard=True)
review_or_continue_kb.add(KeyboardButton('Reply'))
review_or_continue_kb.add(KeyboardButton('Continue checking'))

class_kb = ReplyKeyboardMarkup(resize_keyboard=True)
class_kb.add(KeyboardButton('Spam'))
class_kb.add(KeyboardButton('Fraud'))
class_kb.add(KeyboardButton('Threats'))
class_kb.add(KeyboardButton('Advertisement'))
class_kb.add(KeyboardButton('Other'))

call_back = callback_data.CallbackData("rew", "edit_or_del", "numb")