import sqlite3
from datetime import datetime
import time

def create_score_tables(db_name="maia_scores.db"):
    tables = ["content_analysis", "body_language", "emotion_detection", "job_suitability", "overall"]
    
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    for table in tables:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                session_no INTEGER PRIMARY KEY AUTOINCREMENT,
                score INTEGER NOT NULL,
                test_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    connection.commit()
    connection.close()

def insert_score(table_name, score, db_name="maia_scores.db"):
    valid_tables = {"content_analysis", "body_language", "emotion_detection", "job_suitability", "overall"}
    
    if table_name not in valid_tables:
        raise ValueError(f"Invalid table name: {table_name}. Must be one of {valid_tables}")

    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cursor.execute(f"""
        INSERT INTO {table_name} (score, test_time)
        VALUES (?, ?)
    """, (score, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))  # Ensuring proper datetime format

    connection.commit()
    connection.close()

def print_all_scores(db_name="maia_scores.db"):
    tables = ["content_analysis", "body_language", "emotion_detection", "job_suitability", "overall"]
    
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    for table in tables:
        print(f"\n--- {table.upper()} ---")
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()

        if not rows:
            print("No records found.")
        else:
            for row in rows:
                print(row)  # Each row is a tuple (session_no, score, test_time)

    connection.close()

def reset_all_scores(db_name="maia_scores.db"):
    tables = ["content_analysis", "body_language", "emotion_detection", "job_suitability", "overall"]
    
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    for table in tables:
        cursor.execute(f"DELETE FROM {table}")  # Deletes all records but keeps the table structure
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")  # Resets AUTOINCREMENT for session_no

    connection.commit()
    connection.close()
    print("All scores have been reset.")

def get_recent_and_best_score(table_name, db_name="maia_scores.db"):
    valid_tables = {"content_analysis", "body_language", "emotion_detection", "job_suitability", "overall"}
    
    if table_name not in valid_tables:
        raise ValueError(f"Invalid table name: {table_name}. Must be one of {valid_tables}")

    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # Fetch the most recent score (latest test_time)
    cursor.execute(f"""
        SELECT score FROM {table_name}
        ORDER BY test_time DESC
        LIMIT 1
    """)
    recent_score = cursor.fetchone()
    recent_score = recent_score[0] if recent_score else None  # Extract value or None if no records

    # Fetch the highest score
    cursor.execute(f"""
        SELECT MAX(score) FROM {table_name}
    """)
    best_score = cursor.fetchone()
    best_score = best_score[0] if best_score else None  # Extract value or None if no records

    connection.close()
    return recent_score, best_score

if __name__ == "__main__":
    create_score_tables()
    insert_score("overall", 90)
    time.sleep(1)
    insert_score("overall", 95)
    insert_score("content_analysis",68)
    time.sleep(1)
    insert_score("content_analysis",72)
    insert_score("body_language", 59)
    time.sleep(1)
    insert_score("body_language", 91)
    insert_score("emotion_detection", 70)
    time.sleep(1)
    insert_score("emotion_detection", 30)
    insert_score("job_suitability", 50)
    time.sleep(1)
    insert_score("job_suitability", 75)

#     time.sleep(2)
#     insert_score("overall", 70)
    print_all_scores()
#     r,b=get_recent_and_best_score("overall")
    #reset_all_scores()
#     print(r,b)