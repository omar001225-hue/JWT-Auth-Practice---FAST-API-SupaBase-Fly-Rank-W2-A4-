import os

from dotenv import load_dotenv
from fastapi import FastAPI
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PORT = int(os.getenv("PORT", 3000))

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

print("Server running and connected to Supabase")