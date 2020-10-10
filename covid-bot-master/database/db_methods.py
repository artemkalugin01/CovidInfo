from database import db_connector as db
import json


# region users
def get_user_state(db_session, icq_id):
    """
    gets current user state
    """
    if db_session.query(db.IcqUser.id).filter(db.IcqUser.icq_id == icq_id).scalar() is None:
        db_session.add(db.IcqUser(icq_id))
        db_session.commit()

    return db_session.query(db.IcqUser.state).filter(db.IcqUser.icq_id == icq_id).scalar()


def set_user_state(db_session, icq_id, new_state):
    """
    sets current user state
    """
    user = db_session.query(db.IcqUser).filter(db.IcqUser.icq_id == icq_id).scalar()
    user.state = new_state
    db_session.commit()


def get_answer(db_session, state_name):
    """
    get default answer for state
    """
    message = db_session.query(db.UserState.message). \
        filter(db.UserState.name == state_name).scalar()
    keyboard = db_session.query(db.UserState.keyboard). \
        filter(db.UserState.name == state_name).scalar()

    if keyboard is None:
        return message, None

    return message, json.loads(keyboard)
# endregion
