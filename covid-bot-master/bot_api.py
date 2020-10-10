import math
from concurrent.futures.thread import ThreadPoolExecutor
import requests
import logger
import json
from urllib import parse
from database import db_methods as db

# bot token
BOT_TOKEN = '001.2137597123.2463626034:752499739'

# logger
log = logger.get_logger("bot_api")


def __parse_geo_data(message):
    try:
        parsed = parse.urlsplit(message)
        params = dict(parse.parse_qsl(parsed.query))
        lat, lon = [float(x) for x in params['query'].split(',')]
        if math.isnan(lon) or math.isnan(lat):
            raise Exception("Bad format")
        return lon, lat
    except Exception as ex:
        return None, None


def listen_events(db_session, message_handler, button_handler):
    """
    all event listener

    message_handler (user_id, state, message, lon, lat, payload)

    button_handler (user_id, state, action, payload)
    """

    executor = ThreadPoolExecutor(max_workers=100000)

    # last event id
    last_event_id = 0

    # infinite receive
    while True:
        # api query
        raw_response = requests.get('https://api.icq.net/bot/v1/events/get',
                                    params={'token': BOT_TOKEN,
                                            'lastEventId': last_event_id, 'pollTime': '60'})
        # api response
        data = raw_response.json()

        # parsing
        for event in data['events']:
            log.debug(event)

            # set last event id
            last_event_id = event['eventId']

            # event is callback for button
            if event['type'] == 'callbackQuery':
                log.debug(f"[{event['payload']['from']['userId']}] -> [BOT]: callbackData = <{event['payload']['callbackData']}>")
                executor.submit(button_handler, event['payload']['from']['userId'],
                                db.get_user_state(db_session, event['payload']['from']['userId']),
                                event['payload']['callbackData'],
                                event['payload']['queryId'],
                                event['payload'])

            # event is new message
            elif event['type'] == 'newMessage':
                log.debug(f"[{event['payload']['from']['userId']}] -> [BOT]: message = <{event['payload']['text']}>")

                lon, lat = __parse_geo_data(event['payload']['text'])
                executor.submit(message_handler, event['payload']['from']['userId'],
                                db.get_user_state(db_session, event['payload']['from']['userId']),
                                event['payload']['text'],
                                lon,
                                lat,
                                event['payload'])


def send_message(user_id, message, keyboard=None):
    """ send text message with keyboard """

    log.debug(f"[BOT] -> [{user_id}]: message = <{message}>, keyboard = <{keyboard}>")

    # if only message, without keyboard
    if not keyboard:
        return requests.get('https://api.icq.net/bot/v1/messages/sendText',
                            params={'token': BOT_TOKEN, 'chatId': user_id,
                                    'text': message})

    # with specific keyboard for message
    return requests.get('https://api.icq.net/bot/v1/messages/sendText',
                        params={'token': BOT_TOKEN, 'chatId': user_id,
                                'text': message, 'inlineKeyboardMarkup': json.dumps(keyboard)})


def send_file(user_id, binary_data, caption=None):
    log.debug(f"[BOT] -> [{user_id}]: binary_data = <file>, caption = {caption}")

    return requests.post('https://api.icq.net/bot/v1/messages/sendFile',
                         params={'token': BOT_TOKEN, 'chatId': user_id,
                                 'caption': caption}, files={'file': binary_data})


def send_confirmation(user_id, query_id, notification=None):
    """ send callback 'ok' for button """

    log.debug(f"[BOT] -> [{user_id}]: query_id = <{query_id}>, notification = <{notification}>")

    # if only confirmation, without alert
    if not notification:
        return requests.get('https://api.icq.net/bot/v1/messages/answerCallbackQuery',
                            params={'token': BOT_TOKEN, 'queryId': query_id})

    # confirmation with specific alert
    return requests.get('https://api.icq.net/bot/v1/messages/answerCallbackQuery',
                        params={'token': BOT_TOKEN, 'queryId': query_id,
                                'text': notification})
