import logger
import pandas as pd
import random
from sqlalchemy import func
from database import db_connector as db

log = logger.get_logger("game_update")


def __add_game_question(db_session, question, answer):
    """
    add question for game
    """
    db_session.add(db.GameQuestion(question, answer))
    db_session.commit()


def update_database(db_session):
    return
