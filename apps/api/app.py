from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

@app.route('/api/status')
def status():
    return jsonify({"status": "healthy", "message": "API is running!"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)