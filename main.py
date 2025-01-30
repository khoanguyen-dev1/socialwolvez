from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

def fetch_key_value(url, api_key):
    if api_key != "phantruongdpzai":
        return jsonify({"error": "Invalid API key"}), 403
    
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
                print("Data received:", data)  # In ra dữ liệu để kiểm tra cấu trúc

                # Kiểm tra xem dữ liệu có phải là danh sách hay không
                if isinstance(data, list) and len(data) > 6:
                    extracted_url = data[5]
                    extracted_name = data[6]

                    return jsonify({'bypassed_url': extracted_url, 'name': extracted_name})
                else:
                    return jsonify({'error': 'Required data not found in the JSON structure.'}), 500

            except (json.JSONDecodeError, KeyError, IndexError) as e:
                return jsonify({'error': 'Failed to parse JSON data.', 'details': str(e)}), 500
        else:
            return jsonify({'error': 'Script tag with JSON data not found.'}), 404

    except requests.RequestException as e:
        return jsonify({'error': 'Failed to make request to the provided URL.', 'details': str(e)}), 500

@app.route('/bypass', methods=['GET'])
def socialwolvez():
    api_key = request.args.get("api_key")
    url = request.args.get('url')

    # Gọi hàm fetch_key_value và trả về giá trị
    return fetch_key_value(url, api_key)

if __name__ == '__main__':
    app.run(debug=True)
