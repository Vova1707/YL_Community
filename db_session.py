import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

SqlAlchemyBase = declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    conn_str = f'sqlite:///{db_file.strip()}'
    print(f"Подключение к базе данных по адресу {conn_str}")
    try:
        engine = sa.create_engine(conn_str, echo=False)
        __factory = orm.sessionmaker(bind=engine)
    except Exception as e:
        raise Exception(conn_str, e)

    import models.__all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
