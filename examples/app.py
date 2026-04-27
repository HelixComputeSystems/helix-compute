from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from examples.run_api import run_demo

app = FastAPI()

# ✅ CORS FIX (this is what enables your website to call the API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for now (safe for demo)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/demo")
def demo():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "AEP_hourly.json")

    return run_demo(file_path)