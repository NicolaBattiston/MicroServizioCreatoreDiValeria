#!/usr/bin/env python3
import argparse
import logging
import uuid
from flask import Flask, Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest
from modules.config import load_config
from modules.webwalk import start_webwalk, MockWebWalker
from modules.valeria import configure_company, import_vector_json
from modules.crypto_utils import generate_custom_link

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask application and API blueprint
app = Flask(__name__)
api = Blueprint('api', __name__)

# Global holders for config and mock
config = {}
mock_webwalker = None

# Authentication: Next-Out tokens
VALID_NEXTOUT_TOKENS = []

def load_tokens():
    global VALID_NEXTOUT_TOKENS
    tokens = config.get('NEXTOUT_TOKENS', [])
    if isinstance(tokens, list):
        VALID_NEXTOUT_TOKENS = tokens
    else:
        VALID_NEXTOUT_TOKENS = []

@api.before_app_first_request
def setup_auth():
    # Populate valid tokens from config
    load_tokens()

@api.before_request
def authenticate():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Next-Out '):
        return jsonify({'status': 'failed', 'error': 'Unauthorized'}), 401
    token = auth.split(' ', 1)[1]
    if token not in VALID_NEXTOUT_TOKENS:
        return jsonify({'status': 'failed', 'error': 'Unauthorized'}), 401

@api.route('/start', methods=['POST'])
def start():
    try:
        try:
            data = request.get_json(force=True) or {}
        except BadRequest:
            return jsonify({'status': 'failed', 'error': 'Invalid JSON body'}), 400
        job_id = data.get('job_id', '')
        if not job_id:
            return jsonify({'status': 'failed', 'error': 'Missing job_id'}), 400
        try:
            uuid.UUID(job_id)
        except ValueError:
            return jsonify({'status': 'failed', 'error': 'Invalid job_id format, must be UUID'}), 400

        # Invoke WebWalker (mock or real)
        if app.config.get('USE_MOCKS'):
            logger.info(f"[Mock] Starting WebWalker for job_id: {job_id}")
            result = mock_webwalker.process_job(job_id)
        else:
            logger.info(f"[Real] Starting WebWalker for job_id: {job_id}")
            result = start_webwalk(job_id, config['WEBWALKER_URL'])

        # Validate response
        company_id = result.get('company_id')
        company_name = result.get('company_name')
        if not company_id or not company_name:
            return jsonify({'status': 'failed', 'job_id': job_id, 'error': 'Missing company_id or company_name in response'}), 500

        # Configure company
        configure_company(result, config['VALERIA_URL'])
        # Import vector data if present
        if 'vector_data' in result:
            import_vector_json(company_id, result['vector_data'], config['VALERIA_URL'])

        # Generate encrypted link
        link = generate_custom_link(company_name, config['AES_KEY'])
        return jsonify({'status': 'started', 'job_id': job_id, 'link': link}), 200

    except TimeoutError as e:
        logger.error(f"Timeout: {e}")
        return jsonify({'status': 'failed', 'job_id': data.get('job_id', ''), 'error': f"Timeout: {e}"}), 504
    except Exception as e:
        logger.error(f"Unhandled error: {e}", exc_info=True)
        job = data.get('job_id') if 'data' in locals() else ''
        return jsonify({'status': 'failed', 'job_id': job, 'error': str(e)}), 500

def create_app(use_mocks: bool = False) -> Flask:
    global config, mock_webwalker
    config = load_config()
    if use_mocks:
        mock_webwalker = MockWebWalker()
        app.config['USE_MOCKS'] = True
    else:
        app.config['USE_MOCKS'] = False
    app.register_blueprint(api, url_prefix='/api')
    return app

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Flask microservice')
    parser.add_argument('--use-mocks', action='store_true', help='Use mock implementations')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind')
    args = parser.parse_args()

    app = create_app(use_mocks=args.use_mocks)
    app.run(host=args.host, port=args.port)
