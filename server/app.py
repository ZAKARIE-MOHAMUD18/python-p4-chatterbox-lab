#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

from models import db, Message

# ------------------------------------------------------------
# APP CONFIG
# ------------------------------------------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)


# ------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------

# GET /messages — return all messages ordered by created_at ascending
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([m.to_dict() for m in messages]), 200


# POST /messages — create a new message
@app.route('/messages', methods=['POST'])
def post_message():
    data = request.get_json()

    if not data or 'body' not in data or 'username' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    try:
        new_message = Message(body=data['body'], username=data['username'])
        db.session.add(new_message)
        db.session.commit()
        return jsonify(new_message.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Database error'}), 500


# PATCH /messages/<int:id> — update message body
@app.route('/messages/<int:id>', methods=['PATCH'])
def patch_message(id):
    message = db.session.get(Message, id)

    if not message:
        return jsonify({'error': 'Message not found'}), 404

    data = request.get_json()
    if 'body' in data:
        message.body = data['body']
    db.session.commit()

    return jsonify(message.to_dict()), 200


# DELETE /messages/<int:id> — delete a message
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = db.session.get(Message, id)

    if not message:
        return jsonify({'error': 'Message not found'}), 404

    db.session.delete(message)
    db.session.commit()
    return '', 204


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
if __name__ == '__main__':
    app.run(port=5555, debug=True)
