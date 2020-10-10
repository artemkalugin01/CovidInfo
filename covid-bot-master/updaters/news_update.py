import logger
from bs4 import BeautifulSoup
import pandas as pd
import urllib.request

log = logger.get_logger("news_module")


def update_database(db_engine):
    log.info('Sending data to sql')
    data = __get_df()
    data.to_sql('news', con=db_engine, if_exists='replace')
    log.info('Data updated')


def __get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()


def __get_reference_from_string(string):
    # Some strings already contain full reference.
    # Check this case.
    string = string if "//" in string else 'https://news.mail.ru' + string
    string = string[:string.find('?')]
    return string


def __parse(html):
    log.info('Parsing data from site')
    soup = BeautifulSoup(html, features="lxml")
    data = soup.find_all('a', href=True)

    result = []

    for new in data:
        if 'newsitem' in str(new) and 'story=coronavirus' in str(new):
            result.append({
                'text': new.text,
                'reference': __get_reference_from_string(str(new['href']))
            })

    return result


def __get_df():
    log.info('Parsing data to df')
    dict = __parse(__get_html('https://news.mail.ru/story/incident/coronavirus/'))
    df = pd.DataFrame(dict)
    return df
