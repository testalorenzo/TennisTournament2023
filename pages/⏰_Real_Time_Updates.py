import streamlit as st
from google.oauth2 import service_account
from shillelagh.backends.apsw.db import connect


st.set_page_config(page_title="Real Time Updates - TDRTennis 2023", page_icon="🎾")

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

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True


if check_password():
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    st.title('Real Time Updates')


    rows = cursor.execute(f'SELECT * FROM "{games_url}"')
    rows = rows.fetchall()
    matches = [(row[0], row[1]) for row in rows if row[2] == 'Scheduled']

    raw_options = []
    options = []
    for match in matches:
        player1 = cursor.execute(f'SELECT "Name", "Surname" FROM "{sheet_url}" WHERE "ID" = "{match[0]}"')
        player1 = player1.fetchall()
        player2 = cursor.execute(f'SELECT "Name", "Surname" FROM "{sheet_url}" WHERE "ID" = "{match[1]}"')
        player2 = player2.fetchall()
        options.append(f'{player1[0][0]} {player1[0][1]} vs {player2[0][0]} {player2[0][1]}')
        raw_options.append((player1[0][0], player1[0][1], player2[0][0], player2[0][1]))

    option = st.selectbox('Quale partita vuoi arbitrare?', options)
    index = options.index(option)
    raw_option = raw_options[index]
    credentials = matches[index]

    cols = st.columns(2)
    with cols[0]:
        st.write(f'ID1: {credentials[0]}')
        if st.button(raw_option[0] + ' ' + raw_option[1] + ' +'):
            cursor.execute(f'UPDATE "{games_url}" SET "Score1" = "Score1" + 15 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
            connection.commit()
        if st.button(raw_option[0] + ' ' + raw_option[1] + ' -'):
            cursor.execute(f'UPDATE "{games_url}" SET "Score1" = "Score1" - 15 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
            connection.commit()
    with cols[1]:
        st.write(f'ID2: {credentials[1]}')
        if st.button(raw_option[2] + ' ' + raw_option[3] + ' +'):
            cursor.execute(f'UPDATE "{games_url}" SET "Score2" = "Score2" + 15 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
            connection.commit()
            cursor.execute(f'UPDATE "{games_url}" SET "MatchStatus" = Playing WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
            connection.commit()
        if st.button(raw_option[2] + ' ' + raw_option[3] + ' -'):
            cursor.execute(f'UPDATE "{games_url}" SET "Score2" = "Score2" - 15 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
            connection.commit()
            cursor.execute(f'UPDATE "{games_url}" SET "MatchStatus" = Playing WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
            connection.commit()

    rows = cursor.execute(f'SELECT * FROM "{games_url}" WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
    rows = rows.fetchall()

    score1 = rows[0][4]
    score2 = rows[0][5]
    game1 = rows[0][6]
    game2 = rows[0][7]
    set1 = rows[0][8]
    set2 = rows[0][9]
    tie1 = rows[0][10]
    tie2 = rows[0][11]
    advantage1 = rows[0][12]
    advantage2 = rows[0][13]

    # Natural progression of game
    if score1 == 45:
        score1 = 40
        cursor.execute(f'UPDATE "{games_url}" SET "Score1" = 40 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
        connection.commit()
    if score2 == 45:
        score2 = 40
        cursor.execute(f'UPDATE "{games_url}" SET "Score2" = 40 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
        connection.commit()
    if score1 == 55 and score2 != 40:
        game1 += 1
        score1 = 0
        score2 = 0
        advantage1 = 0
        advantage2 = 0
        cursor.execute(f'UPDATE "{games_url}" SET "Game1" = "Game1" + 1, "Score1" = 0, "Score2" = 0, "Advantage1" = 0, "Advantage2" = 0 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
        connection.commit()
    if score2 == 55 and score1 != 40:
        game2 += 1
        score1 = 0
        score2 = 0
        advantage1 = 0
        advantage2 = 0
        cursor.execute(f'UPDATE "{games_url}" SET "Game2" = "Game2" + 1, "Score1" = 0, "Score2" = 0, "Advantage1" = 0, "Advantage2" = 0 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
        connection.commit()

    if game1 == 4 and game2 < 3:
        set1 += 1
        game1 = 0
        game2 = 0
        cursor.execute(f'UPDATE "{games_url}" SET "Set1" = "Set1" + 1, "Game1" = 0, "Game2" = 0 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
        connection.commit()
    if game2 == 4 and game1 < 3:
        set2 += 1
        game1 = 0
        game2 = 0
        cursor.execute(f'UPDATE "{games_url}" SET "Set2" = "Set2" + 1, "Game1" = 0, "Game2" = 0 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
        connection.commit()

    if game1 == 5 and game2 == 3:
        set1 += 1
        game1 = 0
        game2 = 0
        cursor.execute(f'UPDATE "{games_url}" SET "Set1" = "Set1" + 1, "Game1" = 0, "Game2" = 0 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
        connection.commit()
    if game2 == 5 and game1 == 3:
        set2 += 1
        game1 = 0
        game2 = 0
        cursor.execute(f'UPDATE "{games_url}" SET "Set2" = "Set2" + 1, "Game1" = 0, "Game2" = 0 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
        connection.commit()

    # 4-4 (Tie break)
    if game1 == 4 and game2 == 4:
        if score1 == 15:
            score1 = 0
            tie1 += 1
            cursor.execute(f'UPDATE "{games_url}" SET "Score1" = 0, "Tie1" = "Tie1" + 1 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
            connection.commit()
        if score2 == 15:
            score2 = 0
            tie2 += 1
            cursor.execute(f'UPDATE "{games_url}" SET "Score2" = 0, "Tie2" = "Tie2" + 1 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
            connection.commit()
        if score1 == -15:
            score1 = 0
            tie1 -= 1
            cursor.execute(f'UPDATE "{games_url}" SET "Score1" = 0, "Tie1" = "Tie1" - 1 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
            connection.commit()
        if score2 == -15:
            score2 = 0
            tie2 -= 1
            cursor.execute(f'UPDATE "{games_url}" SET "Score2" = 0, "Tie2" = "Tie2" - 1 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
            connection.commit()
        if tie1 == 7 and tie2 < 6:
            set1 += 1
            game1 = 0
            game2 = 0
            tie1 = 0
            tie2 = 0
            cursor.execute(f'UPDATE "{games_url}" SET "Set1" = "Set1" + 1, "Game1" = 0, "Game2" = 0, "Tie1" = 0, "Tie2" = 0 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
            connection.commit()
        if tie2 == 7 and tie1 < 6:
            set2 += 1
            game1 = 0
            game2 = 0
            tie1 = 0
            tie2 = 0
            cursor.execute(f'UPDATE "{games_url}" SET "Set2" = "Set2" + 1, "Game1" = 0, "Game2" = 0, "Tie1" = 0, "Tie2" = 0 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
            connection.commit()
        if tie1 > 7 and tie1 > tie2 + 1:
            set1 += 1
            game1 = 0
            game2 = 0
            tie1 = 0
            tie2 = 0
            cursor.execute(f'UPDATE "{games_url}" SET "Set1" = "Set1" + 1, "Game1" = 0, "Game2" = 0, "Tie1" = 0, "Tie2" = 0 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
            connection.commit()
        if tie2 > 7 and tie2 > tie1 + 1:
            set2 += 1
            game1 = 0
            game2 = 0
            tie1 = 0
            tie2 = 0
            cursor.execute(f'UPDATE "{games_url}" SET "Set2" = "Set2" + 1, "Game1" = 0, "Game2" = 0, "Tie1" = 0, "Tie2" = 0 WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
            connection.commit()
        
        

    # 40-40 (Deuce)
    if score1 == 55 and score2 == 40:
        score1 = 40
        st.text('here we are 1')
        if advantage2 == 1:
            st.text('here we are 2')
            advantage1 = 0
            advantage2 = 0
        elif advantage1 == 1:
            st.text('here we are 4')
            advantage1 = 0
            advantage2 = 0
            score1 = 0
            score2 = 0
            game1 += 1
        else:
            st.text('here we are 3')
            advantage1 = 1
            advantage2 = 0
        cursor.execute(f'UPDATE "{games_url}" SET "Score1" = {score1}, "Advantage1" = {advantage1}, "Advantage2" = {advantage2} WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
        connection.commit()
    elif score1 == 40 and score2 == 55:
        score2 = 40
        if advantage1 == 1:
            advantage1 = 0
            advantage2 = 0
        elif advantage2 == 1:
            advantage1 = 0
            advantage2 = 0
            score1 = 0
            score2 = 0
            game2 += 1
        else:
            advantage1 = 0
            advantage2 = 1
        cursor.execute(f'UPDATE "{games_url}" SET "Score2" = {score2}, "Advantage1" = {advantage1}, "Advantage2" = {advantage2} WHERE "ID1" = "{credentials[0]}" AND "ID2" = "{credentials[1]}"')
        connection.commit()


    st.write(f'Punteggio: {score1} - {score2}')
    st.write(f'Vantaggio: {advantage1} - {advantage2}')
    st.write(f'Game: {game1} - {game2}')
    st.write(f'Set: {set1} - {set2}')
    st.write(f'Tie break: {tie1} - {tie2}')