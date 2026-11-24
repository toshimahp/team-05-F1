from fastapi import FastAPI, HTTPException, Header
import functions
from fastapi.middleware.cors import CORSMiddleware
from model import RegisterRequest, LoginRequest, FeedbackCreate

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"]
)

ROLE= ["admin", "organizer" , "driver"]