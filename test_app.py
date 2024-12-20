import unittest
from unittest.mock import patch
from app import app, init_db

class MovieWithFlagAppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Se ejecuta una sola vez para toda la clase de pruebas."""
        cls.client = app.test_client()
        app.config['TESTING'] = True
        init_db()

    def notest_integration(self):
        response = self.client.get("/api/movies?filter=superman")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 10)
        for movie in data:
            self.assertIsNotNone(movie["title"])
            self.assertIsNotNone(movie["year"])
            self.assertIsNotNone(movie["countries"])

    @patch("app.searchfilms")
    @patch("app.getmoviedetails")
    def test_movie_flag_get(self, mock_getmoviedetails, mock_searchfilms):
        mock_getmoviedetails.return_value = {
            "Title": "Superman II",
            "Year": "1980",
            "Country": "United States, United Kingdom, Canada, France",
        }
        mock_searchfilms.return_value = [
            {
                "Title": "Superman II",
                "Year": "1980",
                "imdbID": "tt0081573"
            }
        ]

        response = self.client.get("/api/movies?filter=superman")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        for movie in data:
            self.assertEqual(movie["title"], "Superman II")
            self.assertEqual(movie["year"], "1980")
            self.assertEqual(len(movie["countries"]), 4)
            self.assertEqual(movie["countries"][0]["name"], "United States")
            self.assertEqual(movie["countries"][1]["name"], "United Kingdom")
            self.assertEqual(movie["countries"][2]["name"], "Canada")
            self.assertEqual(movie["countries"][3]["name"], "France")
            self.assertEqual(movie["countries"][0]["flag"], "https://flagcdn.com/us.svg")
            self.assertEqual(movie["countries"][1]["flag"], "https://flagcdn.com/gb.svg")
            self.assertEqual(movie["countries"][2]["flag"], "https://flagcdn.com/ca.svg")
            self.assertEqual(movie["countries"][3]["flag"], "https://flagcdn.com/fr.svg")

    @patch("app.get_country_flag")
    @patch("app.getmoviedetails")
    @patch("app.searchfilms")
    def test_movie_searchapi(self, mock_searchfilms, mock_getmoviedetails, mock_get_country_flag):
        mock_searchfilms.return_value = [
            {"Title": f"Superman {i}", "Year": "1980", "imdbID": f"tt008157{i}"} for i in range(10)
        ]
        mock_getmoviedetails.return_value = {
            "Title": "Superman II",
            "Year": "1980",
            "Country": "United States, United Kingdom, Canada, France"
        }
        mock_get_country_flag.side_effect = lambda country: {
            "United States": "https://flagcdn.com/us.svg",
            "United Kingdom": "https://flagcdn.com/gb.svg",
            "Canada": "https://flagcdn.com/ca.svg",
            "France": "https://flagcdn.com/fr.svg",
        }.get(country, "https://flagcdn.com/unknown.svg")

        response = self.client.get("/api/movies?filter=superman")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 10)
        for movie in data:
            self.assertEqual(movie["title"], "Superman II")
            self.assertEqual(movie["year"], "1980")
            self.assertEqual(len(movie["countries"]), 4)
            self.assertEqual(movie["countries"][0]["name"], "United States")
            self.assertEqual(movie["countries"][0]["flag"], "https://flagcdn.com/us.svg")
            self.assertEqual(movie["countries"][1]["name"], "United Kingdom")
            self.assertEqual(movie["countries"][1]["flag"], "https://flagcdn.com/gb.svg")
            self.assertEqual(movie["countries"][2]["name"], "Canada")
            self.assertEqual(movie["countries"][2]["flag"], "https://flagcdn.com/ca.svg")
            self.assertEqual(movie["countries"][3]["name"], "France")
            self.assertEqual(movie["countries"][3]["flag"], "https://flagcdn.com/fr.svg")


if __name__ == "__main__":
    unittest.main()
