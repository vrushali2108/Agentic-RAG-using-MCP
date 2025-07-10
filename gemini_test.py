import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env variables
load_dotenv()

# Configure with the Gemini API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ Use v1 models like this:
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

response = model.generate_content("What's the capital of France?")
print(response.text)
