import json
import psycopg2
import pandas as pd
import re
from backend.db.config import load_config
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ------ PREPROCESSING DATA FOR ANALYSIS AND ML TRAINING -------

# Necessary downloads for NLTK
#.download("stopwords")
#nltk.download("punkt_tab")
#nltk.download("wordnet")

class DataPreprocessing:
    """Functions to preprocess data and Feature Extraction"""
    # I'm thinking of having maybe like an init function but does it require it?

    @staticmethod
    def get_data_from_db(columns, table_name):
        """Fetch data from database
        columns is a list of columns to find
        table_name is a string of the table to find it in"""
        config = load_config()
        column_str = ", ".join(columns)
        try:
            with psycopg2.connect(**config) as conn:
                with conn.cursor() as cur:
                    query = f"SELECT {column_str} FROM {table_name};"
                    cur.execute(query)
                    rows = cur.fetchall() # returns a list of tuple

                    # Create an empty Dataframe
                    df = pd.DataFrame(rows, columns=columns)
                    return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error getting data from {table_name}: ",error)
            return pd.DataFrame()

    @staticmethod
    def remove_special_characters(text):
        """Removes special characters and punctuation from text"""
        return re.sub(r'[^a-zA-Z0-9\s]', '', str(text))

    @staticmethod
    def preprocess_data(df, columns):
        """Clean the data"""
        # Remove special characters and punctuation from the data
        # Convert to lowercase
        #columns = ["title", "description"]
        for column in columns:
            df[column] = df[column].apply(DataPreprocessing.remove_special_characters)
            df[column] = df[column].str.lower()

        # Fill every missing value in the table
        df.fillna("not specified", inplace=True)

        return df

    @staticmethod
    def text_preprocessing(text):
        """Prepare text data for analysis and search"""

        # Tokenize the text, word
        token = word_tokenize(text)

        # Remove stopwords
        stop_words = set(stopwords.words(["english", "french"]))
        filtered_list = []
        for word in token:
            if word.casefold() not in stop_words:
                filtered_list.append(word)

        # Lemmatize the words
        lemmatizer = WordNetLemmatizer()
        lemmatized_words = []

        for word in filtered_list:
            lemmatized_words.append(lemmatizer.lemmatize(word))

        return lemmatized_words

    @staticmethod
    def extract_salary_range(salary):
        """Feature Extraction: Extract min salary, max salary and frequency from salary column"""
        if not salary or salary.lower() == "not specified":
            return None, None, None

        # Identify salary frequency
        frequency = None
        if "year" in salary:
            frequency = "year"
        elif "month" in salary:
            frequency = "month"
        elif "hour" in salary:
            frequency = "hour"

        # Extract the salary values
        salaries = re.findall(r'\$\s*[\d,]+(?:\.\d+)?|\d+(?:,\d{3})*(?:\.\d+)?\s*(?:dollars|USD|CAD)', salary, re.IGNORECASE)

        # Clean and convert extracted salaries to integers
        salaries_cleaned = [float(re.sub(r"[$,USD,CAD\s]", "", salary)) for salary in salaries]

        min_salary = min(salaries_cleaned)
        max_salary = max(salaries_cleaned)

        return min_salary, max_salary, frequency

    #REMOVE METHOD LATER
    @staticmethod
    def save_preprocessed_data(df):
        """Save preprocessed data as JSON for ML model and analysis"""

        preprocessed_text_data = df[["id", "title", "description"]].copy()

        # Convert to JSON file
        output_path = "preprocessed_data.json"
        with open(output_path, "w") as file:
            json.dump(preprocessed_text_data.to_dict(orient="records"), file, indent=4)

        print(f"Preprocessed text data saved to {output_path}")

"""def main():
    # Get job data
    job_data = get_jobs()

    #print(job_data.head(1))

    # Preprocess the data
    preprocessed_data = preprocess_data(job_data)

    # Now preprocess the title and description column for NLP
    columns = ["title", "description"]
    for column in columns:
        preprocessed_data[column] = preprocessed_data[column].apply(text_preprocessing)

    # Feature Extraction for Salary Range
    # Create a new table (dataframe) and add the job id column to it
    salary_range = preprocessed_data[["id"]].copy()
    salary_range[['min_salary', 'max_salary', 'frequency']] = preprocessed_data['salary'].apply(extract_salary_range).apply(pd.Series)

    # Check the salary_range DataFrame before insertion
    print(salary_range.head())

    # Save dataframe to database
    salary_range_feature(salary_range)

    # Save the preprocessed text and description in a new dataframe and save as a json file for ML
    save_preprocessed_data(preprocessed_data)

    print("Data preprocessing completed successfully.")"""


"""if __name__ == '__main__':
    main()"""

