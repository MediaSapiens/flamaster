from flamaster.app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(20), nullable=True)
    addresses = db.relationship('Address', lazy='dynamic',
                                backref=db.backref('user', lazy='joined'),
                                cascade="all, delete, delete-orphan")

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return "<User: %r>" % self.email

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sity = db.Column(db.String(25))
    street = db.Column(db.String(25))
    home = db.Column(db.String(20))
    apartment = db.Column(db.String(20), nullable=False)
    post_index = db.Column(db.String(20), nullable=False)

    def __init__(self, sity, street, home, apartment):
        self.sity = sity
        self.street = street
        self.home = home
        self.apartment = apartment

    def __repr__(self):
        return "<Address:('%s','%s', '%s')>" % (self.sity, self.street, self.home)

    def create(self):
        return ''

    def update(self):
        return ''

    def delete(self):
        return ''


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    users = db.relationship('User', lazy='dynamic',
                            backref=db.backref('role', lazy='joined'))
