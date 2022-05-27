import config
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton


card = "Карты"
ticket = "Талоны"


def faqButton():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Как использовать бота\'s', callback_data='faqCallbackdata'))
    return markup


def registerTypeKeyboard():
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton(card))
    markup.add(KeyboardButton(ticket))
    return markup