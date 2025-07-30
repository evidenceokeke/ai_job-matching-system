import psycopg2
from config import load_config


def create_tables():
    """Create tables in the PostgreSQL database"""
    # Initialize a list of CREATE TABLE statements
    commands = (
        """
        CREATE TABLE IF NOT EXISTS jobs (
          id SERIAL PRIMARY KEY,
          job_id VARCHAR UNIQUE NOT NULL,
          title VARCHAR NOT NULL,
          company VARCHAR,
          location VARCHAR,
          salary VARCHAR(1000),
          rating NUMERIC,
          reviews_count INTEGER,
          url VARCHAR,
          apply_link VARCHAR,
          description VARCHAR,
          date_posted TIMESTAMP,
          scraped_at TIMESTAMP,
          is_expired BOOLEAN,
          raw_data JSONB  
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS job_types (
            id SERIAL PRIMARY KEY,
            job_type VARCHAR(50) UNIQUE NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS job_job_types (
            job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
            job_type_id INTEGER NOT NULL REFERENCES job_types(id) ON DELETE CASCADE,
            PRIMARY KEY (job_id, job_type_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS resumes (
            id SERIAL PRIMARY KEY,
            filename VARCHAR,
            raw_text VARCHAR,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS resume_data (
            resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
            name VARCHAR,
            email VARCHAR UNIQUE,
            phone VARCHAR UNIQUE,
            location VARCHAR,
            education JSONB,
            experience JSONB,
            skills TEXT[],
            certifications JSONB,
            projects JSONB
        )
        """
    )
    try:
        # Read the connection parameters
        config = load_config()
        # Connect to PostgreSQL server
        with psycopg2.connect(**config) as conn:
            # Create a new cursor object from the connection object
            with conn.cursor() as cur:
                # execute the CREATE TABLE statement
                for command in commands:
                    cur.execute(command)
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)



if __name__ == '__main__':
    create_tables()
