# ----- Feature Extraction SQL Processes ------

import psycopg2
from backend.db.config import load_config


# move to create-tables.py
create_salary_range = """
CREATE TABLE IF NOT EXISTS salary_range (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    min_salary FLOAT,
    max_salary FLOAT,
    frequency VARCHAR(30)
    )
"""
# move to insert.py
insert_sr_data = """
INSERT INTO salary_range (job_id, min_salary, max_salary, frequency)
VALUES (%s, %s, %s, %s);
"""

def salary_range_feature(salary_range):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Create Table first
                cur.execute(create_salary_range)

                # Now insert data into table
                for _, row in salary_range.iterrows():
                    cur.execute(insert_sr_data,(row["id"], row["min_salary"],
                                                 row["max_salary"], row["frequency"]))

                # commit the changes to the database
                conn.commit()
                print(f"Successfully created salary range")

    except (Exception, psycopg2.DatabaseError) as error:
         print(error)