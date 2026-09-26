import os
from dotenv import load_dotenv

# STAGE 4:
# Added Depends and HTTPException for the reusable authentication guard.
# Request is used for the custom error response format.
from fastapi import FastAPI, Header, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # Stage 5 
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase import create_client


# ============================================================
# SAME AS STAGE 3
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PORT = int(os.getenv("PORT", 3000))


# SAME AS STAGE 3
# Connect to Supabase when the server starts
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Server running and connected to Supabase")

app = FastAPI()

# ============================================================
# STAGE 5 — SWAGGER BEARER AUTHENTICATION
# ============================================================

# Tells FastAPI/Swagger that our API uses Bearer tokens.
# This creates the Authorize 🔒 button in Swagger UI.


security = HTTPBearer()

# ============================================================
# STAGE 4
# ============================================================

# This makes HTTPException return:
#
# {
#     "error": "Access token required"
# }
#
# instead of FastAPI's default:
#
# {
#     "detail": "Access token required"
# }

# Stage 5 also makes Swagger recognize these routes
# as requiring Bearer authentication.


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


# ============================================================
# SAME AS STAGE 3
# ============================================================

class UserData(BaseModel):
    email: str
    password: str


# ============================================================
# STAGE 4 — REUSABLE AUTHENTICATION GUARD
# ============================================================

# This contains the authentication logic from Stage 3.
#
# In Stage 3, this logic was written specifically for
# /protected/profile.
#
# In Stage 4, we turned it into a reusable dependency.
#
# Any protected route can now use:
#
#     Depends(get_current_user)
#
# without writing the token-checking code again.

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    # Get the actual JWT token.
    #
    # Example:
    #
    # Authorization: Bearer eyJhbGciOi...
    #
    # credentials.credentials contains:
    #
    # eyJhbGciOi...

    token = credentials.credentials

    # Verify token with Supabase
    try:

        response = supabase.auth.get_user(token)

        # Return authenticated user
        return response.user

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# ============================================================
# SIGN UP — SAME AS STAGE 3
# ============================================================

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


# ============================================================
# LOGIN — SAME AS STAGE 3
# ============================================================

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


# ============================================================
# PUBLIC ROUTE — SAME AS STAGE 3
# ============================================================

@app.get("/public/info")
def show_message():

    return JSONResponse(
        status_code=200,
        content={
            "message": "Welcome stranger! This info is public."
        }
    )


# ============================================================
# PROTECTED PROFILE — STAGE 3 LOGIC REUSED IN STAGE 4
# ============================================================

@app.get("/protected/profile")

# STAGE 4 CHANGE:
# Instead of manually checking the token inside this route,
# FastAPI runs get_current_user() first.
#
# If the token is invalid:
#     Route does NOT run → 401
#
# If the token is valid:
#     user is passed into this function.

def protected_profile(user=Depends(get_current_user)):

    # SAME RESPONSE AS STAGE 3
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }


# ============================================================
# STAGE 4 — SECOND PROTECTED ROUTE
# ============================================================

@app.get("/protected/dashboard")

# STAGE 4:
# SAME authentication guard.
#
# NO NEW AUTHENTICATION CODE.
#
# This is the main checkpoint of Stage 4.

def dashboard(user=Depends(get_current_user)):

    return {
        "message": "Welcome to the dashboard"
    }


# ============================================================
# STAGE 4 — LOGOUT
# ============================================================

@app.post("/auth/logout")

# STAGE 4:
# Logout is also protected.
#
# The user must have a valid access token before
# the logout function is allowed to run.

def logout(user=Depends(get_current_user)):

    # STAGE 4:
    # Sign the user out using Supabase.
    supabase.auth.sign_out()

    # STAGE 4:
    # 204 means:
    # "Request succeeded, but there is no response body."

    return JSONResponse(
        status_code=204,
        content=None
    )
