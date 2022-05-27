import pymysql
import config
from datetime import datetime


# Connect to MySQL Database
def getConnection():
    connection = pymysql.connect(host=config.mysql_host,
                                 user=config.mysql_user,
                                 password=config.mysql_pw,
                                 db=config.mysql_db,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor,
                                 autocommit=True)
    return connection


def createTables():
    connection = getConnection()
    with connection.cursor() as cursor:
        tablename = "users"
        try:
            cursor.execute(
                "	CREATE TABLE `" + tablename + "` (  `userid` int(11) DEFAULT NULL,  `open_ticket` int(4) DEFAULT 0,  `banned` int(4) DEFAULT 0,  \
                `open_ticket_spam` int(4) DEFAULT 1,  `verified` int(4) DEFAULT 0,  `open_ticket_link` varchar(50) DEFAULT NULL,  `open_ticket_time` datetime NOT NULL DEFAULT '1000-01-01 00:00:00', `organization` varchar(50) DEFAULT NULL, `card_number` varchar(50) DEFAULT NULL, `ticket_number` varchar(50) DEFAULT NULL)")
            return createTables
        except Exception as e:
            print(e)
        try:
            cursor.execute(f'''ALTER TABLE {tablename}
                               ADD COLUMN `ticket_number` varchar(50) DEFAULT NULL''')
        except Exception as e:
            print(e)
                


def spam(user_id):
    connection = getConnection()
    with connection.cursor() as cursor:
        sql = "SELECT banned, open_ticket, open_ticket_spam FROM users WHERE userid = %s"
        cursor.execute(sql, user_id)
        data = cursor.fetchone()
        ticket_spam = data['open_ticket_spam']

        sql = "UPDATE users SET open_ticket_spam = %s WHERE userid = %s"
        spam = ticket_spam + 1
        cursor.execute(sql, (spam, user_id))
        return spam


def verif_update(user_id, state, organization, card_number):
    connection = getConnection()
    with connection.cursor() as cursor:
        sql = "UPDATE users SET verified = %s, organization = %s, card_number = %s WHERE userid = %s"
        cursor.execute(sql, (state, organization, card_number, user_id))


def user_tables(user_id):
    connection = getConnection()
    with connection.cursor() as cursor:
        sql = "SELECT open_ticket, banned, open_ticket_time, open_ticket_spam, verified, open_ticket_link, card_number, organization FROM users WHERE userid = %s"
        cursor.execute(sql, user_id)
        data = cursor.fetchone()
        return data


def getOpenTickets():
    connection = getConnection()
    with connection.cursor() as cursor:
        tmp = []
        cursor.execute("SELECT userid FROM users WHERE open_ticket = 1")
        for i in cursor.fetchall():
            tmp.append(i['userid'])
        return tmp


def getBanned():
    connection = getConnection()
    with connection.cursor() as cursor:
        tmp = []
        cursor.execute("SELECT userid FROM users WHERE banned = 1")
        for i in cursor.fetchall():
            tmp.append(i['userid'])
        return tmp


def start_bot(user_id):
    connection = getConnection()
    with connection.cursor() as cursor:
        sql = "SELECT EXISTS(SELECT userid FROM users WHERE userid = %s)"
        cursor.execute(sql, user_id)
        result = cursor.fetchone()
        # If the User never started the bot before, add the Telegram ID to the database
        if not list(result.values())[0]:
            sql = "INSERT INTO users(userid) VALUES (%s)"
            cursor.execute(sql, user_id)


def open_ticket(user_id):
    connection = getConnection()
    with connection.cursor() as cursor:
        sql = "UPDATE users SET open_ticket = 1, open_ticket_time = %s WHERE userid = %s"
        now = datetime.now()
        cursor.execute(sql, (now, user_id))
        open_tickets.append(user_id)
        return open_ticket


def update_name(user_id, name):
    connection = getConnection()
    with connection.cursor() as cursor:
        sql = "UPDATE users SET organization = %s WHERE userid = %s"
        cursor.execute(sql, (name, user_id))

def update_telephone(user_id, telephone):
    connection = getConnection()
    with connection.cursor() as cursor:
        sql = "UPDATE users SET card_number = %s WHERE userid = %s"
        cursor.execute(sql, (telephone, user_id))

def update_ticket(user_id, number):
    connection = getConnection()
    with connection.cursor() as cursor:
        sql = "UPDATE users SET ticket_number = %s, verified=1 WHERE userid = %s"
        cursor.execute(sql, (number, user_id))


def post_open_ticket(link, msg_id):
    connection = getConnection()
    with connection.cursor() as cursor:
        sql = "UPDATE users SET open_ticket_link = %s WHERE userid = %s"
        cursor.execute(sql, (link, msg_id))
        return post_open_ticket


def reset_open_ticket(user_id):
    connection = getConnection()
    with connection.cursor() as cursor:
        sql = "UPDATE users SET open_ticket = 0,  open_ticket_spam = 1 WHERE userid = %s"
        cursor.execute(sql, user_id)
        open_tickets.pop(open_tickets.index(user_id))
        return reset_open_ticket


def ban_user(user_id):
    connection = getConnection()
    with connection.cursor() as cursor:
        sql = "UPDATE users SET banned = 1 WHERE userid = %s"
        cursor.execute(sql, user_id)
        banned.append(user_id)
        return ban_user


def unban_user(user_id):
    connection = getConnection()
    with connection.cursor() as cursor:
        sql = "UPDATE users SET banned = 0 WHERE userid = %s"
        cursor.execute(sql, user_id)
        banned.pop(banned.index(user_id))
        return unban_user


def verif_user(card_number):
    connection = getConnection()
    with connection.cursor() as cursor:
        sql = "SELECT * FROM userDataCrm WHERE card_number = %s"
        cursor.execute(sql, card_number)
        result = cursor.fetchone()
        return result


createTables = createTables()
open_tickets = getOpenTickets()
banned = getBanned()
