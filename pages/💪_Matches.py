import streamlit as st
from PIL import Image
from google.oauth2 import service_account
from shillelagh.backends.apsw.db import connect
import pandas as pd
import datetime
import pytz


st.set_page_config(page_title="Matches - TDRTennis 2023", page_icon="💪")

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """

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
games_url = st.secrets["private_gsheets_url2"]

tz = pytz.timezone('Europe/Berlin')
today = datetime.datetime.now(tz).date()
rows = cursor.execute(f'SELECT * FROM "{games_url}"')
rows = rows.fetchall()
matches = [row[0:14] for row in rows if row[3].date() < datetime.timedelta(days = 3) + today]

names = []
for match in matches:
        player1 = cursor.execute(f'SELECT "Name", "Surname" FROM "{sheet_url}" WHERE "ID" = "{match[0]}"')
        player1 = player1.fetchall()
        player2 = cursor.execute(f'SELECT "Name", "Surname" FROM "{sheet_url}" WHERE "ID" = "{match[1]}"')
        player2 = player2.fetchall()
        names.append((player1[0][0], player1[0][1], player2[0][0], player2[0][1]))        

image = Image.open('./pages/20230711_094921_0000.png')

# Set up page
st.markdown(hide_menu_style, unsafe_allow_html=True)
st.title('Matches')

dt = pd.DataFrame(matches, columns=['ID1', 'ID2', 'MatchStatus', 'Date', 'Score1', 'Score2', 'Game1', 'Game2', 'Set1', 'Set2', 'Tie1', 'Tie2', 'Advantage1', 'Advantage2'])

for row in range(dt.shape[0]):
        dt.loc[row, 'ID1'] = names[row][0] + ' ' + names[row][1]
        dt.loc[row, 'ID2'] = names[row][2] + ' ' + names[row][3]

dt.Date = dt.Date.apply(lambda x: x + datetime.timedelta(hours = 2))

st.dataframe(dt)

st.sidebar.image(image, use_column_width=True)
