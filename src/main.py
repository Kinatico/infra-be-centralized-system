import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Post(BaseModel):
    userId: int
    id: int
    title: str
    body: str


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/data", response_model=list[Post])
def call_external_api():
    url = "https://jsonplaceholder.typicode.com/posts"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print("Data received from external API:", data)
        return data
    except requests.exceptions.RequestException as e:
        print("Failed to retrieve data.", str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch data from external API")