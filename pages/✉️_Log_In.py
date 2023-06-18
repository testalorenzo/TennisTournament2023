import re 
import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect

def check_email(string):
    # Regular expression for validating an email
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    # pass the regular expression and the string into the fullmatch() method
    if re.fullmatch(regex, string):
        return True
    return False

# Perform SQL query on the Google Sheet
# Uses st.cache_data to only rerun when the query changes or after 10 min.
#@st.cache_data(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

# Set up page
st.title('Log In')

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)
sheet_url = st.secrets["private_gsheets_url"]

st.write('Inserisci qui i tuoi dati per accedere alla tua area personale')

ID = st.text_input('ID', '')
email = st.text_input('E-Mail', '')

if st.button('Log In'):
    if check_email(email):
        rows = run_query(f'SELECT * FROM "{sheet_url}"')
        IDs = [x[0] for x in rows]
        emails = [x[4] for x in rows]
        if ID in IDs:
            index = IDs.index(ID)
        if email != emails[index]:
            st.error("L'e-mail che hai inserito non combacia con quella che hai usato in fase di registrazione")
        else:
            st.write(f"ID: {ID}")
            st.write(f"Nome: {rows[index][1]}")
            st.write(f"Cognome: {rows[index][2]}")
            st.write(f"Data di nascita: {rows[index][3]}")
            st.write(f"E-mail: {email}")
            st.write(f"Livello: {rows[index][5]}")
            st.write(f"Telefono: {int(rows[index][6])}")
            st.write(f"Prossima partita: {rows[index][7]}")
    else:
        st.error('Email non valida')