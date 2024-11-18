import os
from flask import Flask, render_template, request, jsonify
import requests
import sqlite3

app = Flask(__name__)
apikey = "387c9432"

# Eliminar el archivo de base de datos si existe
if os.path.exists("movies_cache.db"):
    os.remove("movies_cache.db")
    print("Archivo movies_cache.db eliminado.")
else:
    print("El archivo movies_cache.db no existe.")

# Inicialización de la base de datos
def init_db():
    connection = sqlite3.connect("movies_cache.db")
    cursor = connection.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Movie (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imdb_id TEXT UNIQUE,
            title TEXT,
            year TEXT
        );
        CREATE TABLE IF NOT EXISTS Country (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        );
        CREATE TABLE IF NOT EXISTS Flag (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            flag_url TEXT,
            FOREIGN KEY (country_id) REFERENCES Country (id)
        );
        CREATE TABLE IF NOT EXISTS MovieCountry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER,
            country_id INTEGER,
            FOREIGN KEY (movie_id) REFERENCES Movie (id),
            FOREIGN KEY (country_id) REFERENCES Country (id)
        );
    """)
    connection.commit()
    connection.close()

def searchfilms(search_text):
    url = f"https://www.omdbapi.com/?s={search_text}&apikey={apikey}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "Search" in data:
            return data["Search"]
        elif data.get("Response") == "True":
            return [data]
    return []

def getmoviedetails(movie):
    url = f"https://www.omdbapi.com/?i={movie['imdbID']}&apikey={apikey}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_country_flag(fullname):
    url = f"https://restcountries.com/v3.1/name/{fullname}?fullText=true"
    response = requests.get(url)
    if response.status_code == 200:
        country_data = response.json()
        if country_data:
            return country_data[0].get("flags", {}).get("svg", None)
    return None

def save_movie_to_db(imdb_id, title, year):
    connection = sqlite3.connect("movies_cache.db")
    cursor = connection.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO Movie (imdb_id, title, year) VALUES (?, ?, ?);",
        (imdb_id, title, year)
    )
    connection.commit()
    connection.close()

def merge_data_with_flags(filter):
    filmssearch = searchfilms(filter)
    if not isinstance(filmssearch, list):  # Validación del resultado de searchfilms
        print("Expected list from searchfilms, but got:", type(filmssearch))
        return []

    moviesdetailswithflags = []
    for movie in filmssearch:
        if not isinstance(movie, dict):  # Validación de tipo en cada película
            print("Expected dict for movie, but got:", type(movie))
            continue

        moviedetails = getmoviedetails(movie)
        if moviedetails and "Country" in moviedetails:
            countriesNames = moviedetails["Country"].split(",")
            countries = []
            for country in countriesNames:
                country_name = country.strip()
                country_flag = get_country_flag(country_name)
                countries.append({
                    "name": country_name,
                    "flag": country_flag
                })

            moviewithflags = {
                "title": moviedetails["Title"],
                "year": moviedetails["Year"],
                "countries": countries
            }
            moviesdetailswithflags.append(moviewithflags)

            # Guardar en la base de datos
            save_movie_to_db(movie["imdbID"], moviedetails["Title"], moviedetails["Year"])

    return moviesdetailswithflags

@app.route("/")
def index():
    filter = request.args.get("filter", "").upper()
    movies = merge_data_with_flags(filter)
    return render_template("index.html", movies=movies)

@app.route("/api/movies")
def api_movies():
    filter = request.args.get("filter", "")
    return jsonify(merge_data_with_flags(filter))

if __name__ == "__main__":
    init_db()  # Inicializar la base de datos al inicio
    app.run(debug=True)
