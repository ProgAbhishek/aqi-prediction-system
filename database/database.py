import sqlite3
import os

# Path to air_quality.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "air_quality.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_table():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS air_quality(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        timestamp TEXT NOT NULL,

        aqi INTEGER,

        pm2_5 REAL,

        pm10 REAL,

        co REAL,

        no2 REAL,

        o3 REAL,

        so2 REAL

    );
    """)

    conn.commit()
    conn.close()

    print("Table Ready.")


def insert_data(data):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO air_quality(

        timestamp,
        aqi,
        pm2_5,
        pm10,
        co,
        no2,
        o3,
        so2

        )

        VALUES(?,?,?,?,?,?,?,?)

    """,(

        data["timestamp"],
        data["aqi"],
        data["pm2_5"],
        data["pm10"],
        data["co"],
        data["no2"],
        data["o3"],
        data["so2"]

    ))

    conn.commit()
    conn.close()

    print("Inserted Successfully")

def view_data():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM air_quality")

    rows = cursor.fetchall()

    for row in rows:
        print(row)

    conn.close()