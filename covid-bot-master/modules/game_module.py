import logger
from database import db_connector as db
import random
from sqlalchemy.sql.expression import func

log = logger.get_logger("game_module")

keyboard = [
    [
        {
            "text": "🔙 Меню",
            "callbackData": "main"
        },
        {
            "text": "▶ Другой вопрос",
            "callbackData": "game_random"
        }
    ]
]


def __get_random_question(db_session):
    """
    get random question for game
    """
    random_row = random.choice(db_session.query(db.GameQuestion).all())
    return random_row.id, random_row.question


def __get_answer(db_session, question_id):
    """
    get question
    """
    answer = db_session.query(db.GameQuestion.answer). \
        filter(db.GameQuestion.id == question_id).scalar()
    comment = db_session.query(db.GameQuestion.comment). \
        filter(db.GameQuestion.id == question_id).scalar()
    return answer, comment


# get content method
def get_question(db_session):
    question_id, question = __get_random_question(db_session)
    return question_id, question


# check answer method
def check_answer(db_session, question_id, user_answer):
    answer, comment = __get_answer(db_session, question_id)
    if str(answer).lower().strip() == user_answer.lower().strip():
        return comment
    return None
