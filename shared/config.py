import os
from dotenv import load_dotenv

# ---------- OPENAI CONFIGURATION -------

load_dotenv()


class Config:
    @staticmethod
    def get_api_key():
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key not found."
                "Please set it in .env file or environment variables."
            )
        return api_key

    MODEL_NAME = "gpt-3.5-turbo"
    MAX_TOKENS = 3000
    TEMPERATURE = 0.1
