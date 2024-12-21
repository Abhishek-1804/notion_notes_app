# For testing run this docker command: docker run --rm -v "$(pwd):/app" -w /app python:3.9-slim bash -c "
#     apt-get update && apt-get install -y gcc python3-dev libffi-dev && \
#     pip install --upgrade pip setuptools wheel && \
#     pip install openai python-dotenv && \
#     python3 testing.py
# "

from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)

print(completion.choices[0].message.content)
