import os
import json
import itertools

from flask import Blueprint, jsonify, request
from nameko.standalone.rpc import ClusterRpcProxy
from nameko.standalone.events import event_dispatcher


news = Blueprint('news', __name__)
CONFIG_RPC = {'AMQP_URI': os.environ.get('QUEUE_HOST')}
BROKER_CONFIG = {'AMQP_URI': os.environ.get('QUEUE_HOST')}



@news.route('/<string:news_type>/<int:news_id>', methods=['GET'])
def get_single_news(news_type, news_id):
    try:
        response = rpc_get_news(news_type, news_id)

        dispatcher = event_dispatcher(BROKER_CONFIG)
        dispatcher('recommendation_sender', 'receiver', {
            'user_id': request.cookies.get('user_id'),
            'news': response['news']
        })

        return jsonify(response), 200
    except Exception as e:
        return error_response(e, 500)


@news.route('/all/<int:num_page>/<int:limit>', methods=['GET'])
def get_all_news(num_page, limit):
    try:
        response_famous = rpc_get_all_news('famous', num_page, limit)
        response_politics = rpc_get_all_news('politics', num_page, limit)
        response_sports = rpc_get_all_news('sports', num_page, limit)

        all_news = itertools.chain(
            response_famous.get('news', []),
            response_politics.get('news', []),
            response_sports.get('news', []),
        )

        response = {
            'status': 'success',
            'news': list(all_news),
        }

        return jsonify(response), 200

    except Exception as e:
        return error_response(e, 500)


@news.route('/<string:news_type>/<int:num_page>/<int:limit>', methods=['GET'])
def get_all_news_per_type(news_type, num_page, limit):
    try:
        response = rpc_get_all_news(news_type, num_page, limit)

        return jsonify(response), 200
    
    except Exception as e:
        return error_response(e, 500)


@news.route('/<string:news_type>', methods=['POST', 'PUT'])
def add_news(news_type):
    post_data = request.get_json()

    if not post_data:
        return error_response('Invalid payload', 400)
    
    try:
        response = rpc_command(news_type, post_data)
        
        return jsonify(response), 201
    except Exception as e:
        return error_response(e, 500)


def error_response(e, code):
    response = {
        'status': 'fail',
        'message': str(e),
    }
    return jsonify(response), code


def rpc_get_news(news_type, news_id):
    with ClusterRpcProxy(CONFIG_RPC) as rpc:
        if news_type == 'famous':
            news = rpc.query_famous.get_news(news_id)
        elif news_type == 'sports':
            news = rpc.query_sports.get_news(news_id)
        elif news_type == 'politics':
            news = rpc.query_politics.get_news(news_id)
        else:
            raise Exception('Invalid news type')

        return {
            'status': 'success',
            'news': json.loads(news)
        }


def rpc_get_all_news(news_type, num_page, limit):
    with ClusterRpcProxy(CONFIG_RPC) as rpc:

        news_type = 'famous'

        if news_type == 'famous':
            news = rpc.query_famous.get_all_news(num_page, limit)
        elif news_type == 'sports':
            news = rpc.query_sports.get_all_news(num_page, limit)
        elif news_type == 'politics':
            news = rpc.query_politics.get_all_news(num_page, limit)
        else:
            raise Exception('Invalid news type')

        return {
            'status': 'success',
            'news': json.loads(news)
        }


def rpc_command(news_type, data):
    with ClusterRpcProxy(CONFIG_RPC) as rpc:
        
        news_type = 'famous'

        if news_type == 'famous':
            news = rpc.query_famous.add_news(data)
        elif news_type == 'sports':
            news = rpc.query_sports.add_news(data)
        elif news_type == 'politics':
            news = rpc.query_politics.add_news(data)
        else:
            raise Exception('Invalid news type')
        
        return {
            'status': 'success',
            'news': json.loads(news)
        }