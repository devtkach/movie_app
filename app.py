from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from forms import RegistrationForm, LoginForm
from utils import fetch_random_movies, fetch_movie_details, OMDB_API_KEY
from werkzeug.security import generate_password_hash, check_password_hash
from models import WatchedMovie, User
import requests


def movie_already_watched(imdb_id):
    return WatchedMovie.query.filter_by(user_id=current_user.id, imdb_id=imdb_id).first() is not None


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    watched_movies = db.relationship('WatchedMovie', backref='watched_by', lazy=True)


class WatchedMovie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    imdb_id = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    director = db.Column(db.String(50), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    rating = db.Column(db.String(10), nullable=True)
    is_favorite = db.Column(db.Boolean, default=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    movies = fetch_random_movies()
    if current_user.is_authenticated:
        watched_titles = [movie.title for movie in current_user.watched_movies]
        excluded_titles = set(watched_titles)
        movies = [movie for movie in movies if movie['Title'] not in excluded_titles]
    return render_template('index.html', movies=movies)


@app.route("/search")
def search():
    query = request.args.get('query')
    print(f"Search query: {query}")  # Debugging print statement
    if query:
        response = requests.get(f'http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={query}&type=movie')
        data = response.json()
        print(f"OMDB API Response: {data}")  # Debugging print statement
        if data['Response'] == 'True':
            movies = data.get('Search', [])
        else:
            movies = []
            if data['Error'] == 'Too many results.':
                print(f"Too many results for query: {query}")  # Debugging print statement
                flash('Too many results. Please refine your search query.', 'warning')
            else:
                print(f"No movies found for query: {query}")  # Debugging print statement
    else:
        movies = []
        print("No query provided")  # Debugging print statement

    return render_template('search_results.html', movies=movies)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Username or email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            flash('Error in form submission. Please check your details and try again.', 'danger')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    else:
        if request.method == 'POST':
            flash('Error in form submission. Please check your details and try again.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/watched')
@login_required
def watched():
    watched_movies = current_user.watched_movies
    genres = {}
    ratings_over_decades = {}
    for movie in watched_movies:
        for genre in movie.genre.split(', '):
            genres[genre] = genres.get(genre, 0) + 1
        try:
            rating = float(movie.rating) if movie.rating and movie.rating != 'Unrated' else None
            if rating:
                decade = (int(movie.year) // 10) * 10
                if decade in ratings_over_decades:
                    ratings_over_decades[decade].append(rating)
                else:
                    ratings_over_decades[decade] = [rating]
        except ValueError:
            continue
    decades_list = sorted(ratings_over_decades.keys())
    avg_ratings = [sum(ratings_over_decades[decade]) / len(ratings_over_decades[decade]) for decade in decades_list]
    genres_keys = list(genres.keys())
    genres_values = list(genres.values())
    return render_template('watched.html', watched_movies=watched_movies, genres_keys=genres_keys,
                           genres_values=genres_values, ratings_decades=decades_list, avg_ratings=avg_ratings)


@app.route('/add_to_favorites/<string:movie_id>')
@login_required
def add_to_favorites(movie_id):
    movie = fetch_movie_details(movie_id)
    if not movie:
        flash('Error fetching movie details.', 'danger')
        return redirect(url_for('home'))

    watched_movie = WatchedMovie.query.filter_by(imdb_id=movie_id, user_id=current_user.id).first()
    if watched_movie:
        watched_movie.is_favorite = True
    else:
        watched_movie = WatchedMovie(
            user_id=current_user.id,
            imdb_id=movie_id,
            title=movie['Title'],
            genre=movie['Genre'],
            director=movie['Director'],
            year=movie['Year'],
            rating=movie.get('imdbRating', 'Unrated'),
            is_favorite=True
        )
        db.session.add(watched_movie)

    db.session.commit()
    flash('Movie added to favorites!', 'success')
    return redirect(url_for('home'))


@app.route('/add_to_watched/<string:movie_id>')
@login_required
def add_to_watched(movie_id):
    movie = fetch_movie_details(movie_id)
    if not movie:
        flash('Error fetching movie details.', 'danger')
        return redirect(url_for('home'))

    existing_watched = WatchedMovie.query.filter_by(imdb_id=movie_id, user_id=current_user.id).first()
    if existing_watched:
        flash('This movie is already in your watched list.', 'info')
    else:
        watched_movie = WatchedMovie(
            title=movie['Title'],
            genre=movie['Genre'],
            director=movie['Director'],
            year=movie['Year'],
            rating=movie.get('imdbRating', 'Unrated'),
            user_id=current_user.id,
            imdb_id=movie_id
        )
        db.session.add(watched_movie)
        db.session.commit()
        flash('Movie added to watched list!', 'success')
    return redirect(url_for('watched'))


if __name__ == '__main__':
    app.run(debug=True)
