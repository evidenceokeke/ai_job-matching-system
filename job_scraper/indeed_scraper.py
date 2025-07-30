import asyncio
import os
from dotenv import load_dotenv
from apify_client import ApifyClientAsync
from backend.db.insert import insert_jobs
from data_pipeline.elasticsearch_service import ElasticsearchService

load_dotenv()

class IndeedScraper:
    def __init__(self):
        self.token = os.getenv('MY-APIFY-TOKEN')
        if not self.token:
            raise Exception("Apify token is missing. Check the .env file.")

        # Client initialization with the API token
        self.apify_client = ApifyClientAsync(self.token)

        # Actor initialization with ID
        self.actor_client = self.apify_client.actor("hMvNSpz3JnHgl5jkh")

        # List of job positions to search
        self.positions = ["software engineer", "data analyst", "machine learning engineer", "backend engineer",
                     "product manager"]

    async def run(self):
        actor_client = self.apify_client.actor(self.actor_client)

        for position in self.positions:
            print(f"Searching for position: {position}")

            # Define the input for the actor
            run_input = {
                "country": "CA",
                "followApplyRedirects": False,
                "maxItems": 100,
                "parseCompanyDetails": False,
                "position": position,
                "saveOnlyUniqueItems": True
            }

            # Start an actor and wait for it to finish
            call_result = await actor_client.call(run_input=run_input)

            if call_result is None:
                print(f'Actor run failed for position: {position}')
                continue

            # Fetch results from the Actor run's default dataset.
            dataset_client = self.apify_client.dataset(call_result['defaultDatasetId'])
            list_items_result = await dataset_client.list_items()
            job_data = list_items_result.items

            # Export to PostgreSQL database
            print(f"Fetched {len(job_data)} job records for position '{position}'. Inserting into database...")
            insert_jobs(job_data)

            # Export to Elasticsearch
            es = ElasticsearchService()
            es.update_es(job_data)

