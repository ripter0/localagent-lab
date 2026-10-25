from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from config import settings
import os

# Create directories if they don't exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("data", exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def root():
    """Redirect to home page"""
    return RedirectResponse(url="/home")

@app.get("/home")
def home_page():
    """Home page with reporting form"""
    return templates.TemplateResponse("index.html", {"request": None})

@app.get("/about")
def about_page():
    """About page"""
    return templates.TemplateResponse("about.html", {"request": None})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)