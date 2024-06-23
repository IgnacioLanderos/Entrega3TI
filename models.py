from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Message {self.data}>'
