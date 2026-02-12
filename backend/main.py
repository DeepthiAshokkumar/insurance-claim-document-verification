from fastapi import FastAPI, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import shutil
import os
from contextlib import asynccontextmanager
from backend.database import SessionLocal, engine
from backend.models import Document, Base
from backend.utils import extract_data_from_image
import json

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Intelligent Document Processing API")

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Templates
templates = Jinja2Templates(directory="frontend/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        # Extract using Gemini
        result = extract_data_from_image(contents)

        # Convert result to string if it's dict
        if isinstance(result, dict):
            extracted_json = json.dumps(result)
        else:
            extracted_json = result

        # 🔽 Save to database
        db = SessionLocal()

        new_doc = Document(
            filename=file.filename,
            extracted_data=extracted_json
        )

        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        db.close()
        # 🔼 Database save complete

        return result

    except Exception as e:
        return {"error": str(e)}


# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     try:
#         conteats = await file.read()
#         # Save locally for reference (optional)
#         # with open(f"uploads/{file.filename}", "wb") as buffer:
#         #     shutil.copyfileobj(file.file, buffer)
        
#         # Process directly from memory
#         result = extract_data_from_image(conteats)
#         return result
#     except Exception as e:
#         return {"error": str(e)}

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
