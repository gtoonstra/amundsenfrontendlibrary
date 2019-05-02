import logging

from http import HTTPStatus

from flask import Response, jsonify, make_response
from flask import current_app as app
from flask.blueprints import Blueprint

from amundsen_application.api.metadata.v0 import USER_ENDPOINT
from amundsen_application.api.utils.request_utils import request_wrapper
from amundsen_application.models.user import load_user, dump_user

REQUEST_SESSION_TIMEOUT_SEC = 3

LOGGER = logging.getLogger(__name__)

blueprint = Blueprint('api', __name__, url_prefix='/api')


@blueprint.route('/auth_user', methods=['GET'])
def current_user() -> Response:
    if app.config['AUTH_USER_METHOD']:
        user = app.config['AUTH_USER_METHOD'](app)
    else:
        raise Exception('Missing auth method')

    url = '{0}{1}/{2}'.format(app.config['METADATASERVICE_BASE'], USER_ENDPOINT, user.user_id)

    response = request_wrapper(method='GET',
                               url=url,
                               client=app.config['METADATASERVICE_REQUEST_CLIENT'],
                               headers=app.config['METADATASERVICE_REQUEST_HEADERS'],
                               timeout_sec=REQUEST_SESSION_TIMEOUT_SEC)

    status_code = response.status_code

    if status_code == HTTPStatus.OK:
        message = 'Success'
    else:
        message = 'Failure'
        logging.error(message)


    payload = {
        'msg': message,
        'user': dump_user(load_user(response.json()))
    }

    return make_response(jsonify(payload), status_code)
