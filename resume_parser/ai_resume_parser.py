import traceback
import json
import re
from openai import OpenAI
from PyPDF2 import PdfReader
from shared.config import Config
from resume_parser.backup_parser import BackupParser
from data_pipeline.data_preprocessing import DataPreprocessing
from backend.db.insert import insert_resumes, insert_resume_data

class ResumeParser:
    def __init__(self, file_obj):
        try:
            print("ResumeParser __init_ called")
            traceback.print_stack()
            self.client = OpenAI(api_key=Config.get_api_key())
            self.model = Config.MODEL_NAME
            self.max_tokens = Config.MAX_TOKENS
            self.temperature = Config.TEMPERATURE
            # Hardcoded for testing
            #self.pdf_path = Path(r"/resume_parser/test_resumes/Olivia_Chen_Resume.pdf")
            self.file = file_obj
        except ValueError as e:
            raise RuntimeError(f"OpenAI client initialization failed: {str(e)}")

    def run(self):
        resumes = dict()

        # Get the filename
        file_name = self.get_filename()
        resumes["filename"] = file_name

        # Extract text from resume pdf
        raw_text = self.extract_text_from_pdf()
        resumes["raw_text"] = raw_text

        # Insert raw text into DB
        try:
            # Get the id too for foreign key
            resume_id = insert_resumes(resumes)
        except Exception as e:
            print(f"Error inserting into table: {e}")
            return

        # Parse the resume and insert parsed data
        try:
            resume_data = self.parse_resume(raw_text)
            if "error" not in resume_data:
                # Insert into database
                insert_resume_data(resume_id, resume_data)
            return {"resume_id": resume_id, "resume_data": resume_data}
        except Exception as e:
            print(f"Error parsing or inserting resume data:{e}")
            return None

    def get_filename(self):
        """Get the filename of the file"""
        if hasattr(self.file, "filename"):
            return self.file.filename
        """file_path_pathlib = Path(self.pdf_path)
        file_name = file_path_pathlib.name
        return file_name"""

    def extract_text_from_pdf(self):
        """Extract text from pdf file"""
        text = ""
        try:
            reader = PdfReader(self.file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")
        return text

    def parse_resume(self, text):
        """Parse the resume text"""
        try:
            # Validate input
            if not text or len(text.strip()) < 50:
                return {
                    "error": "Resume text too short",
                    "min_length": 50,
                    "received": len(text.strip()) if text else 0
                }

            # Get AI response
            response = self.get_ai_response(text)
            if "error" in response:
                return response

            # Parse and validate
            parsed_data = self.parse_and_validate(response, text)
            if "error" in parsed_data:
                return parsed_data

            return parsed_data

        except Exception as e:
            raise Exception (f"Unexpected error: {e}")

    def get_ai_response(self, text):
        """Get response from OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages= [
                    {
                        "role": "user",
                        "content": self.create_prompt(text)
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            return {"content": response.choices[0].message.content}
        except Exception as e:
            raise Exception (f"OpenAI API error: {e}")

    def parse_and_validate(self, response, original_text):
        """Parse and validate the AI response"""
        try:
            content = self.clean_json_response(response["content"])
            result = json.loads(content)

            # Validate minimum required fields
            # Preprocess text for NLP and regex parsing
            data_preprocessor = DataPreprocessing()
            preprocessed_text = data_preprocessor.text_preprocessing(original_text)
            missing_fields = list()

            if not result.get("name"):
                result["name"] = BackupParser.extract_name(preprocessed_text) or "Not Found"

            if result["name"] == "Not found":
                missing_fields.append("name")

            if not result.get("email"):
                result["email"] = BackupParser.extract_email(preprocessed_text) or "Not Found"

            if result["email"] == "Not found":
                missing_fields.append("email")

            if not result.get("phone"):
                result["phone"] = BackupParser.extract_phone_number(preprocessed_text) or "Not Found"

            if result["phone"] == "Not found":
                missing_fields.append("phone")

            if not result.get("skills"):
                result["skills"] = BackupParser.extract_skills(preprocessed_text)

            if result["skills"] == "Not found":
                missing_fields.append("skills")

            if missing_fields:
                return {
                    "error": "Critical fields missing",
                    "missing_fields": missing_fields,
                    "raw_text_sample": original_text[:200] if original_text else None
                }

            # Clean empty values
            for key in list(result.keys()):
                if result[key] in [None, "", "Not Found", []]:
                    del result[key]

            return result

        except Exception as e:
            raise Exception (f"Parse and validate error: {e}")

    def create_prompt(self, text):
        """Create the prompt for OpenAI"""
        prompt = f"""
        Extract resume information into this EXACT JSON structure. Follow these rules:
        1. Use null for missing fields.
        2. Keep values concise.
        3. Must return valid JSON.
        4. Prioritize finding name and email
        IMPORTANT: Only include actual information found in the resume. DO NOT use example values.
        
        Required structure:
        {{
            "name": "Full name (if found, otherwise null)",
            "email": "Email address (if found, otherwise null)",
            "phone": "Phone number (if found, otherwise null)",
            "location": "Address (if found, otherwise null)",
            "education": [
                {{
                    "institution": "School name (if found)",
                    "degree": Degree (e.g, B.Sc. Computer Science, Bachelor of Engineering)",
                    "field": "Major (if available, otherwise null)",
                    "year": "Graduation year (if available, otherwise null)",
                    "gpa": "GPA (if mentioned, otherwise null)"
                }}
            ],
            "experience": [
                {{
                    "company": "Company name (if found)",
                    "position": "Job title (if found)",
                    "location": "Job location (if available, otherwise null)",
                    "duration": "Time period (e.g 05/2020 - Present)
                    "responsibilities": [
                        (if found, otherwise null)
                        "specific responsibility 1",
                        "specific responsibility 2" ,
                        ...
                    ]
                }}
            ],
            "skills": [e.g "Python", "SQL",...], # must extract real skills from content,
            "certifications": [
                {{
                    "name": "Certification name (if found)",
                    "issuer": "Issuing organization (if available, otherwise null)",
                    "date": "Date obtained (if available, otherwise null)"
                }}
            ],
            "projects": [
                {{
                    "name": "Actual Project name (if found)",
                    "description": "Project description (if available)",
                    "url": Project URL (if available, otherwise null)"
                }}
            ]
        }}
        
        INSTRUCTIONS:
        1. Extract ONLY information present in the resume text.
        2. Leave fields null if not found.
        3. For skills:
            - Look for a 'skills' section
            - Extract all technical/professional skills mentioned
            - Include programming languages, tools, methodologies mentioned
            - Exclude generic terms like 'Teamwork'
        4. For experience:
            - Include location when available (city/country)
        5. For projects:
            - Extract technologies used and URLs when mentioned
        6. For certifications:
            - Include issuer and date when available
        7. Return valid JSON - test your output with json.loads() before returning
        
        Resume Content:
        {text}
        """
        return prompt

    def clean_json_response(self, text):
        """Clean the JSON response from OpenAI"""
        text = re.sub(r'```json|```', '', text)
        # Fix common JSON issues
        text = re.sub(r',\s*([}\]])', r'\1', text)  # Trailing commas
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)  # Control chars

        return text.strip()
