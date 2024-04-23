from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at).all()
        messages_dict = [message.to_dict() for message in messages]
        response = make_response(
            messages_dict,
            200
        )
        return response
    elif request.method == 'POST':
        data = request.json
         # new_message = Message(
        #     body=data['body'],
        #     username=data['username']
        # )
        new_message = Message(body=data.get('body'), username=data.get('username'))
        db.session.add(new_message)
        db.session.commit()
       
        message_dict = new_message.to_dict()
        response = make_response(
            message_dict,
            201
        )
        return response

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter(Message.id == id).first()
    if message == None:
       return jsonify({ "Error": "No message found in database."}, 404)
    else:
        if request.method == 'PATCH':
            data = request.json
            message.body = data.get('body', message.body)
            message.username = data.get('username', message.username)

            db.session.commit()
            
            message_dict = message.to_dict()
            response = make_response(
                message_dict,
                200
            )
            return response
        elif request.method == 'DELETE':
            if not message:
                return jsonify({'Error': 'Message not found'}, 404)
            db.session.delete(message)
            db.session.commit()
            response_body = {
                "message_deleted": True,
                "message": "Message deleted."
            }
            response = make_response(
                response_body, 200
            )
            return response

if __name__ == '__main__':
    app.run(port=5555)
