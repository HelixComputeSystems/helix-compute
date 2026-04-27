from fastapi import FastAPI
import os
from examples.run_api import run_demo

app = FastAPI()

@app.get("/demo")
def demo():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "AEP_hourly.json")

    return run_demo(file_path)