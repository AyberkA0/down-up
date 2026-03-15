from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin as fa
from firebase_admin import credentials, firestore
from datetime import datetime
import threading
import uuid

cred = credentials.Certificate("serviceAccountKey.json")
fa.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
lock = threading.Lock()

# student = 0, observer = 1

@app.route("/", methods=["GET"])
def ping():
    return jsonify({"status": "ok"}), 200

@app.route("/register_user", methods=["POST"])
def register_user():
    try:
        data = request.get_json(force=True)
        user_id = data.get("user_id") or str(uuid.uuid4())
        created_at = data.get("created_at") or datetime.utcnow().isoformat()
        role = data.get("role")

        print("Registering user:", user_id, created_at, role)

        if role not in [0, 1]:
            return jsonify({"error": "Invalid role. Must be 0 (student) or 1 (observer)."}), 400

        doc_ref = db.collection("users").document(user_id)

        with lock:
            if doc_ref.get().exists:
                return jsonify({"message": "already exists"}), 200

            doc_ref.set({
                "user_id": user_id,
                "created_at": created_at,
                "last_online": created_at,
                "role": role,
                "matched_ids": [],
                "actions": []
            })

        return jsonify({"message": "user registered", "user_id": user_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/delete_user", methods=["POST"])
def delete_user():
    try:
        data = request.get_json(force=True)
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        user_ref = db.collection("users").document(user_id)

        with lock:
            if not user_ref.get().exists:
                return jsonify({"error": "User not found"}), 404

            all_users = db.collection("users").stream()
            for doc in all_users:
                doc_data = doc.to_dict()
                matched_ids = doc_data.get("matched_ids", [])
                if user_id in matched_ids:
                    matched_ids.remove(user_id)
                    db.collection("users").document(doc.id).update({"matched_ids": matched_ids})

            user_ref.delete()

        return jsonify({"message": f"User {user_id} deleted and references removed"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/match", methods=["POST"])
def match_users():
    try:
        data = request.get_json(force=True)
        user_id_1 = data.get("observer_id")
        user_id_2 = data.get("student_id")

        if not user_id_1 or not user_id_2:
            return jsonify({"error": "observer_id and student_id required"}), 400

        if user_id_1 == user_id_2:
            return jsonify({"error": "Cannot match a user with themselves."}), 400

        user_ref_1 = db.collection("users").document(user_id_1)
        user_ref_2 = db.collection("users").document(user_id_2)

        with lock:
            doc1 = user_ref_1.get()
            doc2 = user_ref_2.get()

            if not doc1.exists or not doc2.exists:
                return jsonify({"error": "One or both users not found"}), 404

            user1_data = doc1.to_dict()
            user2_data = doc2.to_dict()

            if user2_data.get("role") != 0:
                return jsonify({"error": "student_id must be a student (role = 0)"}), 400

            matched_ids_1 = user1_data.get("matched_ids", [])
            matched_ids_2 = user2_data.get("matched_ids", [])

            updated = False

            if user_id_2 not in matched_ids_1:
                matched_ids_1.append(user_id_2)
                user_ref_1.update({"matched_ids": matched_ids_1})
                updated = True

            if user_id_2 not in matched_ids_2:
                matched_ids_2.append(user_id_2)
                user_ref_2.update({"matched_ids": matched_ids_2})
                updated = True

        if updated:
            return jsonify({"message": "matched successfully"}), 200
        else:
            return jsonify({"message": "already matched"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/set_data", methods=["POST"])
def set_data():
    try:
        data = request.get_json(force=True)
        user_id = data.get("user_id")
        data_key = data.get("data_key")
        data_value = data.get("data_value")

        if not user_id or not data_key or not data_value:
            return jsonify({"error": "user_id, data_key, and data_value are required"}), 400

        user_ref = db.collection("users").document(user_id)

        with lock:
            if not user_ref.get().exists:
                return jsonify({"error": "User not found"}), 404

            user_ref.update({data_key: data_value})

        return jsonify({"message": f"Data set for user {user_id}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_data", methods=["GET"])
def get_data():
    try:
        user_id = request.args.get("user_id")
        data_key = request.args.get("data_key")

        if not user_id or not data_key:
            return jsonify({"error": "user_id and data_key are required"}), 400

        user_ref = db.collection("users").document(user_id)

        with lock:
            doc = user_ref.get()

            if not doc.exists:
                return jsonify({"error": "User not found"}), 404

            user_data = doc.to_dict()
            data_value = user_data.get(data_key)

            if data_value is None:
                return jsonify({"error": f"Data key '{data_key}' not found"}), 404

        return jsonify({data_key: data_value}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/debug_log", methods=["POST"])
def debug_log():
    try:
        data = request.get_json(force=True)
        message = data.get("message", "")
        print(f"[DEBUG_LOG] {message}")
        return jsonify({"message": "Logged to console"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
