from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import base64

# Create SQLAlchemy instance
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuration for SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy with the Flask app
    db.init_app(app)

    # Define the Message model
    class Message(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        data = db.Column(db.String, nullable=False)

        def __repr__(self):
            return f'<Message {self.data}>'

    # Create the database tables
    with app.app_context():
        db.create_all()

    # Route to handle Pub/Sub push messages
    @app.route('/pubsub/push', methods=['POST'])
    def pubsub_push_handler():
        try:
            # Obtain the message from the request body
            envelope = request.get_json()
            if not envelope:
                return 'Bad Request: no Pub/Sub message received', 400

            # Pub/Sub message
            pubsub_message = envelope.get('message')
            if not pubsub_message:
                return 'Bad Request: no Pub/Sub message received', 400

            # Get the message data
            message_data = pubsub_message.get('data')
            if message_data:
                # Decode base64 message
                decoded_message = base64.b64decode(message_data).decode('utf-8')
                print(f'Received message: {decoded_message}')

                # Save message to database
                message = Message(data=decoded_message)
                db.session.add(message)
                db.session.commit()

                # Confirm message received
                return jsonify(status='Message received'), 200
            else:
                print('No data in message')
                return 'Bad Request: no data in Pub/Sub message', 400

        except Exception as e:
            return f'Internal Server Error: {str(e)}', 500

    # Route to retrieve all messages from database
    @app.route('/messages', methods=['GET'])
    def get_messages():
        messages = Message.query.all()
        message_dicts = [message.to_dict() for message in messages]
        return jsonify(message_dicts), 200

    return app

# Entry point of the application
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080)
