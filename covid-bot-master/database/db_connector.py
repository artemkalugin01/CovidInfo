import urllib
import configparser
import logger
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event, create_engine
from sqlalchemy.orm import scoped_session
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

# region models
Base = declarative_base()


class IcqUser(Base):
    __tablename__ = 'icq_users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    icq_id = sqlalchemy.Column(sqlalchemy.Unicode(80), unique=True)
    state = sqlalchemy.Column(sqlalchemy.Unicode(50))

    passport = sqlalchemy.Column(sqlalchemy.Unicode(10))
    latitude = sqlalchemy.Column(sqlalchemy.Float)
    longitude = sqlalchemy.Column(sqlalchemy.Float)

    def __init__(self, icq_id):
        self.icq_id = icq_id
        self.state = "main"


class UserState(Base):
    __tablename__ = 'user_states'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.Unicode(50), unique=True)
    message = sqlalchemy.Column(sqlalchemy.Unicode(4000))
    keyboard = sqlalchemy.Column(sqlalchemy.Unicode(1000))

    def __init__(self, name, message, keyboard):
        self.name = name
        self.message = message
        self.keyboard = keyboard


class GameQuestion(Base):
    __tablename__ = 'game_questions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    question = sqlalchemy.Column(sqlalchemy.Unicode(1000))
    answer = sqlalchemy.Column(sqlalchemy.Unicode(1000))
    comment = sqlalchemy.Column(sqlalchemy.Unicode(1000))

    def __init__(self, question, answer, comment):
        self.question = question
        self.answer = answer
        self.comment = comment


# endregion

# logging and configuration


def connect():
    log = logger.get_logger("db")
    config = configparser.ConfigParser()
    config.read("database/conf.ini")

    log.info("Connection to database")

    db_connection_parameters = urllib.parse.quote_plus(f"DRIVER={config.get('Database', 'driver')};"
                                                       f"SERVER={config.get('Database', 'server')};"
                                                       f"DATABASE={config.get('Database', 'database')};"
                                                       f"UID={config.get('Database', 'login')};"
                                                       f"PWD={config.get('Database', 'password')};")
    try:
        engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect={}".format(db_connection_parameters),
                                          pool_size=10000, max_overflow=0)
        Base.metadata.create_all(engine)

        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory)

        log.info("Database connected successfully")
    except Exception as ex:
        log.error("Database connection error")
        raise

    @event.listens_for(engine, 'before_cursor_execute')
    def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
        if executemany:
            cursor.fast_executemany = True
            cursor.commit()

    return engine, Session
