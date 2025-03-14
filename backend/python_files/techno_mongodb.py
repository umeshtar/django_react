from backend.settings import mongo_db

movies = mongo_db.get_collection("movies")

# Query for a movie that has the title 'Back to the Future'
query = {"title": "Back to the Future"}
movie = movies.find_one(query)

print(movie)

# client.close()
