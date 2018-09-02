import pandas as pd
import telegram
import configparser
from bs4 import BeautifulSoup
import requests

config = configparser.ConfigParser()
config.read('/home/ec2-user/stock/config/waldokconfig')

my_token = config['DEFAULT']['TELE_TOKEN']
bot = telegram.Bot(token=my_token)


def getStockList(kospi_url):
    stock_list = []

    for i in range(1, 2000):
        url = kospi_url + str(i)
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        items = soup.find_all('tr', {'onmouseover':'mouseOver(this)'})
        if items.__len__() is 0:
            break

        for index in range(0, len(items)):
            # items[0].find_all('tr', class_="number")
            # print(items[index].a.get('href')[-6:]) #종목코드
            # print(items[index].a.text) # 종목명
            # print(items[index].find_all("td", class_="number")[4].text) #시가총액
            # print(items[index].find_all("td", class_="number")[7].text) #거래량
            items_list = items[index]
            class_number_list = items_list.find_all("td", class_="number")
            asset = str(class_number_list[4].text).replace(",", "")
            volume = str(class_number_list[7].text).replace(",", "")

            if int(volume) > 100000 and int(asset) > 400:
                stock_list.append([items_list.a.get('href')[-6:], items_list.a.text, class_number_list[4].text])

    return stock_list


def all_stock_name_by_df():

    kospi_url = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0&&page='
    kosdaq_url = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok=1&page='

    final_list = getStockList(kospi_url)
    final_list.extend(getStockList(kosdaq_url))

    return pd.DataFrame(final_list, columns=['code', 'name', 'volume'])


# 종목 이름을 입력하면 종목에 해당하는 코드를 불러와 # 네이버 금융(http://finance.naver.com)에 넣어줌
def get_url(item_name, code_df):
    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)

    return url


def is_desire_volume_reduction(volume):
    if volume > 11:
        return True

    return False


def is_bull_day(start_price, end_price):
    if start_price < end_price:
        return True

    return False


def is_bear_day(start_price, end_price):
    if start_price > end_price:
        return True

    return False


def calculate_eight_line(end_price_list):
    total = 0
    for price in end_price_list:
        total += price

    return total / end_price_list.__len__()


def check_data_frame(df):
    volume_list = list()
    start_price_list = list()
    end_price_list = list()

    try:
        for index in range(0, 8):
            volume_list.append(df.iloc[index]['거래량'])
            start_price_list.append(df.iloc[index]['시가'])
            end_price_list.append(df.iloc[index]['종가'])

        eight_price = calculate_eight_line(end_price_list)

        today_volume = df.iloc[0]['거래량']
        for index in range(1, 8):
            value = volume_list[index] / today_volume
            if is_desire_volume_reduction(value) and is_bull_day(start_price_list[index], end_price_list[index]) and today_volume >= eight_price:
                return True

    except IndexError:
        return False

    return False


def get_head_subject(stock_df):
    stock_list = []

    for index, row in stock_df.iterrows():
        df = pd.DataFrame()
        url = get_url(row['name'], stock_df)
        for page in range(1, 2):
            pg_url = '{url}&page={page}'.format(url=url, page=page)
            df = df.append(pd.read_html(pg_url, header=0)[0], ignore_index=True)

        df = df.dropna()
        if check_data_frame(df):
            stock_list.append(row['code'] + " " + row['name'])

    return stock_list


def main():
    stock_df = all_stock_name_by_df()
    value = get_head_subject(stock_df)
    value_list = '\n'.join(value)
    if value_list != "":
        bot.send_message(chat_id='@waldok', text=value_list, timeout=10)


if __name__ == "__main__":
    main()