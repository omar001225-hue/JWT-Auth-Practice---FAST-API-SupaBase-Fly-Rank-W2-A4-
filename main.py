import os
from dotenv import load_dotenv
from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase import create_client


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PORT = int(os.getenv("PORT", 3000))

# Connect to Supabase when the server starts
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


@app.get("/public/info")
def show_message():
    return JSONResponse(
        status_code=200,
        content={
            "message": "Welcome stranger! This info is public"
        }
    )


@app.get("/protected/profile")
def protected_profile(
    authorization: str | None = Header(default=None)
):
    # First, make sure the client actually sent the header
    print("AUTHORIZATION:", authorization)

    if not authorization:
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"}
        )

    # We only accept the format: Bearer <token>
    if not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"}
        )

    # Remove "Bearer " and keep only the token
    token = authorization[7:].strip()

    if not token:
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"}
        )

    # Token verification will be added later
    return {
        "message": "Protected profile accessed",
        "token": token
    }
