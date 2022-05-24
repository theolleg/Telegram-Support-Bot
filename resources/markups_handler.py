import config
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def faqButton():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Как использовать бота\'s', callback_data='faqCallbackdata'))
    return markup
