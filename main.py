from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os

app = FastAPI()

# Enable CORS (important for Shopify frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class UserData(BaseModel):
    name: str
    size: str
    color: str


@app.get("/")
def home():
    return {"status": "AI backend running"}


@app.post("/gpt")
def generate_summary(data: UserData):

    prompt = f"""
    Create a short sentence describing a t-shirt order.

    Name: {data.name}
    Size: {data.size}
    Color: {data.color}

    Example:
    User Ali wants a Medium size Red color t-shirt.
    """

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    summary = response.output_text

    return {
        "summary": summary
    }