import streamlit as st
from PIL import Image

st.set_page_config(page_title="Gironi e Regolamento - TDRTennis 2023", page_icon="📚")

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """

st.markdown(hide_menu_style, unsafe_allow_html=True)
st.title('Gironi e Regolamento')

r1 = Image.open('./pages/Regolamento pag 1.png')
r2 = Image.open('./pages/Regolamento pag 2.png')

g1 = Image.open('./pages/Girone A.png')
g2 = Image.open('./pages/Girone B.png')
g3 = Image.open('./pages/Girone C.png')
g4 = Image.open('./pages/Girone D.png')
g5 = Image.open('./pages/Girone E.png')
g6 = Image.open('./pages/Girone F.png')
g7 = Image.open('./pages/Girone G.png')
g8 = Image.open('./pages/Girone H.png')

col1, col2 = st.columns(2)

with col1:
    st.image(r1)
    st.image(g1)
    st.image(g3)
    st.image(g5)
    st.image(g7)

with col2:
    st.image(r2)
    st.image(g2)
    st.image(g4)
    st.image(g6)
    st.image(g8)
    