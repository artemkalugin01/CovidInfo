import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import logger
from datetime import *
import plot_extension
matplotlib.use('Agg')

log = logger.get_logger("stat_module")

__confirmed = 'Confirmed cases'
__recovered = 'Recoveries'
__death = 'Deaths'


def get_content(db_engine):
    return __get_rus(db_engine), __get_mos(db_engine)


# get stat of total cases in Moscow over time
def __get_mos_total(mos_total, x_label):
    message = f'Общая статистика по Москве\r\n' \
              f'🦠 Заболевших: {mos_total[__confirmed][0]} \r\n' \
              f'🦠 Излечившихся: {mos_total[__recovered][0]} \r\n' \
              f'🦠 Умерших: {mos_total[__death][0]}'

    return message


# get stat of new cases in Moscow over time
def __get_mos_new(mos_new, x_label):
    log.info(f"Statistic creator started for mos new")

    plt.clf()
    plt.bar(x_label, mos_new[__confirmed].tail(30), label='Динамика заражений', color='#EB004177')
    plt.bar(x_label, mos_new[__recovered].tail(30), label='Динамика выздоровлений', color='#EB0041FF')
    plt.title('Количество новых случаев по Москве')
    plt.ylabel('Количество людей')
    plt.xticks(x_label, x_label, rotation=45, fontsize=9)
    plt.legend()

    # saving Moscow graph to a binary
    binary_file = plot_extension.get_binary(plt, log, 'newmoscow')
    message = f'Новые данные по Москве\r\n' \
              f'🦠 Заболевших: {mos_new[__confirmed][0]} \r\n' \
              f'🦠 Излечившихся: {mos_new[__recovered][0]} \r\n' \
              f'🦠 Умерших: {mos_new[__death][0]}'
    return binary_file, message

# parsing to dataframe Moscow cases files
def __get_mos(db_engine):
    log.info(f"Statistic creator started for mos")

    mos_total = pd.read_sql('mos_total', con=db_engine)
    mos_new = pd.read_sql('mos_new', con=db_engine)

    mos_total = mos_total.drop('index', axis=1)
    mos_new = mos_new.drop('index', axis=1)
    mos_total = mos_total.reindex(index=mos_total.index[::-1])
    mos_new = mos_new.reindex(index=mos_new.index[::-1])

    x_label = []
    for i in range(30):
        today = datetime.today()
        day = today - timedelta(days=i)
        x_label.append(day.strftime('%d/%m'))
    x_label = x_label[::-1]

    return __get_mos_total(mos_total, x_label), __get_mos_new(mos_new, x_label)


# parsing to dataframe Russia files
def __get_rus(db_engine):
    log.info(f"Statistic creator started for rus")

    rus_total = pd.read_sql('rus_total', con=db_engine)
    rus_new = pd.read_sql('rus_new', con=db_engine)

    rus_total = rus_total.drop('index', axis=1)
    rus_new = rus_new.drop('index', axis=1)
    rus_total = rus_total.reindex(index=rus_total.index[::-1])
    rus_new = rus_new.reindex(index=rus_new.index[::-1])

    x_label = []
    for i in range(30):
        today = datetime.today()
        day = today - timedelta(days=i)
        x_label.append(day.strftime('%d/%m'))
    x_label = x_label[::-1]

    return __get_rus_total(rus_total, x_label), __get_rus_new(rus_new, x_label)


# get stat of new cases in Russia over time
def __get_rus_new(rus_new, x_label):
    log.info(f"Statistic creator started for rus new")

    plt.clf()
    plt.bar(x_label, rus_new[__confirmed].tail(30), label='Динамика заражений', color='#EB004177')
    plt.bar(x_label, rus_new[__recovered].tail(30), label='Динамика выздоровлений', color='#EB0041FF')
    plt.title('Количество новых случаев по Москве')
    plt.ylabel('Количество людей')
    plt.xticks(x_label, x_label, rotation=45, fontsize=9)
    plt.legend()

    binary_file = plot_extension.get_binary(plt, log, 'newmoscow')
    message = f'Новые данные по России\r\n' \
              f'🦠 Заболевших: {rus_new[__confirmed][0]} \r\n' \
              f'🦠 Излечившихся: {rus_new[__recovered][0]} \r\n' \
              f'🦠 Умерших: {rus_new[__death][0]}'
    return binary_file, message


# get stat of total cases in Russia over time
def __get_rus_total(mos_total, x_label):
    message = f'Общая статистика по России\r\n' \
              f'🦠 Заболевших: {mos_total[__confirmed][0]} \r\n' \
              f'🦠 Излечившихся: {mos_total[__recovered][0]} \r\n' \
              f'🦠 Умерших: {mos_total[__death][0]}'

    return message
