from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)
apikey = "387c9432"

def searchfilms(search_text):
    url = f"https://www.omdbapi.com/?s={search_text}&apikey={apikey}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("OMDB API Response:", data)
        if "Search" in data:
            return data["Search"]
        elif data.get("Response") == "True":
            return [data]
        else:
            print("No movies found in search results.")
            return None
    else:
        print("Failed to retrieve search results.")
        return None



def getmoviedetails(movie):
    url = f"https://www.omdbapi.com/?i={movie['imdbID']}&apikey={apikey}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve details for movie ID: {movie['imdbID']}")
        return None

def get_country_flag(fullname):
    url = f"https://restcountries.com/v3.1/name/{fullname}?fullText=true"
    response = requests.get(url)
    if response.status_code == 200:
        country_data = response.json()
        if country_data:
            return country_data[0].get("flags", {}).get("svg", None)
    print(f"Failed to retrieve flag for country: {fullname}")
    return None

def merge_data_with_flags(filter):
    filmssearch = searchfilms(filter)
    if filmssearch is None:
        print("No movies found for the given filter.")
        return []
    
    moviesdetailswithflags = []
    for movie in filmssearch:
        moviedetails = getmoviedetails(movie)
        if moviedetails and "Country" in moviedetails:
            countriesNames = moviedetails["Country"].split(",")
            countries = []
            for country in countriesNames:
                countrywithflag = {
                    "name": country.strip(),
                    "flag": get_country_flag(country.strip())
                }
                countries.append(countrywithflag)
            moviewithflags = {
                "title": moviedetails["Title"],
                "year": moviedetails["Year"],
                "countries": countries
            }
            moviesdetailswithflags.append(moviewithflags)
    print("Movies with Flags:", moviesdetailswithflags)  
    return moviesdetailswithflags


@app.route("/")
def index():
    filter = request.args.get("filter", "").upper()
    print("Filter received:", filter)  
    movies = merge_data_with_flags(filter)
    return render_template("index.html", movies=movies)


@app.route("/api/movies")
def api_movies():
    filter = request.args.get("filter", "")
    return jsonify(merge_data_with_flags(filter))

if __name__ == "__main__":
    app.run(debug=True)
