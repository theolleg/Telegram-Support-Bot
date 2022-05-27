import config, storage
from resources import mysql_handler as mysql
from resources import markups_handler as markup
from resources import msg_handler as msg

import telebot
from datetime import datetime, timedelta
import arrow

bot = telebot.TeleBot(config.token)

mysql.createTables


# Callback Handlers
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "faqCallbackdata":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=config.text_messages['faqs'], parse_mode='Markdown',
                                        disable_web_page_preview=True)


# Start Command
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':
        
        bot.send_message(message.chat.id,
                         config.text_messages['start'].format(message.from_user.first_name),
                         parse_mode='Markdown',
                         disable_web_page_preview=True,
                         reply_markup=markup.registerTypeKeyboard()
                         )
        mysql.start_bot(message.chat.id)
        bot.register_next_step_handler(message, choose_registration_type)

    else:
        bot.reply_to(message, 'Будь ласка, надішліть мені приватні повідомлення, якщо ви хочете поговорити з командою підтримки.')


def choose_registration_type(message: telebot.types.Message):
    try:
        if message.text not in (markup.card, markup.ticket):
            bot.send_message(message.chat.id, text="Верифікація не пройдена, натисніть /start щоб вибрати тип регестрації", reply_markup=markup.ReplyKeyboardRemove())
            return
        
        if message.text == markup.card:
            bot.send_message(message.chat.id, "Введіть номер вашої карти", reply_markup=markup.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, mtouser)
            return
        if message.text == markup.ticket:
            bot.send_message(message.chat.id, "Введіть ваше ім'я", reply_markup=markup.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, register_name)
            return

    except Exception as e:
        pass


def mtouser(message):
    org = mysql.verif_user(message.text)
    if org is None:
        bot.send_message(message.chat.id, text="Верифікація не пройдена, натисніть /start щоб ввести номер картки знову")
    else:
        mysql.verif_update(message.chat.id, 1, org['organization'], org['card_number'])
        msg = bot.send_message(message.chat.id, text=f"Доброго дня, {org['organization']}, напишіть ваше запитання")

def register_name(message: telebot.types.Message):
    mysql.update_name(message.from_user.id, message.text)
    bot.send_message(message.chat.id, "Введіть ваш номер телефону")
    bot.register_next_step_handler(message, register_telephone)

def register_telephone(message: telebot.types.Message):
    mysql.update_telephone(message.from_user.id, message.text)
    bot.send_message(message.chat.id, text=f"Введіть номер талону")
    bot.register_next_step_handler(message, register_ticket)

def register_ticket(message: telebot.types.Message):
    mysql.update_ticket(message.from_user.id, message.text)
    bot.send_message(message.chat.id, text=f"Доброго дня, напишіть ваше запитання")


# FAQ Command
@bot.message_handler(commands=['faq'])
def start(message):
    if message.chat.type == 'private':
        bot.reply_to(message, config.text_messages['faqs'], parse_mode='Markdown', disable_web_page_preview=True)
    else:
        pass


# Get All Open Tickets
@bot.message_handler(commands=['tickets', 't'])
def ot_handler(message):
    if message.chat.id == config.support_chat:
        if not mysql.open_tickets:
            bot.reply_to(message, "ℹ️  Чудова робота, всі запити оброблені")
            return

        ot_msg = '📨 *Open tickets:*\n\n'
        for user in mysql.open_tickets:
            bot.send_chat_action(message.chat.id, 'typing')
            ot_link = mysql.user_tables(int(user))['open_ticket_link']

            now = arrow.now()
            diff = datetime.now() - mysql.user_tables(int(user))['open_ticket_time']
            diff.total_seconds() / 3600  # seconds to hour
            time_since_secs = float(diff.seconds)
            time_since = now.shift(seconds=-time_since_secs).humanize()

            # Bring attention to 1 day old tickets
            if time_since_secs > config.open_ticket_emoji * 3600:
                alert = ' ↳ ⚠️ '
            else:
                alert = ' ↳ '

            ot_msg += "• [{0}{1}](tg://user?id={2}) (`{2}`)\n{5}_{3}_ [➜ Перейти до повідоблення]({4})\n".format(
                bot.get_chat(int(user)).first_name,
                ' {0}'.format(bot.get_chat(int(user)).last_name) if bot.get_chat(int(user)).last_name else '',
                int(user), time_since, ot_link, alert)

        bot.send_message(message.chat.id, ot_msg, parse_mode='Markdown')
    else:
        pass


# Close a ticket manually #TODO: add stop chat
@bot.message_handler(commands=['close', 'c'])
def ot_handler(message):
    if message.chat.id == config.support_chat:
        if message.reply_to_message and '(#id' in message.reply_to_message.text:
            bot.send_chat_action(message.chat.id, 'typing')
            user_id = int(message.reply_to_message.text.split('(#id')[1].split(')')[0])
            ticket_status = mysql.user_tables(user_id)['open_ticket']

            if ticket_status == 0:
                bot.reply_to(message, '❌ У данного клієнта відсутні відкриті запити...')
            else:
                # Reset Open Tickets as well as the Spamfilter
                mysql.reset_open_ticket(user_id)
                bot.reply_to(message, '✅ Запит закритий')
                storage.stop_link(user_id)
        else:
            bot.reply_to(message, 'ℹ️  Потрібно відповісти на повідомлення')
    else:
        pass


# Get Banned User
@bot.message_handler(commands=['banned'])
def ot_handler(message):
    if message.chat.id == config.support_chat:
        if not mysql.banned:
            bot.reply_to(message, "ℹ️  Заблоковані користувачі відсутні")
            return

        ot_msg = '⛔️ *Заблоковані користувачі:*\n\n'
        for user in mysql.banned:
            bot.send_chat_action(message.chat.id, 'typing')
            ot_link = mysql.user_tables(int(user))['open_ticket_link']

            ot_msg += "• [{0}{1}](tg://user?id={2}) (`{2}`)\n[➜ Перейти до останнього повідомлення]({3})\n".format(
                bot.get_chat(int(user)).first_name,
                ' {0}'.format(bot.get_chat(int(user)).last_name) if bot.get_chat(int(user)).last_name else '',
                int(user), ot_link)

        bot.send_message(message.chat.id, ot_msg, parse_mode='Markdown')
    else:
        pass


# Ban User
@bot.message_handler(commands=['ban'])
def ot_handler(message):
    try:
        if message.chat.id == config.support_chat:
            if message.reply_to_message and '(#id' in msg.msgCheck(message):
                user_id = msg.getUserID(message)
                banned_status = mysql.user_tables(user_id)['banned']

                if banned_status == 1:
                    bot.reply_to(message, '❌ Користувач вже заблокований...')
                else:
                    mysql.ban_user(user_id)
                    try:
                        # Reset Open Tickets as well as the Spamfilter
                        mysql.reset_open_ticket(user_id)
                    except Exception as e:
                        pass
                    bot.reply_to(message, '✅ Користувач був заблокований!')

            elif msg.getReferrer(message.text):
                user_id = int(msg.getReferrer(message.text))
                banned_status = mysql.user_tables(user_id)['banned']

                if banned_status == 1:
                    bot.reply_to(message, '❌ Користувач вже заблокований...')
                else:
                    mysql.ban_user(user_id)
                    try:
                        # Reset Open Tickets as well as the Spamfilter
                        mysql.reset_open_ticket(user_id)
                    except Exception as e:
                        pass
                    bot.reply_to(message, '✅ Користувач був заблокований!')
        else:
            bot.reply_to(message, 'ℹ️ Вам нужно будет либо ответить на сообщение, либо упомянуть `Идентификатор пользователя`.',
                         parse_mode='Markdown')
    except TypeError:
        bot.reply_to(message, '❌ Неизвесный пользователь...')


# Un-ban Useer
@bot.message_handler(commands=['unban'])
def ot_handler(message):
    try:
        if message.chat.id == config.support_chat:
            if message.reply_to_message and '(#id' in msg.msgCheck(message):
                user_id = msg.getUserID(message)
                banned_status = mysql.user_tables(user_id)['banned']

                if banned_status == 0:
                    bot.reply_to(message, '❌ Цей користувач вже заблокований...')
                else:
                    mysql.unban_user(user_id)
                    bot.reply_to(message, '✅ Цей користувач був заблокований')

            elif msg.getReferrer(message.text):
                user_id = int(msg.getReferrer(message.text))
                banned_status = mysql.user_tables(user_id)['banned']

                if banned_status == 0:
                    bot.reply_to(message, '❌ Цей користувач вже заблокований...')
                else:
                    mysql.unban_user(user_id)
                    bot.reply_to(message, '✅ Цей користувач був заблокований!')
            else:
                bot.reply_to(message, 'ℹ️  Вам потрібно або відповісти на повідомлення, або згадати `Ідентифікатор користувача`.',
                             parse_mode='Markdown')
    except TypeError:
        bot.reply_to(message, '❌ Неизвесный пользователь...')


@bot.message_handler(commands=['ban_manager'])
def ban_manager(message: telebot.types.Message):
    try:
        if message.chat.id == config.support_chat:
            hours = int(message.text.split(' ')[1])
            if message.reply_to_message:
                manager_id = message.reply_to_message.from_user.id
                storage.stop_by_manager_id(manager_id)
                bot.restrict_chat_member(config.support_chat, manager_id, until_date=datetime.now() + timedelta(hours=hours), can_send_messages=False)
                bot.reply_to(message, '✅ Цей менеджер був заблокований на {hours} годин!')
            else:
                bot.reply_to(message, '❌ Отметьте пользователя')
    except:
        bot.reply_to(message, '❌ Ошибка віполнения команды')


# Message Forward Handler (User - Support)
@bot.message_handler(func=lambda message: message.chat.type == 'private', content_types=['text', 'photo', 'document'])
def echo_all(message):

    while True:
        mysql.start_bot(message.chat.id)
        user_id = message.chat.id
        message = message
        user_data = mysql.user_tables(user_id)

        banned = user_data['banned']
        verif_check = user_data['verified']
        ticket_status = user_data['open_ticket']
        ticket_spam = user_data['open_ticket_spam']

        if verif_check == 0:
            return
        if banned == 1:
            return
        elif msg.spam_handler_warning(bot, user_id, message):  # First spam warning
            return
        elif msg.bad_words_handler(bot, message):
            return
        elif msg.spam_handler_blocked(bot, user_id, message):  # Final spam warning // user cant send messages anymore
            return
        elif ticket_status == 0:
            mysql.open_ticket(user_id)
            continue
        else:
            msg.fwd_handler(user_id, bot, message, user_data)
            return


# Message Forward Handler (Support - User)
@bot.message_handler(content_types=['text', 'photo', 'document'])
def echo_all(message):
    while True:
        try:
            try:
                user_id = msg.getUserID(message)
                message = message
                text = message.text
                msg_check = msg.msgCheck(message)
                ticket_status = mysql.user_tables(user_id)['open_ticket']
                banned_status = mysql.user_tables(user_id)['banned']

                if banned_status == 1:
                    # If User is banned - un-ban user and sent message
                    mysql.unban_user(user_id)
                    bot.reply_to(message, 'ℹ️  *Цей користувач був заблокований.*\nРозблокуйте його та відправте повідомлення._',
                                 parse_mode='Markdown')

                elif ticket_status == 1:
                    # Reset Open Tickets as well as the Spamfilter
                    mysql.reset_open_ticket(user_id)
                    continue

                else:
                    if message.reply_to_message and '(#id' in msg_check:
                        if storage.check_user_to_manager(user_id, message.from_user.id):
                            msg.snd_handler(user_id, bot, message, text)
                            return
                        else:
                            bot.reply_to(message, "Цей користувач вже в обробці")

            except telebot.apihelper.ApiException:
                bot.reply_to(message, '❌ Невдалось відправити повідомлення... \nМожливо користувач заблокував бота.')
                return

        except Exception as e:
            # bot.reply_to(message, '❌ Неправильная команда!')
            return


print("Telegram Support Bot started...")
bot.polling()
