import pickle
import streamlit as st
import requests
import os

# --- DOWNLOAD LARGE FILE IF NOT PRESENT ---
def download_file(url, filename):
    if not os.path.exists(filename):
        with st.spinner(f"Downloading {filename}..."):
            response = requests.get(url)
            with open(filename, 'wb') as f:
                f.write(response.content)
            st.success(f"{filename} downloaded successfully.")

# Replace this with your own public URL (Google Drive with direct link, Dropbox, etc.)
SIMILARITY_FILE_URL = "https://drive.google.com/file/d/1w68d-svWF2kXzB6gkemPPNv_2E0_PsAB/view?usp=drive_link"
SIMILARITY_FILE_NAME = "similarity.pkl"

download_file(SIMILARITY_FILE_URL, SIMILARITY_FILE_NAME)

# --- LOAD DATA ---
movies = pickle.load(open('movie_list.pkl', 'rb'))

with open(SIMILARITY_FILE_NAME, 'rb') as f:
    similarity = pickle.load(f)

# --- FETCH POSTER ---
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url, timeout=5)
        data.raise_for_status()
        poster_path = data.json().get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return None
    except:
        return None

# --- RECOMMEND MOVIES ---
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))
    return recommended_movie_names, recommended_movie_posters

# --- STREAMLIT UI ---
st.header('Movie Recommender System')

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button('Show Recommendation'):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            if posters[i]:
                st.image(posters[i])
            else:
                st.warning("Poster unavailable")
