import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("DUMMYJSON_USERNAME")
PASSWORD = os.getenv("DUMMYJSON_PASSWORD")

BASE_URL = "https://dummyjson.com"

PAGE_SIZE = 10