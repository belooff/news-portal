import os
import pytest
import json

from nameko.testing.utils import get_container
from nameko.testing.services import worker_factory, entrypoint_hook
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from service import Command, Query
from models import Base, QueryNewsModel
from dbmigrate import create_db


@pytest.fixture
def session():
    engine = create_engine(os.environ.get('COMMANDDB_HOST'))
    create_db(engine)
    Session = sessionmaker(engine)
    return Session()


@pytest.yield_fixture()
def config():

    conf = {
        'AMQP_URI': os.environ.get('QUEUE_HOST'),
        'DB_URIS': {
            'command_famous:Base': os.environ.get('COMMANDDB_HOST'),
        }
    }

    yield conf


def test_add_news(session):
    data = {
        "title": "title test",
        "author": "author test",
        "content": "content test",
        "tags": [
            "test tag1",
            "test tag2",
        ],
    }

    command = worker_factory(Command, db=session)
    result = command.add_news(data)

    assert result['title'] == "title test"
    assert result['version'] == 1

    data['id'] = result['id']
    data['version'] = result['version']

    command = worker_factory(Command, db=session)
    result = command.add_news(data)

    assert result['version'] == 2


def test_integration(runner_factory, config):

    runner = runner_factory(config, Command, Query)
    runner.start()

    container = get_container(runner, Command)
    
    with entrypoint_hook(container, 'add_news') as entrypoint:
        data = {
            "title": "title test",
            "author": "author test",
            "content": "content test",
            "tags": [
                "test tag1",
                "test tag2",
            ],
        }
        result = entrypoint(data)
        
        assert result == data
        
    container = get_container(runner, Query)
    with entrypoint_hook(container, 'get_news') as entrypoint:

        news = json.loads(entrypoint(result['id']))

        assert news["_id"] == result['id']

    with entrypoint_hook(container, 'get_all_news') as get_all_news:

        news = json.loads(get_all_news(1, 10))

        assert len(news) > 0