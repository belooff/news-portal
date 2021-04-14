import json
import logging
import os
import requests

from nameko.web.handlers import http
from nameko.events import event_handler

from models import (
    create_user_node,
    create_label_node,
    create_recommendation,
    get_labels_by_user_id,
    get_users_by_label,
)


class Recommendation:
    name = 'recommendation'

    @event_handler('recommendation_sender', 'receiver')
    def receiver(self, data):
        try:

            user_service_route = os.getenv('USER_SERVICE_ROUTE')

            user = requests.get(
                "{}{}".format(
                    user_service_route,
                    data['user_id']
                )
            )
            user = user.json()

            create_user_node(user)

            for label in data['news']['tags']:
                create_label_node(label)
                create_recommendation(
                    user['id'], label
                )

        except Exception as e:
            logging.error('RELATIONSHIP_ERROR: {}'.format(e))


def error_response(code, ex):
    response = {
        'status': 'fail',
        'message': str(ex),
    }
    return code, json.dumps(response)


class RecommendationApi:
    name = 'recommendation_api'

    @http('GET', '/user/<int:user_id>')
    def get_recommendations_by_user(self, request, user_id):
        try:
            relationship_response = get_labels_by_user_id(user_id)
            http_response = [
                rel.end_node() for rel in relationship_response
            ]
            return 200, json.dumps(http_response)
        except Exception as ex:
            error_response(500, ex)

    @http('GET', '/label/<string:label>')
    def get_users_recommentations_by_label(self, request, label):
        try:
            pass
        except Exception as ex:
            error_response(500, ex)
