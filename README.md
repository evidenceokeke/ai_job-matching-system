# AI JOB MATCHING SYSTEM


This project is an AI-powere job matching system where users can upload a PDF resume. The system parses the resume, finds the best-matching jobs from the database and generates intelligent recommendations using prompt engineering.

https://github.com/user-attachments/assets/f4cf7196-0d91-4026-996b-3eb2a281d7ed

## Project Structure
* **Database** - PostrgeSQL
*  **Frontend** - Streamlit
*  **Backend API** - FastAPI
*  **Resume Parser** - OpenAI GPT-3.5 (Primary), NLTK (Backup Parser)
*  **Job Matching Algorithm** - OpenAI Text Embediing + Scikit-learn Cosine Similarity
*  **Recommendation** - OpenAI GPT 3.5
*  **Search Functionality** - Elasticsearch
*  **Deployment** - AWS EC2
*  **Job Data Source** - Scraped from Indeed using Apify Job Scraper

## How to Run the Project Locally

1. Clone the repo
2. Install dependencies
3. Start Elasticsearch (Docker)
   ```
    cd elastic-search-local
    docker-compose up -d
Make sure Docker is running. Open Kibana (http://localhost:5601) to inspect data.
<img width="2239" height="1228" alt="image" src="https://github.com/user-attachments/assets/547c27f2-7408-487b-b992-dba0a770263b" />


4. Run FastAPI Backend
   ```
   uvicorn main:app --reload
 Visit http://localhost:8000 access Swagger docs at http://localhost:8000/docs 
 

5. Launch Streamlit Frontend
   ```
   cd frontend
   streamlit run home.py


## Setting Search in Elasticsearch

Create the job_data index by running:

```
python data_pipeline/elasticsearch_service.py

```
This will auto-create and populate the index.


## Scraping Job Listings from Indeed

```
cd job_scraper
python indeed_scraper.py
```
Ensure PostgreSQL and Elasticsearch confgurations are set up correctly because this will scrape and send them to the database and elasticsearch straight.


## Deploying on AWS EC2
* Launch EC2 Instance - Follow this tutorial - https://youtu.be/YH_DVenJHII?si=P4ayk54JiNW3rsn8
* Transfer project files:
  ```
  scp -i your-key.pem -r ./job-matching-system ec2-user@<EC2-IP>:/home/ec2-user/
  ```
* On the instance:
  ```
  pip install -r requirements.txt
  python main.py
  # and other things
* Allow external access (Port 5000)
* Update EC2 Security Group: Custom TCP → Port 5000 → Source: 0.0.0.0/0
* Also update Windows Firewall (if applicable)
* Test API remotely: [http://:5000](http://<ec2-ip>:5000
* Cleanup Terminate your EC2 instance to avoid unwanted AWS charges

*Happy Learning!*
