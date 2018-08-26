import pandas as pd
import telegram
my_token = '643538405:AAGm9ZRYHtSEuLwJMazk7_bTnjlvC9Jx-4w'

# 토큰을 지정해서 bot을 선언해 줍시다! (물론 이 토큰은 dummy!)
bot = telegram.Bot(token=my_token)


def all_stock_name_by_df():
    code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
    #  종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
    #  우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
    code_df = code_df[['회사명', '종목코드']]
    #  한글로된 컬럼명을 영어로 바꿔준다.

    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
    # for index, row in code_df.iterrows():
    #     print(row['code'], row['name'])
    return code_df


# 종목 이름을 입력하면 종목에 해당하는 코드를 불러와 # 네이버 금융(http://finance.naver.com)에 넣어줌
def get_url(item_name, code_df):
    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)

    # print("요청 URL = {}".format(url))
    return url


def check_data_frame(df):
    volume_list = list()
    try:
        for index in range(1, 6):
            volume_list.append(df.iloc[index]['거래량'])

        a = volume_list[4]
        for index in range(1, 4):
            value = volume_list[index] / a
            if volume_list[index] > 1000000 and value > 11:
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

    # bot.send_message(chat_id='@waldok', text=value_list, timeout=10)


if __name__ == "__main__":
    main()