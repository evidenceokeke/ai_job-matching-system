import psycopg2
from backend.db.config import  load_config

# ------ QUERY DATABASE -----
class QueryDatabase:
    def __init__(self):
        self.config = load_config()

    def get_parsed_resume(self, resume_id):
        """ Retrieve parsed resume data from resume_data table"""

        try:
            with psycopg2.connect(**self.config) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM resume_data WHERE resume_id = %s;",
                                (resume_id,))

                    row = cur.fetchone()

                    if not row:
                        return None

                    # convert row to a dictionary
                    columns = list()
                    for desc in cur.description:
                        columns.append(desc[0])

                    row_dict = dict(zip(columns, row))

                    return row_dict

        except (Exception, psycopg2.DatabaseError) as error:
            print("Database error:", error)
            return None


    def delete_job(self, job_id):
        """Delete job from jobs table"""
        try:
            with psycopg2.connect(**self.config) as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM jobs WHERE ID = %s;",
                                (job_id,))

                    deleted_rows = cur.rowcount

                    return deleted_rows > 0

        except (Exception, psycopg2.DatabaseError) as error:
            print("Database error:", error)
            return None