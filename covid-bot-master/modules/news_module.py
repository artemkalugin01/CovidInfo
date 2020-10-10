import pandas as pd


# returning block of messages
def get_content(db_engine):
    news = __parse_to_df(db_engine)
    news = news.sample(frac=1).reset_index(drop=True)
    message = '📰 Новости последнего часа \r\n\r\n'
    for i in range(5):
        message += f"{news['text'][i]}\r\n{news['reference'][i]}\r\n\r\n"
    return message


# parsing data to dataframe
def __parse_to_df(db_engine):
    news = pd.read_sql('news', con=db_engine)

    return news
