"""ITM 220: starter for a small personal-project Streamlit app.

Students change only the YOUR PROJECT SETTINGS section using SQL that already
works in MySQL. The app asks for local connection information; it stores no
password in this file.
"""

import mysql.connector
import streamlit as st

# ============================================================================
# YOUR PROJECT SETTINGS — change only this section.
# ============================================================================
APP_TITLE = "My Project Database"
APP_DESCRIPTION = "Add one record and explore a useful result."

# Add one line for each value the person will type. Do not include an
# auto-increment ID. Keep the same order as the %s placeholders in INSERT_SQL.
INPUT_FIELDS = [
    {"column": "replace_with_column_1", "label": "Replace with a helpful label"},
    {"column": "replace_with_column_2", "label": "Replace with a helpful label"},
]

# Paste SQL that already worked in MySQL. One %s is needed per INPUT_FIELDS row.
INSERT_SQL = """REPLACE_WITH_YOUR_TESTED_INSERT_SQL"""

# Paste SQL that lists a useful result after an insert. A join is welcome when
# it makes a related value easier for a person to understand.
LIST_SQL = """REPLACE_WITH_YOUR_TESTED_LIST_SQL"""

# Paste one tested portfolio query with exactly one %s placeholder.
FILTER_LABEL = "What should the person type to filter this query?"
FILTER_MODE = "contains"  # Use "contains" for LIKE; use "exact" for an exact value.
FILTER_SQL = """REPLACE_WITH_YOUR_TESTED_FILTER_QUERY"""

# ============================================================================
# Supplied app structure — do not change below this line without targeted help.
# ============================================================================
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title(APP_TITLE)
st.caption(APP_DESCRIPTION)

with st.sidebar:
    st.header("Connection")
    host = st.text_input("Host", "127.0.0.1")
    port = st.number_input("Port", 1, 65535, 3306)
    user = st.text_input("MySQL username", "root")
    password = st.text_input("MySQL password", type="password")
    database_name = st.text_input("Project database name")


def connect():
    return mysql.connector.connect(
        host=host, port=int(port), user=user, password=password, database=database_name
    )


def select_rows(sql, parameters=()):
    connection = connect()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql, parameters)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


def change_data(sql, parameters=()):
    connection = connect()
    cursor = connection.cursor()
    cursor.execute(sql, parameters)
    connection.commit()
    cursor.close()
    connection.close()


if not database_name.strip():
    st.info("Enter your project database name in the Connection panel to begin.")
    st.stop()

if "REPLACE_WITH" in INSERT_SQL + LIST_SQL + FILTER_SQL:
    st.warning("Complete the YOUR PROJECT SETTINGS section before running the app.")
    st.stop()

st.subheader("Add one record")
st.write("Enter information, then use the button once to add one row.")
with st.form("insert_form"):
    values = [
        st.text_input(field["label"], key=f"field_{field['column']}")
        for field in INPUT_FIELDS
    ]
    insert_record = st.form_submit_button("Add record")

if insert_record:
    if any(not value.strip() for value in values):
        st.warning("Complete every input box before adding the record.")
    else:
        try:
            change_data(INSERT_SQL, tuple(value.strip() for value in values))
            st.success("The record was added. Check the list below to confirm it.")
        except mysql.connector.Error as error:
            st.error(f"The record was not added: {error}")

st.subheader("Current data")
if st.button("Show current results"):
    try:
        rows = select_rows(LIST_SQL)
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("The list query returned no rows.")
    except mysql.connector.Error as error:
        st.error(f"Could not load the list: {error}")

st.subheader("Explore a portfolio query")
search_value = st.text_input(FILTER_LABEL)
if st.button("Run query"):
    try:
        parameter = f"%{search_value.strip()}%" if FILTER_MODE == "contains" else search_value.strip()
        rows = select_rows(FILTER_SQL, (parameter,))
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
            st.success(f"Returned {len(rows)} row(s).")
        else:
            st.info("The query returned no rows.")
    except mysql.connector.Error as error:
        st.error(f"Could not run the query: {error}")

st.caption("A small working app is enough. Focus on the person, the database action, and the useful result.")
