# # clien_market_parser.py
# import requests
# from bs4 import BeautifulSoup
# import os

import telegram
my_token = '643538405:AAGm9ZRYHtSEuLwJMazk7_bTnjlvC9Jx-4w'

# 토큰을 지정해서 bot을 선언해 줍시다! (물론 이 토큰은 dummy!)
bot = telegram.Bot(token=my_token)

updates = bot.getUpdates()  #업데이트 내역을 받아옵니다.

print(updates)
#
# for u in updates:   # 내역중 메세지를 출력합니다.
#     print(u.message)

# updates = bot.getUpdates()
# chat_id = bot.getUpdates()[-1].message.chat.id
# print(chat_id)

# # 파일의 위치
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#
# req = requests.get('http://clien.net/cs2/bbs/board.php?bo_table=sold')
# req.encoding = 'utf-8'
#
# html = req.text
# soup = BeautifulSoup(html, 'html.parser')
# posts = soup.select('td.post_subject')
# latest = posts[1].text


# bot.sendMessage(chat_id=chat_id, text="Hello eight_bot!")
# with open(os.path.join(BASE_DIR, 'latest.txt'), 'r+') as f_read:
#     before = f_read.readline()
#     if before != latest:
#         bot.sendMessage(chat_id=chat_id, text='새 글이 올라왔어요!')
#     else: # 원래는 이 메시지를 보낼 필요가 없지만, 테스트 할 때는 봇이 동작하는지 확인차 넣어봤어요.
#         bot.sendMessage(chat_id=chat_id, text='새 글이 없어요 ㅠㅠ')
#     f_read.close()
#
# with open(os.path.join(BASE_DIR, 'latest.txt'), 'w+') as f_write:
#     f_write.write(latest)
#     f_write.close()

# def start(bot, update):
#     bot.send_message(chat_id=update.message.chat_id, text="봇 작동합니다.")
#     # print(chat_id)
#     # bot.sendMessage(chat_id=chat_id, text="Hello eight_bot!")
#
#
# def unknown(bot, update):
#     bot.send_message(chat_id=update.message.chat_id, text="죄송하지만 그 명령어를 이해할 수 없습니다.")


def main():
    # bot = telegram.Bot(token='647103292:AAF9EL3zSG0R4CYrfy4TnbyJuLSaprCnbyA')
    # chat_id = bot.getUpdates()[-1].message.chat.id

    # updater = Updater(token)
    # dp = updater.dispatcher
    # Start the bot
    # updater.start_polling()
    # dp.add_handler(CommandHandler('start', start))
    # dp.add_handler(MessageHandler(Filters.command, unknown))

    # Run the bot until you press Ctrl-C
    # updater.idle()
    # updater.stop()

    bot.send_message(chat_id='@waldok', text="시마이", timeout=10)
    # print("123")


if __name__ == '__main__':
    main()