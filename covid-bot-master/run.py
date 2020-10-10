import bot_api
import logger
from database import db_connector, db_methods as db

from modules import map_module
from modules import stat_module
from modules import game_module
from modules import pharmacy_map
from modules import shop_map
from modules import news_module
from modules import qr_module

log = logger.get_logger("run")
_, Session = db_connector.connect()

default_keyboard = [
    [
        {
            "text": "Меню",
            "callbackData": "main"
        }
    ]
]


# change user state
def update_state(user_id, new_state):
    # set state
    db.set_user_state(Session(), user_id, new_state)
    # send updated state
    message, keyboard = db.get_answer(Session(), new_state)
    bot_api.send_message(user_id, message, keyboard)


# handler for message [THREAD]
def message_handler(user_id, state, message, lon, lat, payload):
    try:
        reacted = False

        if state == 'ambulances_map' and (lon and lat):
            binary_data, message = map_module.get_content(Session().bind, lon=lon, lat=lat)
            bot_api.send_file(user_id, binary_data, message)
        elif state == 'pharmacies_map' and (lon and lat):
            binary_data, message = pharmacy_map.get_content(lon=lon, lat=lat)
            bot_api.send_file(user_id, binary_data, message)
        elif state == 'shops_map' and (lon and lat):
            binary_data, message = shop_map.get_content(lon=lon, lat=lat)
            bot_api.send_file(user_id, binary_data, message)
        elif state == 'pass':
            binary_data = qr_module.get_content()
            bot_api.send_file(user_id, binary_data, 'Ваш QR-код готов')
        elif state[0:14] == 'game_question_':
            question_id = int(state.split("_")[2])
            comment = game_module.check_answer(Session(), question_id, message)
            if not comment:
                bot_api.send_message(user_id, '📝 Ответ неверный, попробуйте еще раз', game_module.keyboard)
            else:
                bot_api.send_message(user_id, f'📝 Ответ верный! {comment}', default_keyboard)
                button_handler(user_id, state, 'game_random', 0, payload)
            reacted = True
        else:
            message, keyboard = db.get_answer(Session(), state)
            bot_api.send_message(user_id, message, keyboard)
            reacted = True

        if not reacted:
            update_state(user_id, 'main')
    except Exception as ex:
        log.error(ex)


# handler for button [THREAD]
def button_handler(user_id, state, action, query_id, payload):
    try:
        reacted = False

        if action == 'news':
            message = news_module.get_content(Session().bind)
            bot_api.send_message(user_id, message)
        elif action == 'stat':
            stat_list = stat_module.get_content(Session().bind)
            for stat in stat_list:
                bot_api.send_message(user_id, stat[0])
                bot_api.send_file(user_id, stat[1][0], stat[1][1])
        elif action == 'game_random':
            question_id, question = game_module.get_question(Session())
            update_state(user_id, 'game_question_'+str(question_id))
            bot_api.send_message(user_id, '❓ ' + question, default_keyboard)
            reacted = True
        else:
            update_state(user_id, action)
            reacted = True

        if not reacted:
            update_state(user_id, 'main')

        bot_api.send_confirmation(user_id, query_id)
    except Exception as ex:
        log.error(ex)


# entry point
def main():
    log.info("Bot started")

    # start to listen events
    bot_api.listen_events(Session(), message_handler, button_handler)


# execute only if run as a script
if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        log.fatal(ex)
