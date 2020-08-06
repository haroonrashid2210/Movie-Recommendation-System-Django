import pandas as pd
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.base import TemplateView
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import csv
from main.top_movies import getTOPMovies

# Personal API key
api_key = 'c9aeb176ddbedf1360223c8457d2bfe1'
blank_poster_url = 'https://lh3.googleusercontent.com/proxy/wEDsSXD1LTIJ1mMLGbBKQMreCPZIiPEI0EtuBHJ2PklogRVLcAX99LIJvlt25b7-kfPXD5s46UVGa8kCWZnKSmYv2rM6q9Gr9c8YgqhOsjggwMlXW_UnMH0R-hkhqHNYztnS'


def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def login(request):
    return render(request, "accounts/login.html")


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'


def isMoviePresent(movie_name):
    file = open('/home/harry/PycharmProjects/djangoProject/main/movie_dataset.csv', 'r')
    reader = csv.reader(file)
    for row in reader:
        if row[18] == movie_name:
            return True
    return False


def getMovieDetail(movie_name):
    try:
        file = open('/home/harry/PycharmProjects/djangoProject/main/movie_dataset.csv', 'r')
        reader = csv.reader(file)
        movie_detail = []
        for row in reader:
            if row[18] == movie_name:
                movie_detail.append(row[4])
                movie_detail.append(movie_name)
                return movie_detail
    except:
        return movie_name


def getMoviePoster(movie_id):
    try:
        response = requests.get(
            'https://api.themoviedb.org/3/movie/' + movie_id + '?api_key=' + api_key + '&language=en-US')
        data = response.json()
        return 'https://image.tmdb.org/t/p/original/' + data['poster_path']
    except:
        return blank_poster_url


def SearchMovie(request):
    searched = request.POST.get('search_box')

    # if movie is not in dataset return a message
    if not isMoviePresent(searched):
        return render(request, 'base.html', {'message': 'Movie not found!'})

    f = open('/home/harry/PycharmProjects/djangoProject/main/movie_dataset.csv')
    df = pd.read_csv(f)
    features = ['keywords', 'cast', 'genres', 'director']

    def combine_features(row):
        return row['keywords'] + " " + row['cast'] + " " + row["genres"] + " " + row["director"]

    for feature in features:
        df[feature] = df[feature].fillna('')
    df["combined_features"] = df.apply(combine_features, axis=1)
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(df["combined_features"])
    cosine_sim = cosine_similarity(count_matrix)

    def get_title_from_index(index):
        return df[df.index == index]["title"].values[0]

    def get_index_from_title(title):
        return df[df.title == title]["index"].values[0]

    movie_user_likes = searched
    movie_index = get_index_from_title(movie_user_likes)
    similar_movies = list(enumerate(cosine_sim[movie_index]))
    sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)[1:]
    i = 0
    movie_list = []
    for element in sorted_similar_movies:
        movie_name = get_title_from_index(element[0])
        movie_detail = getMovieDetail(movie_name)
        poster = getMoviePoster(movie_detail[0])
        movie_list.append([movie_name, poster])
        i = i + 1
        if i >= 4:
            break

    return render(request, 'base.html', {'data': movie_list})


def imdbTOP(request):
    top_list = getTOPMovies()
    movie_list = []
    for element in top_list:
        movie_detail = getMovieDetail(element)
        poster = getMoviePoster(movie_detail[0])
        movie_list.append([element, poster])

    return render(request, 'base.html', {'data': movie_list})
