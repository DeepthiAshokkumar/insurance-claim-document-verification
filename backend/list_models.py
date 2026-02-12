import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("Error: GOOGLE_API_KEY not found.")
else:
    genai.configure(api_key=API_KEY)
    try:
        with open("models_list.txt", "w", encoding="utf-8") as f:
            f.write("Listing ALL available models:\n")
            for m in genai.list_models():
                f.write(f"- {m.name}\n")
                f.write(f"  Supported methods: {m.supported_generation_methods}\n")
        print("Models written to models_list.txt")
    except Exception as e:
        print(f"Error listing models: {e}")
