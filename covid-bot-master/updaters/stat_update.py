import ssl
import pandas as pd
import json
import datetime
import requests
import logger

ssl._create_default_https_context = ssl._create_unverified_context
log = logger.get_logger("stat_update")


def fix_format(column):
    arr = []
    for value in column:
        if value == '-':
            arr.append(0)
        else:
            arr.append(value)
    return arr


def update_database(db_engine):
    # reading json file - regions dataframe
    raw = requests.get('https://covid19.rosminzdrav.ru/wp-json/api/mapdata/')
    regions = json.loads(raw.text)['Items']

    date = pd.Series([datetime.datetime.now().date() for region in regions], dtype='datetime64[ns]')
    name = pd.Series([region['LocationName'] for region in regions], dtype='str')
    confirmed = pd.Series([region['Confirmed'] for region in regions], dtype='int64')
    observations = pd.Series([region['Observations'] for region in regions], dtype='int64')
    recovered = pd.Series([region['Recovered'] for region in regions], dtype='int64')
    deaths = pd.Series([region['Deaths'] for region in regions], dtype='int64')

    regions_stat = pd.DataFrame({'date': date, 'name': name, 'observations': observations,
                                 'confirmed': confirmed, 'recovered': recovered, 'deaths': deaths})
    regions_stat.to_sql('regions_stat', con=db_engine, if_exists='append')


    # reading Moscow dataframe
    russia_stat_url = 'https://www.statista.com/statistics/1107929/cumulative-coronavirus-cases-in-russia/'
    dfs = pd.read_html(russia_stat_url)
    rus_total_df = dfs[0]
    rus_total_df = rus_total_df.drop('Unnamed: 0', axis=1)

    for column in rus_total_df.columns:
        rus_total_df[column] = fix_format(rus_total_df[column])

    rus_total_df.to_sql('rus_total', con=db_engine, if_exists='replace')

    # Russia dataframe
    temp_df = rus_total_df

    for column in temp_df.columns:
        temp_df[column] = fix_format(temp_df[column])

    confirmed_rus = []
    active_rus = []
    recover_rus = []
    death_rus = []

    for i in range(len(temp_df) - 1):
        if temp_df['Confirmed cases'][i] - temp_df['Confirmed cases'][i + 1] > 0:
            confirmed_rus.append(temp_df['Confirmed cases'][i] - temp_df['Confirmed cases'][i + 1])
        else:
            confirmed_rus.append(0)

        if int(temp_df['Active cases'][i]) - int(temp_df['Active cases'][i + 1]) > 0:
            active_rus.append(int(temp_df['Active cases'][i]) - int(temp_df['Active cases'][i + 1]))
        else:
            active_rus.append(0)

        if int(temp_df['Recoveries'][i]) - int(temp_df['Recoveries'][i + 1]) > 0:
            recover_rus.append(int(temp_df['Recoveries'][i]) - int(temp_df['Recoveries'][i + 1]))
        else:
            recover_rus.append(0)

        if int(temp_df['Deaths'][i]) - int(temp_df['Deaths'][i + 1]) > 0:
            death_rus.append(int(temp_df['Deaths'][i]) - int(temp_df['Deaths'][i + 1]))
        else:
            death_rus.append(0)
    rus_new_df = pd.DataFrame({'Confirmed cases': confirmed_rus, 'Active cases': active_rus,
                               'Recoveries': recover_rus, 'Deaths': death_rus})
    rus_new_df.to_sql('rus_new', con=db_engine, if_exists='replace')


    moscow_stat_url = 'https://www.statista.com/statistics/1110772/number-of-covid-19-cases-in-moscow/'
    dfs = pd.read_html(moscow_stat_url)
    mos_total_df = dfs[0]
    mos_total_df = mos_total_df.drop('Unnamed: 0', axis=1)
    for column in mos_total_df.columns:
        mos_total_df[column] = fix_format(mos_total_df[column])
    mos_total_df.rename(columns={'Deaths*': 'Deaths'}, inplace=True)
    mos_total_df.to_sql('mos_total', con=db_engine, if_exists='replace')

    temp_df = mos_total_df
    for column in temp_df.columns:
        temp_df[column] = fix_format(temp_df[column])

    confirmed_mos = []
    recover_mos = []
    death_mos = []

    for i in range(len(temp_df) - 1):
        if temp_df['Confirmed cases'][i] - temp_df['Confirmed cases'][i + 1] > 0:
            confirmed_mos.append(temp_df['Confirmed cases'][i] - temp_df['Confirmed cases'][i + 1])
        else:
            confirmed_mos.append(0)

        if int(temp_df['Recoveries'][i]) - int(temp_df['Recoveries'][i + 1]) > 0:
            recover_mos.append(int(temp_df['Recoveries'][i]) - int(temp_df['Recoveries'][i + 1]))
        else:
            recover_mos.append(0)

        if int(temp_df['Deaths'][i]) - int(temp_df['Deaths'][i + 1]) > 0:
            death_mos.append(int(temp_df['Deaths'][i]) - int(temp_df['Deaths'][i + 1]))
        else:
            death_mos.append(0)

    # updating Moscow dataframe to database
    mos_new_df = pd.DataFrame({'Confirmed cases': confirmed_mos, 'Recoveries': recover_mos, 'Deaths': death_mos})
    mos_new_df.to_sql('mos_new', con=db_engine, if_exists='replace')
    # endregion
