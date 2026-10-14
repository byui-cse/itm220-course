"""ITM 220: prepared Puppies front-end walkthrough.

Students enter local connection details in the page. This file stores no
password. It assumes the course Puppies schema contains puppy, puppy_trick,
trick, and breed tables.
"""

import mysql.connector
import streamlit as st

st.set_page_config(page_title="Puppies Front End", layout="centered")
st.title("🐶 Puppies Front End")
st.caption("Search related data, add a breed, and see the changed list.")

with st.sidebar:
    st.header("Connection")
    host = st.text_input("Host", "127.0.0.1")
    port = st.number_input("Port", 1, 65535, 3306)
    user = st.text_input("MySQL username", "root")
    password = st.text_input("MySQL password", type="password")


def connect():
    return mysql.connector.connect(
        host=host, port=int(port), user=user, password=password, database="puppies"
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


if st.sidebar.button("Test connection"):
    try:
        connection = connect()
        connection.close()
        st.sidebar.success("Connected to the Puppies database.")
    except mysql.connector.Error as error:
        st.sidebar.error(f"Could not connect: {error}")

st.subheader("1. Find a puppy's tricks")
st.write("This search follows the relationships among puppy, puppy_trick, and trick.")
name = st.text_input("Puppy name contains")
if st.button("Show tricks"):
    try:
        rows = select_rows(
            """
            SELECT p.puppy_name AS puppy, t.trick_name AS trick
            FROM puppy AS p
            JOIN puppy_trick AS pt ON pt.puppy_id = p.puppy_id
            JOIN trick AS t ON t.trick_id = pt.trick_id
            WHERE p.puppy_name LIKE %s
            ORDER BY p.puppy_name, t.trick_name;
            """,
            (f"%{name.strip()}%",),
        )
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("No matching tricks were found.")
    except mysql.connector.Error as error:
        st.error(f"Could not load tricks: {error}")

st.divider()
st.subheader("2. Add a breed")
with st.form("new_breed"):
    breed = st.text_input("New breed name")
    add_breed = st.form_submit_button("Add breed")

if add_breed:
    clean_breed = breed.strip()
    if not clean_breed:
        st.warning("Type a breed name before selecting Add breed.")
    else:
        try:
            exists = select_rows(
                "SELECT 1 FROM breed WHERE LOWER(breed_name) = LOWER(%s) LIMIT 1;",
                (clean_breed,),
            )
            if exists:
                st.info("That breed is already in the database.")
            else:
                change_data("INSERT INTO breed (breed_name) VALUES (%s);", (clean_breed,))
                st.success(f"Added breed: {clean_breed}")
        except mysql.connector.Error as error:
            st.error(f"Could not add the breed: {error}")

if st.button("Show breeds"):
    try:
        rows = select_rows("SELECT breed_id, breed_name FROM breed ORDER BY breed_name;")
        st.dataframe(rows, use_container_width=True, hide_index=True)
    except mysql.connector.Error as error:
        st.error(f"Could not load breeds: {error}")

st.caption("Focus on the person, the database action, and the result—not on Python syntax.")
