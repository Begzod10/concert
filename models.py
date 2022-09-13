from app import Boolean, Integer, String, Column, ForeignKey, DateTime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
db = SQLAlchemy()


def db_setup(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db


class Venue(db.Model):
    __tablename__ = 'Venue'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    city = Column(String(120))
    state = Column(String(120))
    address = Column(String(120))
    phone = Column(String(120))
    image_link = Column(String(500))
    facebook_link = Column(String(120))
    seeking_talent = Column(Boolean, default=False)
    seeking_description = Column(String(500))
    website = Column(String(120))
    genres = Column(String(120))
    shows = db.relationship('Show', backref='Venue', lazy='dynamic')

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def short_response(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city
        }

    def info(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'genres': self.genres,
            'address': self.address,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'image_link': self.image_link,
            'seeking_description': self.seeking_description
        }
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    city = Column(String(120))
    state = Column(String(120))
    phone = Column(String(120))
    genres = Column(String(120))
    image_link = Column(String(500))
    facebook_link = Column(String(120))
    seeking_venue = Column(Boolean)
    seeking_description = Column(String(500))
    website = Column(String)
    shows = db.relationship('Show', backref='Artist', lazy=True)

    def info(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'genres': self.genres,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'image_link': self.image_link,
            'seeking_description': self.seeking_description
        }

    def short_response(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = "Show"
    id = Column(Integer, primary_key=True)
    venue_id = Column(Integer, ForeignKey(Venue.id), nullable=False)
    artist_id = Column(Integer, ForeignKey(Artist.id), nullable=False)
    start_time = Column(String, nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def info(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'start_time': self.start_time
        }

    def artist_info(self):
        return {
            'artist_id': self.venue_id,
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'start_time': self.start_time

        }

    def venue_info(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'venue_image_link': self.Venue.image_link,
            'start_time': self.start_time

        }
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
