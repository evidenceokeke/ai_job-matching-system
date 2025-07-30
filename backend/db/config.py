import os
from dotenv import load_dotenv

# ------ POSTGRESQL CONFIGURATION -----

load_dotenv()

def load_config():
    """Load database configuration from .env file"""
    try:
        db_config = {
            "host": os.getenv("DB_HOST"),
            "database": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "port": os.getenv("DB_PORT")
        }

        # Validate the configuration
        if not all(db_config.values()):
            missing = [key for key, value in db_config.items() if not value]
            raise Exception(f"Missing database configuration : {', '.join(missing)}")
        return db_config
    except Exception as e:
        raise Exception(f"Error loading database configuration: {e}")

if __name__ == '__main__':
    config = load_config()
    print(config)
