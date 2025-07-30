from spacy.matcher import Matcher
from pathlib import Path
import re
import spacy

class BackupParser:
    """Handles PDF text extraction and NLP and regex parsing when AI parser does not work"""
    def __init__(self):
        self.skills_file = Path(r"/resume_parser/patterns/skill_patterns.jsonl")
        self.education_file = Path(r"/resume_parser/patterns/education_patterns.jsonl")

        # Load spaCy and add EntityRuler before processing text
        self.nlp = spacy.load("en_core_web_sm")

        # Initialize matcher with a vocab
        self.matcher = Matcher(self.nlp.vocab)

        # Add Entity Ruler to pretrained model
        if "skill_ruler" not in self.nlp.pipe_names:
            self.skill_ruler = self.nlp.add_pipe("entity_ruler", name="skill_ruler", before="ner")
            self.skill_ruler.from_disk(self.skills_file)

    def extract_name(self, text):
        """Extract name from resume text"""
        nlp_text = self.nlp(text)

        # First name and Last name are always proper nouns
        pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]

        self.matcher.add('NAME', [pattern])

        matches = self.matcher(nlp_text)

        for match_id, start, end in matches:
            span = nlp_text[start:end]
            return span.text

    def extract_phone_number(self, text):
        """Extract phone number from resume text"""
        phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|'
                                      r'[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9]'
                                      r'[02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*'
                                      r'(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
        if phone:
            number = ''.join(phone[0])
            if len(number) > 10:
                return '+' + number
            else:
                return number

    def extract_email(self, text):
        """Extract email address from resume text"""
        email = re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", text)
        if email:
            try:
                return email[0].split()[0].strip(';')
            except IndexError:
                return None

    def extract_skills(self, text):
        """Extract skills from resume text using NLP patterns"""
        skill_matches = list()
        doc = self.nlp(text)

        for ent in doc.ents:
            if ent.label_.startswith("SKILL"):
                skill_matches.append(ent.text)
        return list(set(skill_matches))

"""def main(path_to_file):
    # Read the file and convert to image

    # print(extracted_text[0])

    # Extract text from file
    extracted_text = extract_text_from_pdf(pdf_file)

    #raw_text = "\n".join(extracted_text)

    # Add to dictionary
    resume_data["raw_text"] = extracted_text

    # Get the file name
    file_path_pathlib = Path(pdf_file)
    file_name = file_path_pathlib.name

    # Add to dictionary
    resume_data["filename"] = file_name

    # Preprocess text
    processed_tokens = text_preprocessing(extracted_text)
    processed_text = " ".join(processed_tokens)

    # Add to resume_data dictionary
    resume_data["processed_text"] = processed_text

    # Extract name
    extracted_name = extract_name(extracted_text)

    # Add to parsed_data dictionary
    parsed_data["name"] = extracted_name

    # Extract phone number
    extracted_num = extract_phone_number(extracted_text)

    # Add to parsed_data dictionary
    parsed_data["phone_number"] = extracted_num

    # Extract email address
    extracted_email = extract_email(extracted_text)

    # Add to parsed_data dictionary
    parsed_data["email"] = extracted_email

    # Extract skills
    extracted_skills = extract_skills(extracted_text)

    # Add to parsed_data dictionary
    parsed_data["skills"] = extracted_skills

    # Extract education
    extracted_edu = extract_education(extracted_text)

    # Add to parsed_data dictionary
    parsed_data["education"] = extracted_edu

    # Add to parsed_data to resume_data dictionary
    resume_data["parsed_data"] = parsed_data

    return resume_data

# Should have a dictionary of the resume data i can now insert to the database

if __name__ == '__main__':
    main(pdf_file)
    print(resume_data)
"""