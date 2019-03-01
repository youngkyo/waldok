# coding=utf-8
import pandas as pd
import requests
import telegram
from bs4 import BeautifulSoup

my_token = '643538405:AAGm9ZRYHtSEuLwJMazk7_bTnjlvC9Jx-4w'
bot = telegram.Bot(token=my_token)


def get_stock_list(kospi_url):
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

    final_list = get_stock_list(kospi_url)
    final_list.extend(get_stock_list(kosdaq_url))

    return pd.DataFrame(final_list, columns=['code', 'name', 'volume'])


# 종목 이름을 입력하면 종목에 해당하는 코드를 불러와 # 네이버 금융(http://finance.naver.com)에 넣어줌
def get_url(item_name, code_df):
    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    code = code.strip()
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)

    return url


def is_desire_volume_reduction(volume):
    if volume < 12:
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


def is_bigger_than(last_low_price, today_low_price):
    if last_low_price > today_low_price:
        return False
    return True


def check_is_fit(df):
    volume_list = list()
    end_price_list = list()
    start_price_list = list()

    today = 0
    yesterday = today + 1

    try:
        for index in range(today, 5):
            volume_list.append(df.iloc[index]['거래량'])
            start_price_list.append(df.iloc[index]['시가'])
            end_price_list.append(df.iloc[index]['종가'])

        # eight_price = calculate_eight_line(end_price_list)

        today_volume = df.iloc[today]['거래량']

        # 오늘이 음봉인지 확인.
        if not is_bear_day(start_price_list[today], end_price_list[today]):
            return False

        # 오늘을 제외한 최근 4일간의 거래량이 15% 이하인지 체크.
        # 해당 거래량이 터진날이 양봉인지 체크 필요.
        for index in range(yesterday, 5):
            value = (today_volume / volume_list[index]) * 100

            if is_desire_volume_reduction(value) and is_bull_day(start_price_list[index], end_price_list[index]) \
                    and is_bigger_than(start_price_list[index], end_price_list[today]):
                return True

    except IndexError:
        return False

    return False


def is_not_eft(name):
    exclude_title = ["KBSTAR", "KOSEF", "KINDEX", "KODEX", "HANARO", "TIGER", "ARIRANG", "인버스", "레버리지"]

    for title in exclude_title:
        if title in name:
            return False

    return True


def specific_news_search(name):
    news_list = []
    url = 'https://search.naver.com/search.naver'
    for page in range(1, 2):
        params = {
            'query': name + " 특징주",
            'where': 'news',
            'start': (page - 1) * 10 + 1,
        }

        response = requests.get(url, params=params)
        html = response.text

        # 뷰티풀소프의 인자값 지정
        soup = BeautifulSoup(html, 'html.parser')

        # 쪼개기
        news_title_list = soup.select('._sp_each_title')
        other_info_list = soup.select('.txt_inline')

        try:
            for index in range(0, 3):
                news_list.append(news_title_list[index].text + ' ' + other_info_list[index].text)

        except IndexError:
            continue

    return news_list


def get_head_subject(stock_df):
    stock_list = []

    for index, row in stock_df.iterrows():
        df = pd.DataFrame()
        url = get_url(row['name'], stock_df)
        for page in range(1, 2):
            pg_url = '{url}&page={page}'.format(url=url, page=page)
            df = df.append(pd.read_html(pg_url, header=0)[0], ignore_index=True)

        df = df.dropna()

        if check_is_fit(df) and is_not_eft(row['name']):
            new_list = specific_news_search(row['name'])
            stock_list.append("*" + row['code'] + " " + row['name'] + "*")
            stock_list.append('\n'.join(new_list))

        if len(stock_list) > 10:
            # print(len(stock_list))
            values = '\n\n'.join(stock_list)
            bot.send_message(chat_id='@waldok', text=values, timeout=10, parse_mode=telegram.ParseMode.MARKDOWN)
            stock_list = []

    return stock_list


def main():
    stock_df = all_stock_name_by_df()
    get_head_subject(stock_df)


if __name__ == "__main__":
    main()
