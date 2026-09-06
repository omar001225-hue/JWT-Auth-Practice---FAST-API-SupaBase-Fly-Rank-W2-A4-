import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase import create_client


load_dotenv()
print(os.getenv("SUPABASE_URL"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PORT = int(os.getenv("PORT", 3000))

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Server running and connected to Supabase")

app = FastAPI()


class UserData(BaseModel):
    email: str
    password: str


@app.post("/auth/signup")
def signup(data: UserData):

    email = data.email
    password = data.password

    if not email or not password:
        return JSONResponse(
            status_code=400,
            content={"error": "Bad Request"}
        )

    response = supabase.auth.sign_up({
        "email": email,
        "password": password
    })

    return JSONResponse(
        status_code=201,
        content={
            "user": {
                "id": response.user.id,
                "email": response.user.email
            }
        }
    )

@app.post("/auth/login")
def login(data: UserData):
    email = data.email
    password = data.password

    if not email or not password:
        return JSONResponse(
            status_code=400,
            content={"error": "Bad Request"}
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        return JSONResponse(
            status_code=200,
            content={
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token
            }
        )

    except Exception as e:
        print("LOGIN ERROR:", e)
        return JSONResponse(
            status_code=401,
            content={"error": str(e)}
        )