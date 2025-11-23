import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def update_database(df: pd.DataFrame, video_id: str, video_title: str, upload_date: str):
    con = sqlite3.connect("backend/database/minor_project.db")
    cur = con.cursor()

    # Create tables if not exist
    cur.execute("""
    CREATE TABLE IF NOT EXISTS account(
        post_ID TEXT PRIMARY KEY,
        video_title TEXT,
        total_number_of_comments INTEGER NOT NULL,
        day DATETIME NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS post(
        ordering INTEGER PRIMARY KEY AUTOINCREMENT,
        post_ID INTEGER,
        time TIMESTAMP NOT NULL,
        comment TEXT NOT NULL,
        cleaned_comment TEXT NOT NULL,
        sentiment TEXT NOT NULL,
        FOREIGN KEY (post_ID) REFERENCES account(post_ID),
        UNIQUE(post_ID, comment, time) ON CONFLICT IGNORE
    )
    """)

    # Insert one entry in account for this batch
    total_comments = cur.execute("SELECT COUNT(*) FROM post WHERE post_ID = ?", (video_id,)).fetchone()[0]
    cur.execute("INSERT OR REPLACE INTO account (post_ID, video_title, total_number_of_comments, day) VALUES (?, ?, ?, ?)", (video_id, video_title, total_comments, upload_date))

    # Insert all rows from df into post table
    insert_sql = """
    INSERT OR IGNORE INTO post (post_ID, time, comment, cleaned_comment, sentiment)
    VALUES (?, ?, ?, ?, ?)
    """
    for _, row in df.iterrows():
        cur.execute(insert_sql, (
            video_id,
            row['time'],
            row['comment'],
            row['cleaned_comment'],
            row['sentiment']
        ))

    con.commit()
    con.close()
    return "Database updated with DataFrame content successfully."
