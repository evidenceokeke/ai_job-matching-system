from openai import OpenAI
from shared.config import Config


class Recommendation:
    def __init__(self):
        try:
            self.client = OpenAI(api_key=Config.get_api_key())
            self.model = Config.MODEL_NAME
            self.max_tokens = Config.MAX_TOKENS
            self.temperature = Config.TEMPERATURE
        except Exception as e:
            raise RuntimeError(f"Error initializing Recommendation Module: {str(e)}")

    def run(self, result):
        resume_text = result["resume_text"]
        top_matches = result["top_matches"][:3]
        top_matches_formatted = self.format_job_matches(top_matches)

        response = self.client.chat.completions.create(
            model = self.model,
            messages = [
                {
                    "role": "user",
                    "content": self.create_prompt(resume_text, top_matches_formatted)
                }
            ],
            temperature = self.temperature,
            max_tokens = self.max_tokens,
            response_format = {"type": "json_object"} # this good response format?
        )
        return {"content": response.choices[0].message.content}

    def format_job_matches(self, top_matches):
        job_list = []
        for job in top_matches:
            j = f"Job ID: {job['job_id']}\nJob Title: {job['job_title']}\nScore{job['score']}\nDescription; {job['description']}"
            job_list.append(j)

        return "\n\n".join(job_list)


    def create_prompt(self, resume, top_jobs):
        prompt = f"""
        You are an expert technical recruiter.
        
        Here is a candidate's resume:
        {resume}
        
        Here are the top job descriptions matched to the candidate by a semantic similarity algorithm:
        {top_jobs}
        
        Please do the following:
        1. Explain why this candidate is a good fit for each job.
        3. If any job requires skills or experience the candidate does not have, point them out.
        4. Summarize any key strengths of the candidate based on the matched jobs.
        
        Your response should return a list of JSON objects, each describing a top match like this:
        [
            {{
                "job_id": "<exact job ID>",
                "title": "<exact job title>",
                "similarity_reason": "Why the candidate is a good fit (max 150 words)",
                "strengths": {{
                    "1": "key strength",
                    "2": "another strength",
                    ...
                }},
                "weaknesses": {{
                    "1": "missing skill",
                    "2": "another missing requirement",
                    ...
                }}
            }},
            ...
        ]
        IMPORTANT: Return valid format (list of JSON objects of each job), let your response be able to be converted to a dataframe without errors.
        """
        return prompt
