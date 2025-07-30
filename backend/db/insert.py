import json
import psycopg2
from backend.db.config import load_config

# ------ INSERT DATA TO POSTGRESQL DATABASE ------

def insert_jobs(job_data):
    """Insert original  job data directly into PostgreSQL database from Apify"""
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
               for job in job_data:
                   # Insert the job_data into the 'jobs' table
                    cur.execute(
                        """
                        INSERT INTO jobs (job_id, title, company, location, salary, rating, reviews_count, 
                        url, apply_link, description, date_posted, scraped_at, is_expired, raw_data)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (job_id) DO NOTHING;
                        """, (
                            job.get("id"),
                            job.get("positionName", "N/A"),
                            job.get("company", "N/A"),
                            job.get("location", "N/A"),
                            job.get( "salary", "N/A"),
                            job.get("rating", 0),
                            job.get("reviewsCount", 0),
                            job.get("url", "N/A"),
                            job.get("externalApplyLink", "N/A"),
                            job.get("description", "N/A"),
                            job.get("postingDateParsed"),
                            job.get("scrapedAt"),
                            job.get("isExpired", False),
                            json.dumps(job) # Raw JSON data
                        )
                    )

                    # Insert job types into 'job_types' and link to job
                    for job_type in job.get("jobType", []):
                        #  Normalize job type (capitalize and strip whitespace)
                        job_type = job_type.strip().capitalize()

                        # Insert job type if not exists
                        cur.execute(
                            """
                            INSERT INTO job_types (job_type)
                            VALUES (%s)
                            ON CONFLICT (job_type) DO NOTHING;
                            """, (job_type,)
                        )

                        # Link job to job type in 'job_job_types'
                        cur.execute(
                            """
                            INSERT INTO job_job_types (job_id, job_type_id)
                            SELECT jobs.id, job_types.id
                            FROM jobs
                            JOIN job_types ON job_types.job_type = %s
                            WHERE jobs.job_id = %s
                            ON CONFLICT DO NOTHING;
                            """, (job_type, job["id"])
                        )
            # commit the changes to the database
            conn.commit()
            print(f"Successfully inserted {len(job_data)} job records.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def insert_resumes(resumes):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO resumes (filename, raw_text)
                    VALUES (%s, %s)
                    RETURNING id;
                    """, (
                        resumes.get("filename"),
                        resumes.get("raw_text")
                    )
                )

                # Get the resume id
                resume_id = cur.fetchone()[0]

            conn.commit()

            print("Successfully inserted resume to database.")
            return resume_id

    except(Exception, psycopg2.DatabaseError) as error:
        print(f"Error inserting resume to resumes table: {error}")


def insert_resume_data(resume_id, resume_data):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO resume_data (resume_id, name, email, phone, location, education, experience, skills, certifications, projects)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        resume_id,
                        resume_data.get("name"),
                        resume_data.get("email"),
                        resume_data.get("phone"),
                        resume_data.get("location"),
                        json.dumps(resume_data.get("education")),
                        json.dumps(resume_data.get("experience")),
                        resume_data.get("skills"),
                        json.dumps(resume_data.get("certifications")),
                        json.dumps(resume_data.get("projects"))
                    )
                )

            conn.commit()
            print("Successfully inserted resume data to database")


    except (Exception, psycopg2.DatabaseError) as e:
        print(f"Failure inserting resume data: {e}")

# Use this when you've already scraped the file
"""def main():
    "Read the JSON file and insert data into the database."
    try:
        # Load the file as a dictionary
        with open('data.json', 'r', encoding='utf-8') as file:
            job_data = json.load(file)
            print(f"Loaded {len(job_data)} records successfully.")
            # Insert into database
            insert_jobs(job_data)
    except Exception as e:
        print(e)"""




"""if __name__ == '__main__':
    main()"""