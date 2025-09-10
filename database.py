import os
import pymongo
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def connect_to_mongo():
    """
    Establishes a connection to the MongoDB Atlas cluster.
    Returns the database object if successful, None otherwise.
    """
    mongo_uri = os.getenv("MONGO_URI")
    
    if not mongo_uri:
        print("MONGO_URI not found in environment variables.")
        return None
        
    try:
        client = pymongo.MongoClient(mongo_uri)
        # Ping the server to confirm a successful connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB Atlas!")
        
        # Select your database (it will be created if it doesn't exist)
        db = client['JobFitPoC']
        return db
        
    except pymongo.errors.ConfigurationError as e:
        print(f"Configuration Error: Could not connect to MongoDB. Check your connection string. Details: {e}")
        return None
    except pymongo.errors.ConnectionFailure as e:
        print(f"Connection Failure: Could not connect to MongoDB. Details: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def save_analysis_data(db, job_description, candidate_profile, analysis_result):
    """
    Saves the JD, candidate profile, and analysis result to MongoDB.
    """
    if db is None:
        print("Database connection is not available. Cannot save data.")
        return False
        
    try:
        # Get collections (they will be created if they don't exist)
        jd_collection = db['job_descriptions']
        candidate_collection = db['candidate_profiles']
        
        # Insert the documents
        jd_collection.insert_one(job_description)
        candidate_collection.insert_one(candidate_profile)
        
        print("Job Description and Candidate Profile saved successfully.")
        return True
        
    except Exception as e:
        print(f"An error occurred while saving data to MongoDB: {e}")
        return False