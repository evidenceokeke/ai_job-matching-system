from openai import OpenAI
from shared.config import Config # i'm thinking of having one config file later for all shared configurations
from sklearn.metrics.pairwise import cosine_similarity
from data_pipeline.data_preprocessing import DataPreprocessing


class MatchingAlgorithm:
    def __init__(self):
        try:
            self.client = OpenAI(api_key=Config.get_api_key())
            self.model = "text-embedding-3-small"
        except Exception as e:
            raise Exception(f"Error initializing OpenAI: {e}")

        try:
            self.data_preprocessor = DataPreprocessing()
        except Exception as e:
            raise Exception(f"Error initializing DataPreprocessing class: {e}")

    def run(self, resume_data):
        """
        Get the similarity scores between resume and jobs in the database.
        Return the top 10 jobs that matches with the resume
        """
        # Get jobs from database
        jobs_df = self.data_preprocessor.get_data_from_db(['job_id', 'title', 'description'], 'jobs')

        # preprocess the job data
        jobs_df = self.data_preprocessor.preprocess_data(jobs_df, ['title', 'description'])

        # Generate job embeddings for the jobs
        job_embeddings = []
        for _, row in jobs_df.iterrows():
            job_text = f"{row['title']} {row['description']}"
            job_embedding = self.generate_embedding(job_text)["embedding"]
            job_embeddings.append((row['job_id'], row['title'], job_embedding))

        # Parse the resume
        #resume_data = self.parser.run()

        # Extract the necessary resume text from resume data
        resume_text = self.extract_resume_text(resume_data)

        # Embed the resume
        resume_embedding = self.generate_embedding(resume_text)["embedding"]

        # Now find the top matches
        top_matches = self.compare_similarity(resume_embedding, job_embeddings)
        # returns a list of dictionary of id, title, score
        #print(top_matches)

        # Map the job id to the title and description for efficient lookup
        job_lookup = jobs_df.set_index('job_id')[['title', 'description']].to_dict(orient='index')
        #print(list(job_lookup.items()))[:2]

        for match in top_matches:
            job_id = match["job_id"]
            if job_id in job_lookup:
                match["description"] = job_lookup[job_id]["description"]

        result = {
            #"resume": resume_data, # incase we need to get the name, and other info etc,
            "resume_text": resume_text, # the one i will use for recommendation
            "top_matches": top_matches
        }

        return result

    def generate_embedding(self, text):
        """Generate text embeddings using OpenAI"""
        try:
            response = self.client.embeddings.create(
                input = text,
                model = self.model
            )
            return {"embedding": response.data[0].embedding}
        except Exception as e:
            raise Exception (f"Error generating embedding: {e}")

    def extract_resume_text(self, resume_data):
        """Extract Resume text for Matching from parsed resume data"""

        # Skills
        skills = ' '.join(resume_data.get('skills', []))

        # Experience
        experience_list = []
        for exp in resume_data.get('experience', []):
            details = [
                exp.get('company', ''),
                exp.get('position', ''),
                exp.get('location', ''),
                exp.get('duration', ''),
                ' '.join(exp.get('responsibilities', []))
            ]
            experience_list.append(' '.join(str(d) for d in details if d))
        experience = ' '.join(experience_list)

        # Education
        education_list = []
        for edu in resume_data.get('education', []):
            details = [
                edu.get('institution', ''),
                edu.get('degree', ''),
                edu.get('field', ''),
                edu.get('year', '')
            ]
            education_list.append(' '.join(str(d) for d in details if d))
        education = ' '.join(education_list)

        # Projects
        project_list = []
        for proj in resume_data.get('projects', []):
            details = [
                proj.get('name', ''),
                proj.get('description', '')
            ]
            project_list.append(' '.join(str(d) for d in details if d))
        projects = ' '.join(project_list)

        # Combine all resume text
        resume_text = f"{skills} {experience} {education} {projects}".strip()
        return resume_text

    def compare_similarity(self, resume_vec, job_vecs_w_ids):
        """
        Calculate the cosine similarity_score between resume and all job description
        vec1 - resume, vec2 - list of all embeddings job description
        Return the top 10 jobs
        """
        matches = []

        for job_id, job_title, job_vec in job_vecs_w_ids:
            similarity_score = cosine_similarity([resume_vec], [job_vec])[0][0]
            if similarity_score >= 0.45:
                matches.append((job_id, job_title, similarity_score))

        if not matches:
            return "No strong matches found for this candidate."

        matches.sort(key=lambda x: x[2], reverse=True)
        top_10 = [{
            "job_id": job_id,
            "job_title": job_title,
            "score": round(score, 3)
        } for job_id, job_title, score in matches[:10]]

        return top_10





