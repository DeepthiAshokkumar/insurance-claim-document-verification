import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure the API key
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def extract_data_from_image(image_bytes):
    """
    Extracts structured data from an image using a multimodal LLM.
    """
    if not API_KEY:
        return {
            "error": "API Key not found. Please set GOOGLE_API_KEY in .env file.",
            "raw_response": None
        }

    # List of models to try in order of preference
    # Based on available models: gemini-2.0-flash, gemini-2.5-flash, gemini-flash-latest
    candidate_models = [
        'gemini-2.0-flash',
        'gemini-2.5-flash',
        'gemini-flash-latest',
        'gemini-2.5-pro',
        'gemini-exp-1206' 
    ]

    model = None
    last_error = None

    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            # Test if model is supported by generating dummy content (dry run not really possible without cost, 
            # but we can trust the instantiation or catch generation error)
            break
        except Exception as e:
            last_error = e
            continue

    if not model:
         # If simpler instantiation didn't fail but generation might, we handle it in the generation block
         # But here we default to the first one if all failed instantiation (unlikely)
         model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = """
    You are an intelligent document processing system.
    Task: Extract ONLY the following relevant structured field data from this Motor Insurance Claim Form.
    
    Instructions:
    1. Extract ONLY these specific fields:
       - Policy Number
       - Claim Number
       - Vehicle Number
       - Insured Name
       - Insured Mobile
       - Insured Email
       - Date of Accident
       - Place of Accident
       - Type of Loss
       - Driver Name
       - Driving License No
    
    2. IGNORE detailed address breakdowns, corporate office details, RTO names, and other minor checkboxes unless critical.
    3. If one of the above requested fields is empty/blank, set "value": null.
    4. "missing_fields" must list any of the above fields that are null.
    
    Output JSON structure:
    {
      "document_type": "Motor Insurance Claim Form",
      "fields": { "field_name": { "value": "string/null", "confidence": "high/medium/low" } },
      "missing_fields": ["field1"],
      "unrecognized_text": []
    }
    """

    try:
        # We need to wrap the generation in a loop too if the error happens during generation
        # (which is when the 404 actually happens usually)
        
        response = None
        for model_name in candidate_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content([
                    {'mime_type': 'image/jpeg', 'data': image_bytes},
                    prompt
                ])
                break # Success
            except Exception as e:
                # Capture the error and try the next model
                last_error = e
                print(f"Model {model_name} failed: {e}")
                continue
        
        if not response:
            return {"error": f"All models failed. Last error: {str(last_error)}"}

        # Clean up the response to ensure it's valid JSON
        text_response = response.text
        # Remove markdown code blocks if present
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
        
        data = json.loads(text_response)

        # Post-processing: Ensure missing_fields is populated if value is null
        if "fields" in data:
            if "missing_fields" not in data:
                data["missing_fields"] = []
            
            for field_name, field_data in data["fields"].items():
                if field_data.get("value") is None or field_data.get("value") == "":
                    if field_name not in data["missing_fields"]:
                        data["missing_fields"].append(field_name)
        
        return data

    except Exception as e:
        return {"error": str(e)}
