from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(20))
    role = db.Column(db.Integer, db.ForeignKey('role.id'))
    addresses = db.relationship('Address', backref='user', lazy='dynamic')

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return "<User: %r>" % self.email


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    users = db.relationship('User', backref='roles', lazy='dynamic')
