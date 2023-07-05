import streamlit as st
from google.oauth2 import service_account
from shillelagh.backends.apsw.db import connect
import datetime
import mailtrap as mt
from PIL import Image

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """

def create_ID(n):
    if n < 10:
        string = 'T0D0R' + str(n)
    elif n >= 10 and n < 100:
        string = 'T0D' + str(n)[0] + 'R' + str(n)[1]
    else:
        string = 'T' + str(n)[0] + 'D' + str(n)[1] + 'R' + str(n)[2]
    return string

privacy_text = """
INFORMATIVA TRATTAMENTO DEI DATI PERSONALI
(ART. 13 E 14 REG. UE 2016/679)

Ai fini previsti dal Regolamento Ue n. 2016/679 relativo alla protezione delle persone fisiche con riguardo al trattamento dei dati personali, La informiamo che il trattamento dei dati personali da Lei forniti ed acquisiti da AVIS TORRE DE' ROVERI, saranno oggetto di trattamento nel rispetto della normativa prevista dal premesso Regolamento nel rispetto dei diritti ed obblighi conseguenti e che:

a) FINALITA’ DEL TRATTAMENTO – il trattamento è finalizzato: 1) alla corretta iscrizione, partecipazione e gestione degli eventi sportivi da lei prescelti, comprese tutte le attività inerenti gli obblighi di sicurezza, ed alla successiva compilazione e pubblicazione (limitatamente a nome, cognome) delle relative classifiche; 2) utilizzo dei suoi dati personale di contatto (Nome, Cognome ed indirizzo email) per inviarle informazioni dell’evento.

b) MODALITA’ DEL TRATTAMENTO DEI DATI PERSONALI – Il trattamento è realizzato attraverso operazioni, effettuate con o senza l’ausilio di strumenti elettronici e consiste nella raccolta, registrazione, organizzazione conservazione, consultazione, elaborazione, modificazione, selezione, estrazione, raffronto utilizzo interconnessione, blocco, comunicazione, cancellazione, e distruzione dei dati. Il trattamento è svolto dal titolare e dagli incaricati espressamente autorizzati dal titolare.

c) CONFERIMENTO DEI DATI E RIFIUTO – Il conferimento dei dati personali comuni e sensibili è obbligatorio e necessario ai fini dello svolgimento delle attività di cui al punto a), n. 1 ed il rifiuto da parte dell’interessato di conferire i dati personali comporta l’impossibilità di adempiere all’attività di cui al punto a) n. 1 e 2.

d) COMUNICAZIONE DEI DATI – I dati personali possono venire a conoscenza esclusivamente degli incaricati del trattamento e possono essere comunicati per le finalità di cui al punto a), n. 1, a collaboratori esterni e in generale a tutti i soggetti ai quali la comunicazione è necessaria per il corretto espletamento le finalità di cui al punto a), n. 1, tra cui collaboratori esterni e in generale a tutti i soggetti ai quali la comunicazione è necessaria per il corretto espletamento le finalità di cui al punto a). I dati personali non sono soggetti a diffusione tranne che per quel che riguarda nome e cognome che saranno contenuti nelle classifiche degli eventi sportivi cui partecipa l’interessato e che saranno pubblicati sul sito internet dell' evento e sulle pagine social di AVIS Torre de' Roveri.

f) CONSERVAZIONE DEI DATI – I dati sono conservati per il periodo necessario all’espletamento dell’attività e comunque non superiore a dieci anni.

g) TITOLARE DEL TRATTAMENTO – Il titolare del trattamento è AVIS TORRE DE' ROVERI. con sede in Via Papa Giovanni XXIII, 2, 24060 Torre de' Roveri (BG), avis.torrederoveri@gmail.com

h) DIRITTI DELL’INTERESSATO – L’interessato ha diritto:
- all’accesso, rettifica, cancellazione, limitazione e opposizione al trattamento dei dati;
- ad ottenere senza impedimenti dai titolari del trattamento i dati in un formato strutturato di uso comune e leggibile da dispositivo automatico per trasmetterli ad un altro titolare del trattamento;
- a revocare il consenso al trattamento, senza pregiudizio per la liceità del trattamento basata sul consenso acquisito prima della revoca;           •  il diritto di proporre reclamo ad una autorità di controllo (Garante per la protezione dei dati personali) o autorità giudiziaria.

L’esercizio dei premessi diritti può essere esercitato mediante comunicazione scritta da inviare a mezzo pec all’indirizzo torrederoveri@pec.avisbergamo.it 
"""

opening_text = """
               Per procedere con l’iscrizione ti chiediamo di compilare le informazioni richieste di seguito per poter organizzare al meglio le giornate del torneo! 
               
               La quota di iscrizione - che puoi pagare *dopo* aver effettuato l'iscrizione grazie alle informazioni che troverai nella tua Area Personale - è di 15€ e comprende, oltre alla partecipazione al torneo, anche dei gadget e un buono da spendere presso il Centro Sportivo. 
               """

image = Image.open('./pages/IMG-20201128-WA0004.jpg')

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
st.title('Nuova Iscrizione')
st.image(image)
st.markdown(opening_text)

availability_list = [str(x) + "/09/2023" for x in range(1,18)]

with st.form("my_form"):
    name = st.text_input('Nome')
    surname = st.text_input('Cognome')
    email = st.text_input('E-Mail')
    level = st.selectbox('Livello', ['Principiante', 'Intermedio', 'Avanzato'])
    birth = st.date_input('Data di nascita', min_value=datetime.date(1950,1,1))
    fiscal_code = st.text_input('Codice Fiscale')
    phone = st.text_input('Numero di telefono')
    availability = st.multiselect('In quali date saresti disponibile per giocare?', availability_list)
    agree = st.checkbox('Accetto le condizioni sulla privacy')
    with st.expander("Condizioni sulla privacy"):
        st.write(privacy_text)
    submitted = st.form_submit_button("Invia iscrizione!")
    if submitted:
        query = f'SELECT * FROM "{sheet_url}"'
        rows = cursor.execute(query)
        emails = [x[4] for x in rows]
        n_subscriptions = len(emails)
        if email in emails:
            st.error('E-mail già presente nel database')
        elif not agree:
            st.error('Devi accettare le condizioni sulla privacy')
        else:
            ID = create_ID(n_subscriptions)
            next_match = 'TBD'
            payment = 'Pending'
            availability = str(availability)
            query = f'INSERT INTO "{sheet_url}" (ID, Name, Surname, Birth, Email, Level, Phone, NextMatch, PaymentStatus, Availability) VALUES ("{ID}", "{name}", "{surname}", "{birth}", "{email}", "{level}", "{phone}", "{next_match}", "{payment}", "{availability}", "{fiscal_code}")'
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