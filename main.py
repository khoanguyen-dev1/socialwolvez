import logging
from flask import Flask, request, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
import os
import requests
import time
import re
import random

app = Flask(__name__)
CORS(app)
key_regex = r'let content = \("([^"]+)"\);'
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
port = int(os.getenv('PORT', 8080))

# Cấu hình logging
logger = logging.getLogger('api_usage')
logger.setLevel(logging.INFO)

log_file_path = '/tmp/api_usage.log'
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def get_client_ip():
    """Hàm để lấy địa chỉ IP của client, xem xét cả trường hợp đằng sau proxy."""
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/socialwolvez', methods=['GET'])
def socialwolvez():
    url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'Missing parameter: url'}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        script_tag = soup.find('script', {'id': '__NUXT_DATA__'})
        if script_tag and script_tag.string:
            try:
                data = json.loads(script_tag.string)
                
                extracted_url = data[5]
                extracted_name = data[6]

                if extracted_url and extracted_name:
                    return jsonify({'result': extracted_url, 'name': extracted_name})
                else:
                    return jsonify({'error': 'Required data not found in the JSON structure.'}), 500

            except (json.JSONDecodeError, KeyError, IndexError) as e:
                return jsonify({'error': 'Failed to parse JSON data.', 'details': str(e)}), 500
        else:
            return jsonify({'error': 'Script tag with JSON data not found.'}), 404

    except requests.RequestException as e:
        return jsonify({'error': 'Failed to make request to the provided URL.', 'details': str(e)}), 500
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Đảm bảo rằng debug=False trong môi trường sản xuất
    )
