import re 
import streamlit as st
from google.oauth2 import service_account
from shillelagh.backends.apsw.db import connect
from PIL import Image

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """

def check_email(string):
    # Regular expression for validating an email
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    # pass the regular expression and the string into the fullmatch() method
    if re.fullmatch(regex, string):
        return True
    return False

payment_text = """
                Per pagare la tua quota di iscrizione, puoi inviarci un bonifico bancario rispettando le seguenti indicazioni:
                - IBAN: IT46U0538752470000042475325
                - Causale: Contributo a AVIS Torre de' Roveri per svolgimento torneo Tennis settembre 2023 

                Una volta ricevuto il tuo pagamento, lo processeremo entro 24 ore e ti invieremo una email di conferma. Per qualsiasi informazione, contattaci all'indirizzo e-mail hello@tdrtennis.it"""

image = Image.open('./pages/IMG-20201128-WA0008.jpg')

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/spreadsheets",],)

connection = connect(":memory:", adapter_kwargs={
            "gsheetsapi" : { 
            "service_account_info" : {
                "type" : st.secrets["gcp_service_account"]["type"],
                "project_id" : st.secrets["gcp_service_account"]["project_id"],
                "private_key_id" : st.secrets["gcp_service_account"]["private_key_id"],
                "private_key" : st.secrets["gcp_service_account"]["private_key"],
                "client_email" : st.secrets["gcp_service_account"]["client_email"],
                "client_id" : st.secrets["gcp_service_account"]["client_id"],
                "auth_uri" : st.secrets["gcp_service_account"]["auth_uri"],
                "token_uri" : st.secrets["gcp_service_account"]["token_uri"],
                "auth_provider_x509_cert_url" : st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url" : st.secrets["gcp_service_account"]["client_x509_cert_url"],
                }
            },
        })

cursor = connection.cursor()
sheet_url = st.secrets["private_gsheets_url"]

# Set up page
st.markdown(hide_menu_style, unsafe_allow_html=True)
st.title('Log In')
st.image(image)

with st.form("my_form"):
    ID = st.text_input('ID', '')
    email = st.text_input('E-Mail', '')
    submitted = st.form_submit_button("Log in!")

    if submitted:
        if check_email(email):
            rows = cursor.execute(f'SELECT * FROM "{sheet_url}"')
            rows = rows.fetchall()
            IDs = [x[0] for x in rows]
            emails = [x[4] for x in rows]
            if ID in IDs:
                index = IDs.index(ID)
            else:
                st.error("L'ID che hai inserito non combacia con quello che hai usato in fase di registrazione")
            if email != emails[index]:
                st.error("L'e-mail che hai inserito non combacia con quella che hai usato in fase di registrazione")
            else:
                st.write(f"ID: {ID}")
                st.write(f"Nome: {rows[index][1]}")
                st.write(f"Cognome: {rows[index][2]}")
                st.write(f"Data di nascita: {rows[index][3]}")
                st.write(f"Codice fiscale: {rows[index][10]}")
                st.write(f"E-mail: {email}")
                st.write(f"Livello: {rows[index][5]}")
                st.write(f"Telefono: {int(rows[index][6])}")
                st.write(f"Prossima partita: {rows[index][7]}")
                st.write(f"Stato pagamento: {rows[index][8]}")
                st.write(f"Date in cui sei disponibile a giocare: {rows[index][9]}")
                with st.expander("Hai sbagliato ad inserire i tuoi dati?"):
                    st.write("Contattaci a questo indirizzo: hello@tdrtennis.it. Ti risponderemo entro qualche ora!")
                if rows[index][8] != 'Paid':
                    with st.expander("Quanto costa iscriversi?"):
                        st.write("Per i cittadini e le cittadine residenti nel comune di Torre de' Roveri, la quota di iscrizione è di 15 Euro. Per coloro che non risiedono a Torre de' Roveri, la quota è di 20 Euro")
                    with st.expander("Come effettuare il pagamento?"):
                        st.write(payment_text)
        else:
            st.error('Email non valida')