import sqlalchemy as sa
import sqlalchemy.orm as orm
import logging
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

SqlAlchemyBase = declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory != None:
        return

    #conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    conn_str = 'sqlite:///opt/build/db/db.sqlite'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    import models.__all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session():
    global __factory
    return __factory()
