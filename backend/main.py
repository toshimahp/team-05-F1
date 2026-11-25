from fastapi import FastAPI, HTTPException, Header
import function
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)

ROLE= ["admin", "organizer" , "driver"]

#E1 - E5

#E1 : create organizer account
@app.post("/organizer_account")
def create_organizer_account (username, password):
    result = function.create_organizer_account(username=username, password=password)
    
#E6 - E10



#E11 - E15