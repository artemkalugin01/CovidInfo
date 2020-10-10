import logger
from database import db_connector, db_methods as db
from updaters import map_update
from updaters import stat_update
from updaters import game_update
from updaters import news_update

log = logger.get_logger("update")


def main():
    db_engine, db_session = db_connector.connect()

    log.info("Updating questions database..")
    # game_update.update_database(db_session)
    log.info("Updating questions database completed")

    log.info("Updating ambulances database..")
    # map_update.update_database(db_engine)
    log.info("Updating ambulances database completed")

    log.info("Updating statistics database..")
    # stat_update.update_database(db_engine)
    log.info("Updating statistics database completed")

    log.info("Updating news database..")
    news_update.update_database(db_engine)
    log.info("Updating news database completed")


# execute only if run as a script
if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        log.fatal(ex)
