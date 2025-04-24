import pickle
import streamlit as st
import gdown
import requests

# Set layout BEFORE any other Streamlit command
st.set_page_config(layout="wide")

@st.cache_data
def load_pickle_from_gdrive(file_id):
    url = f"https://drive.google.com/uc?id={file_id}"
    output = f"/tmp/{file_id}.pkl"
    gdown.download(url, output, quiet=False)
    with open(output, 'rb') as f:
        return pickle.load(f)

# Your file IDs
MOVIE_LIST_ID = "1DIUzzePQPOyJuez8RiMxNLFl45x39SBb"
SIMILARITY_ID = "1ON73LlLx3y2p9nTmfQlN5heo03ft31pl"

# Load pickles
movies = load_pickle_from_gdrive(MOVIE_LIST_ID)
similarity = load_pickle_from_gdrive(SIMILARITY_ID)

# ---- Function to fetch movie poster ----
@st.cache_data
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = requests.get(url)
    if response.status_code != 200:
        return "https://via.placeholder.com/150"
    data = response.json()
    poster_path = data.get('poster_path')
    if not poster_path:
        return "https://via.placeholder.com/150"
    return "https://image.tmdb.org/t/p/w500/" + poster_path

# ---- Function to recommend movies ----
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters

# ---- Streamlit UI Setup ----
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center; color: #1f77b4;'>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Discover movies similar to your favorites</p>", unsafe_allow_html=True)

# ---- Movie Dropdown ----
movie_list = movies['title'].values
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_movie = st.selectbox("🎞️ Select a movie to get recommendations:", movie_list)

st.markdown("<br>", unsafe_allow_html=True)

# ---- Show Recommendations ----
if st.button('🎥 Show Recommendations'):
    with st.spinner('Finding similar movies...'):
        names, posters = recommend(selected_movie)
        st.write("")
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.image(posters[idx], use_container_width=True)
                st.markdown(
                    f"<h4 style='text-align: center; font-size:16px'>{names[idx]}</h4>",
                    unsafe_allow_html=True
                )
