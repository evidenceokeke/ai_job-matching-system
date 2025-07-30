import psycopg2
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from dotenv import load_dotenv
from backend.db.config import load_config
import os

# ------- ADDING DATA TO ELASTICSEARCH ------

load_dotenv()

class ElasticsearchService:
    def __init__(self):
        self.auth_keys = {"username": os.getenv("ES_USERNAME"), "password": os.getenv("ES_PASSWORD")}
        self.index_name = "job_data"

        # Connect to ElasticSearch
        self.es = Elasticsearch(
            hosts=['http://localhost:9200'],
            basic_auth=(self.auth_keys["username"], self.auth_keys["password"])
        )

        # check connection
        try:
            if not self.es.ping():
                raise ValueError("Connection to Elasticsearch failed!")
            print("Elasticsearch is up!")
        except Exception as e:
            print(f"Error connecting to Elasticsearch: {e}")

    def create_index(self):
        # Elasticsearch index mappings
        mappings = {
            "properties": {
                "job_id": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "description": {"type": "text", "analyzer": "standard"},
                "company": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "location": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "salary": {"type": "text", "analyzer": "standard"},
                "date_posted": {"type": "date"},
                "is_expired": {"type": "boolean"}

            }
        }

        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": mappings
        }

        # Create an index if it does not exist
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name, body=settings)
            # Check
            print("Index job_data created successfully.")
        else:
            print("Index job_data already exists.")


    # Load the Dataset
    def fetch_data_from_db(self, batch_size=500):
        """Fetch data from PostgreSQL in batches to save in ElasticSearch"""
        config = load_config()
        try:
            with psycopg2.connect(**config) as conn:
                with conn.cursor() as cur:
                    cur.itersize = batch_size
                    cur.execute("""SELECT job_id, title, description, company, location, salary, date_posted FROM jobs;""")

                    for row in cur:
                        yield {
                            "_index": "job_data",
                            "_id": row[0],
                            "_source": {
                                "job_id": row[0],
                                "title": row[1] if row[1] else "",
                                "description": row[2] if row[2] else "",
                                "company": row[3] if row[3] else "",
                                "location": row[4] if row[4] else "",
                                "salary": row[5] if row[5] else "",
                                "date_posted": row[6] if row[6] else "",
                            }
                        }
        except Exception as e:
            print(f"Error fetching data from PostgreSQL: {e}")


    def bulk_index_from_db(self):
        """Bulk insert jobs from Postgres to Elasticsearch"""
        try:
            bulk(self.es, self.fetch_data_from_db())
            print("Data successfully indexed")
        except Exception as e:
            print(f"Bulk indexing error: {e}")

    def update_es(self, new_jobs):
        """Bulk insert new jobs to Elasticsearch"""
        actions = []

        for job in new_jobs:
            actions.append({
                "_index": self.index_name,
                "_id": job.get("job_id"),
                "_source": {
                    "job_id": job.get("job_id", ""),
                    "title": job.get("title", ""),
                    "description": job.get("description", ""),
                    "company": job.get("company", ""),
                    "location": job.get("location", ""),
                    "salary": job.get("salary", ""),
                    "date_posted": job.get("date_posted", ""),
                }
            })
        try:
            bulk(self.es, actions)
            print("Data successfully indexed")
        except Exception as e:
            print(f"Bulk indexing error: {e}")

    def get_all_jobs(self, size=50):
        """Return all jobs (for listing)"""
        response = self.es.search(index=self.index_name, size=size, query={"match_all": {}})
        return [hit["_source"] for hit in response["hits"]["hits"]]
        # expand later, what if i want to click next to get more than 50

    def get_job_by_id(self, job_id: str):
        """Fetch a single job"""
        try:
            result = self.es.get(index=self.index_name, id=job_id)
            return result["_source"]
        except:
            return None


    def search_filter_jobs(self, keyword, size=50):
        """Search and filter jobs from list based on any keyword put in the search"""
        query = {
            "multi_match": {
                "query": keyword,
                "fields": ["title", "description", "company", "location", "salary"],
                "fuzziness": "AUTO"
            }
        }

        response = self.es.search(index=self.index_name, size=size, query=query)
        return [hit["_source"] for hit in response["hits"]["hits"]]

    def delete_job(self, job_id):
        """Delete job from index"""
        try:
            self.es.delete(index=self.index_name, id=job_id)
            return True
        except:
            return False
        # look into bulk deleting later maybe, when a user has selected more than one jobs to be deleted