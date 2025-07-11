import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route('/api/status')
def status():
    return jsonify({"status": "healthy", "message": "API is running!"}), 200

@app.route("/api/test_db")
def test_db_connection():
    try:
        # This is the line that actually uses the connection.
        # We are asking Supabase to select all records from the 'users' table, but limit it to 5 just to be safe.
        response = supabase.table('users').select("*").limit(5).execute()
        
        return jsonify({
            "message": "Successfully connected to Supabase and queried the users table.",
            "data": response.data # shows a list of users.
        })
    except Exception as e:
        return jsonify({
            "message": "Failed to connect to or query the database.",
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)