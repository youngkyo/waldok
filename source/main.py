import pandas as pd
import telegram
import configparser

config = configparser.ConfigParser()
config.read('/home/ec2-user/stock/config/waldokconfig')

my_token = config['DEFAULT']['TELE_TOKEN']
bot = telegram.Bot(token=my_token)


def all_stock_name_by_df():
    code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)

    code_df = code_df[['회사명', '종목코드']]

    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
    return code_df


# 종목 이름을 입력하면 종목에 해당하는 코드를 불러와 # 네이버 금융(http://finance.naver.com)에 넣어줌
def get_url(item_name, code_df):
    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)

    # print("요청 URL = {}".format(url))
    return url


def is_desire_volume(volume):
    if volume > 1000000:
        return True

    return False


def is_desire_volume_reduction(volumn):
    if volumn > 11:
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


def check_data_frame(df):
    volume_list = list()
    start_price_list = list()
    end_price_list = list()

    try:
        for index in range(1, 6):
            volume_list.append(df.iloc[index]['거래량'])
            start_price_list.append(df.iloc[index]['시가'])
            end_price_list.append(df.iloc[index]['종가'])

        today_volume = df.iloc[0]['거래량']
        for index in range(1, 6):
            value = volume_list[index] / today_volume
            if is_desire_volume(volume_list[index]) and is_desire_volume_reduction(value) and is_bull_day(
                    start_price_list[index], end_price_list[index]) and is_bull_day(df.iloc[0]['시가'], df.iloc[0]['종가']):
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

    bot.send_message(chat_id='@waldok', text=value_list, timeout=10)


if __name__ == "__main__":
    main()