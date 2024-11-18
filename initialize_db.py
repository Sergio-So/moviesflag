import sqlite3

def initialize_database():
    connection = sqlite3.connect("movies_cache.db")
    cursor = connection.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Movie (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        imdb_id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        year TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Country (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS Flag (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country_id INTEGER NOT NULL,
        flag_url TEXT NOT NULL,
        FOREIGN KEY (country_id) REFERENCES Country (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS MovieCountry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER NOT NULL,
        country_id INTEGER NOT NULL,
        FOREIGN KEY (movie_id) REFERENCES Movie (id) ON DELETE CASCADE,
        FOREIGN KEY (country_id) REFERENCES Country (id) ON DELETE CASCADE,
        UNIQUE (movie_id, country_id)
    );
    """)

    connection.commit()
    connection.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    initialize_database()
