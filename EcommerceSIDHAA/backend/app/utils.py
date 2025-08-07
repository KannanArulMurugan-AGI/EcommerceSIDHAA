import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from app.models import User

def generate_token(user_id):
    """Generates the Auth Token"""
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e

def verify_token(token):
    """Decodes the auth token"""
    try:
        payload = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])
        current_app.logger.info(f"Payload: {payload}")
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'
    except Exception as e:
        current_app.logger.error(f"Error decoding token: {e}")
        return 'Invalid token. Please log in again.'


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            token = request.args.get('token')

        current_app.logger.info(f"Token: {token}")

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            user_id = verify_token(token)
            if isinstance(user_id, str): # Error string returned from verify_token
                return jsonify({'message': user_id}), 401

            current_user = User.get_by_id(user_id)
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated
