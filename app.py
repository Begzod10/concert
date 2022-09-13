# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask_moment import Moment
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from sqlalchemy import Integer, Boolean, String, Column, ForeignKey, DateTime
from sqlalchemy.exc import SQLAlchemyError
from forms import *
from models import db_setup, Venue, Show, Artist

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = db_setup(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='full'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "d, y H:m"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
    venue = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
    venue_state_city = ''
    data = []
    for ven in venue:
        upcoming_show = ven.shows.filter(Show.start_time > current_time).all()
        if venue_state_city == ven.city + ven.state:
            data[len(data) - 1]["venues"].append({
                "id": ven.id,
                "name": ven.name,
                "num_upcoming_shows": len(upcoming_show)
            })
        else:
            data.append({
                "city": ven.city,
                "state": ven.state,
                "venues": [{
                    "id": ven.id,
                    "name": ven.name,
                    "num_upcoming_shows": len(upcoming_show)
                }]
            })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    venue_response = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%'))
    venue_list = list(map(Venue.short_response, venue_response))
    response = {
        'count': len(venue_list),
        'data': venue_list
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    show = Show.query.first()
    venue_query = Venue.query.get(venue_id)
    if venue_query:
        venues_info = Venue.info(venue_query)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_shows_querying = Show.query.options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id).filter(
            Show.start_time > current_time).all()
        new_show = list(map(Show.artist_info, new_shows_querying))
        venues_info['upcoming_shows'] = new_show
        venues_info['upcoming_shows_count'] = len(new_show)
        old_shows_querying = Show.query.options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id).filter(
            Show.start_time <= current_time).all()
        old_shows = list(map(Show.artist_info, old_shows_querying))
        venues_info['past_shows'] = old_shows
        venues_info['past_shows_count'] = len(old_shows)
        return render_template('pages/show_venue.html', venue=venues_info, show=show)
    return render_template('errors/404.html')


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    seeking_talent = False
    talent = request.form.get('seeking_talent')
    if talent == "on":
        seeking_talent = True
    elif talent == "off":
        seeking_talent = False
    try:
        new_venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            image_link=request.form['image_link'],
            facebook_link=request.form['facebook_link'],
            website=request.form['website'],
            genres=request.form.getlist('genres'),
            seeking_talent=seeking_talent,
            seeking_description=request.form['seeking_description']
        )
        new_venue.insert()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except SQLAlchemyError:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/delete_venue/<int:venue_id>')
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        del_venue = Venue.query.filter_by(id=venue_id).first()
        del_venue.delete()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    return render_template('pages/artists.html', artists=Artist.query.order_by('id').all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    artist_response = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%'))
    artist_list = list(map(Artist.short_response, artist_response))
    response = {
        'count': len(artist_list),
        'data': artist_list
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist_query = Artist.query.get(artist_id)
    if artist_query:
        artist_info = Artist.info(artist_query)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_shows_info = Show.query.options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(
            Show.start_time > current_time).all()
        new_shows_list = list(map(Show.artist_info, new_shows_info))
        artist_info['upcoming_shows'] = new_shows_list
        artist_info['upcoming_shows_count'] = len(new_shows_list)
        old_shows_info = Show.query.options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(
            Show.start_time <= current_time).all()
        old_shows_list = list(map(Show.artist_info, old_shows_info))
        artist_info['past_shows'] = old_shows_list
        artist_info['past_shows_count'] = len(old_shows_list)
        return render_template('pages/show_artist.html', artist=artist_info, show=Show.query.first())


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artis_query = Artist.query.get(artist_id)
    if artis_query:
        artist_info = Artist.info(artis_query)
        form.name.data = artist_info['name']
        form.genres.data = artist_info['genres']
        form.state.data = artist_info['state']
        form.city.data = artist_info['city']
        form.facebook_link.data = artist_info['facebook_link']
        form.image_link.data = artist_info['image_link']
        form.phone.data = artist_info['phone']
        form.website.data = artist_info['website']
        form.seeking_venue.data = artist_info['seeking_venue']
        form.seeking_description.data = artist_info['seeking_description']
        # TODO: populate form with fields from artist with ID <artist_id>
        return render_template('forms/edit_artist.html', form=form, artist=artist_info)
    return render_template('errors/404.html')


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist_query = Artist.query.get(artist_id)

    seeking_venue = False
    venue = request.form.get('seeking_venue')
    if venue == "off":
        seeking_venue = False
    elif venue == "on":
        seeking_venue = True
    setattr(artist_query, 'name', request.form['name'])
    setattr(artist_query, 'website', request.form['website'])
    setattr(artist_query, 'facebook_link', request.form['facebook_link'])
    setattr(artist_query, 'image_link', request.form['image_link'])
    setattr(artist_query, 'seeking_venue', seeking_venue)
    setattr(artist_query, 'seeking_description', request.form['seeking_description'])
    setattr(artist_query, 'phone', request.form['phone'])
    setattr(artist_query, 'state', request.form['state'])
    setattr(artist_query, 'city', request.form['city'])
    setattr(artist_query, 'genres', request.form['genres'])
    Venue.update(artist_query)
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue_query = Venue.query.get(venue_id)
    if venue_query:
        venue_info = Venue.info(venue_query)
        form.name.data = venue_info['name']
        form.genres.data = venue_info['genres']
        form.address.data = venue_info['address']
        form.state.data = venue_info['state']
        form.city.data = venue_info['city']
        form.facebook_link.data = venue_info['facebook_link']
        form.image_link.data = venue_info['image_link']
        form.phone.data = venue_info['phone']
        form.website.data = venue_info['website']
        form.seeking_talent.data = venue_info['seeking_talent']
        form.seeking_description.data = venue_info['seeking_description']
        # TODO: populate form with values from venue with ID <venue_id>
        return render_template('forms/edit_venue.html', form=form, venue=venue_info)
    return render_template('errors/404.html')


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    venue_query = Venue.query.get(venue_id)

    seeking_talent = False
    talent = request.form.get('seeking_talent')
    if talent == "off":
        seeking_talent = False
    elif talent == "on":
        seeking_talent = True
    setattr(venue_query, 'name', request.form['name'])
    setattr(venue_query, 'website', request.form['website'])
    setattr(venue_query, 'facebook_link', request.form['facebook_link'])
    setattr(venue_query, 'image_link', request.form['image_link'])
    setattr(venue_query, 'seeking_talent', seeking_talent)
    setattr(venue_query, 'seeking_description', request.form['seeking_description'])
    setattr(venue_query, 'phone', request.form['phone'])
    setattr(venue_query, 'state', request.form['state'])
    setattr(venue_query, 'city', request.form['city'])
    setattr(venue_query, 'genres', request.form['genres'])
    setattr(venue_query, 'address', request.form['address'])
    Venue.update(venue_query)
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    seeking_venue = False
    venue = request.form.get('seeking_venue')
    if venue == "on":
        seeking_venue = True
    elif venue == "off":
        seeking_venue = False
    try:
        artist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            genres=request.form.getlist('genres'),
            image_link=request.form['image_link'],
            seeking_venue=seeking_venue,
            website=request.form['website'],
            facebook_link=request.form['facebook_link'],
            seeking_description=request.form['seeking_description']
        )
        artist.insert()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except SQLAlchemyError:

        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')


@app.route('/delete_artist/<int:artist_id>')
def delete_artist(artist_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        del_venue = Artist.query.filter_by(id=artist_id).first()
        del_venue.delete()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    show_info = Show.query.options(db.joinedload(Show.Venue), db.joinedload(Show.Artist)).all()
    data = list(map(Show.info, show_info))

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    show = Show(
        venue_id=request.form['venue_id'],
        artist_id=request.form['artist_id'],
        start_time=request.form['start_time']
    )
    show.insert()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
