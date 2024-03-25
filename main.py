from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore

app = FastAPI()

# Mount static and templates directories
app.mount('/static', StaticFiles(directory='static'), name='static') 
templates = Jinja2Templates(directory="templates")

# Initialize Firestore client
db = firestore.Client()

# Firebase authentication setup
firebase_request_adapter = requests.Request()

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    id_token = request.cookies.get("token")
    error_message = "No error here"
    user_token = None

    # Verify Firebase token if available
    if id_token:
        try:
            user_token = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as err:
            error_message = str(err)

    return templates.TemplateResponse('main.html', {'request': request, 'user_token': user_token, 'error_message': error_message})

# Endpoint to render the page for adding EV
@app.get("/add_ev_page", response_class=HTMLResponse)
async def add_ev_page(request: Request):
    return templates.TemplateResponse('add_ev_page.html', {'request': request})

# Endpoint to add EV data
@app.post("/add_ev/")
async def add_ev(request: Request):
    data = await request.form()
    ev_data = {
        "make": data["make"],
        "model": data["model"],
        "year": data["year"],
        "color": data["color"]
    }

    # Add EV data to Firestore
    db.collection('electric_vehicles').add(ev_data)

    return {"message": "EV data added successfully"}
