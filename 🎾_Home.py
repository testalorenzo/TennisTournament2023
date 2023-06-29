import streamlit as st
from PIL import Image

image = Image.open('IMG-20201128-WA0007.jpg')

# Set up page
st.title('2023 AVIS AIDO Tennis Tournament')
st.image(image)

st.write('Benvenuto nel sito del torneo di tennis 2023 AVIS AIDO!')
st.write('Aggiungere testo, descrizione, etc. qui')