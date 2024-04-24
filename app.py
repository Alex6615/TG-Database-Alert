import os 
import time
import requests
import datetime
import multiprocessing as mp

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from essential_tokens import TELEGRAM_TOKEN, allow_groups, Group_Alert, Topic_Id
t_token = TELEGRAM_TOKEN

from elasticTools import ElasticGetter


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id not in allow_groups :
        print(f"Group {update.message.chat.id} not allow !")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="❤️ I'm a db_alerts Bot")

async def getinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id not in allow_groups :
        print(f"Group {update.message.chat.id} not allow !")
        return
    chatId = update.message.chat.id
    username = update.message.from_user.username
    userId = update.message.from_user.id
    reply_text = f"<b>CHAT ID</b> : <code>{chatId}</code>\n<b>USER</b> : <code>{username}</code>\n<b>USER ID</b> : <code>{userId}</code>"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text, parse_mode='HTML')

def send_message(messgae:str):
    if len(messgae) == 0 :
        return 
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={Group_Alert}&text={messgae}&parse_mode=HTML&message_thread_id={Topic_Id}"
    req = requests.post(url = url)
    req.close()

def timeConverter(timestamp:str):
    x = timestamp.split('T')[0]
    y = timestamp.split('T')[1].split('.')[0]
    
    datetime_str = f"{x} {y}"
    
    datetime_object = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    timeChange = datetime.timedelta(hours=8)
    return (datetime_object + timeChange).strftime("%m/%d/%Y %H:%M:%S")

def getErrorLog():
    while True:
        es = ElasticGetter()
        errorLogs, errorLogsCounts = es.getlog()
        reply_text_count = 0
        reply_text = ""
        for index in range(0, len(errorLogs)) :
            if reply_text_count == 0 :
                reply_text += "<b>⚠️ DB ALERT : </b>" + "\n➖➖➖➖➖➖➖➖➖➖➖➖➖➖" + "\n\n"
            errmsg = ""
            errmsgList = errorLogs[index]['error']['message']
            for err in errmsgList :
                errmsg += err + "\n"
            timestamp = errorLogs[index]['@timestamp']
            eventTime = timeConverter(timestamp=timestamp)
            reply_text += f"🕒 <u>{eventTime}</u>" + "\n" + \
            f"🖥️ <i>HOSTNAME</i> : <code>{errorLogs[index]['host']['name']}</code>" + "\n" + \
            f"☁️ <i>CLOUD PROVIDER</i> : <code>{errorLogs[index]['cloud']['provider']}</code>" + "\n" + \
            f"<pre language='c++'>{errorLogs[index]['message']}</pre>" + "\n\n" 
            #f"<b>ERR_MSG</b> : \n<code>{errmsg}</code>" + "\n\n"
            reply_text_count += 1
            if reply_text_count == 5  :
                send_message(messgae=reply_text)
                reply_text = ""
                reply_text_count = 0 
            elif len(errorLogs) == (index + 1) :
                send_message(messgae=reply_text)
            else :
                pass
        time.sleep(60)

def Activate_bot():
    """Run the bot."""
    start_handler = CommandHandler('start', start)
    getinfo_handler = CommandHandler('getinfo', getinfo)

    application = Application.builder().token(t_token).build()
    
    application.add_handler(start_handler)
    application.add_handler(getinfo_handler)

    application.run_polling()


def main():
    process_lists = []
    print("bot added")
    process_lists.append(mp.Process(target=Activate_bot))
    process_lists[0].start()
    print("loop added")
    process_lists.append(mp.Process(target=getErrorLog))
    process_lists[1].start()

    for process in process_lists :
        process.join()


if __name__ == '__main__':
    main()
    
