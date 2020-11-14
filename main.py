from flask import Flask
from flask_restplus import Api, Resource
import json

"""Load JSON"""
with open("movies.json", "r", encoding="utf-8") as infile:
    movies_json = json.load(infile)

"""Define Flask app"""
flask_app = Flask(__name__)
app = Api(app=flask_app,
          version="1.0",
          title="VIA app",
          description="Demo app for via")

"""Define namespace"""
movies_name_space = app.namespace("movies", description='Get info about movies')


@movies_name_space.route("/")  # Define the route
class MoviesList(Resource):
    @app.doc(responses={200: 'OK'}, description="Get list of all movies")  # Documentation of route
    def get(self):  # GET method of REST
        movies_list = []
        for movie in movies_json:
            movies_list.append(movie["Title"])
        return movies_list


@movies_name_space.route("/<string:name>/director")  # Define the route
class Director(Resource):
    @app.doc(responses={200: 'OK', 400: 'Invalid Argument'}, description="Get name of director for movie")
    def get(self, name):
        for movie in movies_json:
            if movie["Title"] == name:
                director = movie["Director"]
                if director != "N/A":
                    return {"Director": movie["Director"]}
                else:
                    movies_name_space.abort(400, status="No director", statusCode="400")
        movies_name_space.abort(400, status="Movie doesn't exist", statusCode="400")


@movies_name_space.route("/<string:name>")
class AddMovie(Resource):
    @app.doc(responses={200: 'OK', 400: 'Invalid Argument'}, description="Create new movie")
    def put(self, name):
        for movie in movies_json:
            if movie["Title"] == name:
                movies_name_space.abort(400, status="Movie already exists", statusCode="400")
        movies_json.append({"Title": name})
        return {"Status": "OK"}


"""Run Flask app"""
flask_app.run()
