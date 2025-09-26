from flask import Blueprint, jsonify
from ..extensions import supabase

core_bp = Blueprint("core", __name__)

@core_bp.route('/api/status')
def status():
    return jsonify({"status": "healthy", "message": "API is running!"}), 200

@core_bp.route("/api/test_db")
def test_db_connection():
    try:
        # Try to ask Supabase to select all records from the 'users' table and limit it to 5 just to be safe.
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