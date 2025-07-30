from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from resume_parser.ai_resume_parser import ResumeParser
from matching_algorithm.matching_system import MatchingAlgorithm
from matching_algorithm.recommendation_system import Recommendation
from data_pipeline.elasticsearch_service import ElasticsearchService
from job_scraper.indeed_scraper import IndeedScraper
from backend.db.utils import QueryDatabase

app = FastAPI()

# NEXT TASKS TO COMPLETE
# add search filters to /jobs
# validate input, make sure that resume upload is pdf
# paginate job lists

@app.post("/")
def home():
    pass

# parse resume and show parsed data
@app.post("/resumes")
def upload_resume(file: UploadFile = File(...)):
    try:
        parser = ResumeParser(file.file)
        parsed_data = parser.run()

        return {
            "message": "Resume parsed successfully.",
            "parsed_data": parsed_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {e}")

# matching algorithm and recommendation system of parsed data
@app.post("/match_candidate/{resume_id}")
def match_candidate(resume_id):
    try:
        # get parsed data from database
        db_query = QueryDatabase()
        parsed_data = db_query.get_parsed_resume(resume_id)

        if not parsed_data:
            raise HTTPException(status_code=404, detail="Resume data not found.")

        # run the matching algorithm
        matcher = MatchingAlgorithm()
        top_matches = matcher.run(parsed_data)

        if top_matches["top_matches"] == "No strong matches found for this candidate.":
            # No need to run recommendation
            return {
                "message": "Matching algorithm ran successfully.",
                "result": top_matches["top_matches"]
            }
        # run the recommendation system
        recommend = Recommendation()
        top_recommendations = recommend.run(top_matches)

        return {
            "message": "Matching algorithm ran successfully.",
            "top_matches": top_matches["top_matches"],
            "recommendations": top_recommendations
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running matching algorithm: {e}")


# click on a job to more details of that job
@app.get("/jobs/{id}")
def view_job_details(id):
    es = ElasticsearchService()
    job_details = es.get_job_by_id(id)
    return {
        "message": "Job details gotten successfully.",
        "job_details": job_details
    }

# list/ table view of all jobs in the database when you navigate to the jobs page
@app.get("/jobs")
def get_jobs(search: str = Query("", alias="search")):
    es = ElasticsearchService()

    if search:
        job_list = es.search_filter_jobs(search)
    else:
        job_list = es.get_all_jobs()

    return {
        "message": "Jobs list success",
        "job_list": job_list
    }

# add more jobs to database
@app.post("/scrape_jobs")
def scrape_jobs():
    scrape_indeed = IndeedScraper()
    try:
        # scrape jobs from indeed
        scrape = scrape_indeed.run()

        if scrape:
            return{
                "message": "New jobs added to database",
                # redirect to jobs page to see list of jobs
            }
    except Exception as e:
        print(f"Error getting new jobs: {e}")


# delete jobs button, for now would on jobs/{id} page,
@app.delete("/delete_job/{job_id}")
def delete_job(job_id):
    # delete from db
    db_query = QueryDatabase()
    from_db = db_query.delete_job(job_id)
    # delete from elasticsearch
    es = ElasticsearchService()
    from_es = es.delete_job(job_id)

    # if it successfully deletes from both
    if from_es and from_db:
        return {
            "message": "Job successfully deleted"
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to delete job from database or Elasticsearch.")