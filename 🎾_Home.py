import streamlit as st
from PIL import Image

st.set_page_config(page_title="Home - TDRTennis 2023", page_icon="🎾")

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """

image = Image.open('./pages/20230711_094921_0000.png')
video_file = open('video_home.mp4', 'rb')
video_bytes = video_file.read()

main_text = """
            Benvenuti nel sito del torneo di tennis 2023 AVIS AIDO!

            A Settembre 2023, presso il Centro Sportivo di Torre de' Roveri - FranVi Bar, verrà organizzato, insieme alle associazioni AVIS e AIDO locali, il secondo Torneo di Tennis AVIS-AIDO.
            
            Il torneo si svolgerà dal 01 Settembre al 17 Settembre, con tabellone e format che verranno comunicati successivamente, in relazione al numero di iscritti.

            Le partite si svolgeranno dal Lunedì al Venerdì a partire dalle ore 19, e il Sabato e la Domenica durante l’intera giornata.

            Vi chiediamo gentilmente di iscrivervi a [questo link](https://tdrtennis.streamlit.app/Nuova_Iscrizione), selezionando i giorni in cui sarete disponibili per svolgere le partite.

            Una volta iscritti, riceverete presso la e-mail indicata il vostro ID personale, che vi servirà per rimanere aggiornati su tabellone e prossimi match! 🎾 

            Per essere ufficialmente iscritti vi servirà, oltre alla conferma della registrazione che riceverete via e-mail, anche la conferma di avvenuto pagamento (maggiori informazioni nell’Area Riservata, che trovate a [questo link](https://tdrtennis.streamlit.app/Log_In))
            
            Per qualsiasi informazione ci potete contattare alla e-mail: hello@tdrtennis.it
            """

# Set up page
st.markdown(hide_menu_style, unsafe_allow_html=True)
st.title('2023 AVIS AIDO Tennis Tournament')
st.video(video_bytes, start_time=0)

st.markdown(main_text)

st.sidebar.image(image, use_column_width=True)
