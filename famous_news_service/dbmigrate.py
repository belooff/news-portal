from models import Base


def create_db(engine):
    engine.execute('CREATE SEQUENCE IF NOT EXISTS news_id_seq START 1;')
    Base.metadata.create_all(engine)
