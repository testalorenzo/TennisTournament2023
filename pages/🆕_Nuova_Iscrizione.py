import streamlit as st
from google.oauth2 import service_account
from shillelagh.backends.apsw.db import connect
import datetime
import mailtrap as mt

def create_ID(n):
    if n < 10:
        string = 'T0D0R' + str(n)
    elif n >= 10 and n < 100:
        string = 'T0D' + str(n)[0] + 'R' + str(n)[1]
    else:
        string = 'T' + str(n)[0] + 'D' + str(n)[1] + 'R' + str(n)[2]
    return string

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
st.title('Nuova Iscrizione')

name = st.text_input('Nome')
surname = st.text_input('Cognome')
email = st.text_input('E-Mail')
level = st.selectbox('Livello', ['Principiante', 'Intermedio', 'Avanzato'])
birth = st.date_input('Data di nascita', min_value=datetime.date(1950,1,1))
phone = st.text_input('Numero di telefono')

query = f'SELECT * FROM "{sheet_url}"'
rows = cursor.execute(query)
emails = [x[4] for x in rows]
n_subscriptions = len(emails)

if email in emails:
    st.error('E-mail già presente nel database')
else:
    if st.button('Invia iscrizione!'):
        ID = create_ID(n_subscriptions)
        next_match = 'TBD'
        query = f'INSERT INTO "{sheet_url}" (ID, Name, Surname, Birth, Email, Level, Phone, NextMatch) VALUES ("{ID}", "{name}", "{surname}", "{birth}", "{email}", "{level}", "{phone}", "{next_match}")'
        cursor.execute(query)
        connection.commit()

        text_to_send = mt.Mail(sender=mt.Address(email="no-reply@tdrtennis.it", name="no-reply"),
                               to=[mt.Address(email= email)],
                               subject="Iscrizione TDR Tennis",
                               text="Ciao " + name + ",\n\nGrazie per esserti iscritto a TDR Tennis!\n\n Questo è il tuo codice identificativo per accedere alla tua area personale: " + ID + "\n\nA presto,\n\nTDR Tennis",
                               category="Welcome")

        client = mt.MailtrapClient(token= st.secrets["private_token"])
        client.send(text_to_send)

        st.success("Iscrizione effettuata con successo. Riceverai una mail di conferma con il tuo codice identificativo all'indirizzo che hai specificato!")
        st.balloons()