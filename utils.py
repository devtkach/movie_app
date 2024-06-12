import requests
import random

OMDB_API_KEY = 'd186e5eb'

def fetch_random_movies():
    keywords = ['love', 'war', 'action', 'comedy', 'drama', 'fantasy', 'thriller', 'science', 'history', 'adventure']
    keyword = random.choice(keywords)
    url = f"http://www.omdbapi.com/?s={keyword}&type=movie&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data['Response'] == 'True':
        movies = data['Search']
        return random.sample(movies, min(len(movies), 10))
    else:
        return []

def fetch_movie_details(movie_id):
    url = f'http://www.omdbapi.com/?i={movie_id}&apikey={OMDB_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        movie_data = response.json()
        print(f"Fetched movie details: {movie_data}")  # Debug print
        if movie_data['Response'] == 'True':
            return movie_data
        else:
            print(f"Error fetching movie details: {movie_data['Error']}")  # Debug print
            return None
    else:
        print(f"Error fetching movie details: {response.status_code}")  # Debug print
        return None
