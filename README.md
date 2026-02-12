# Insurance claim document verification

This project is a scaffold for an Intelligent Document Processing System using FastAPI and Google Gemini.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables:**
    - Rename `.env.example` to `.env`.
    - Add your Google Gemini API Key to `.env`:
      ```
      GOOGLE_API_KEY=your_actual_api_key_here
      ```

## Running the Application

1.  **Start the Server:**
    ```bash
    python backend/main.py
    ```
    Or directly with uvicorn:
    ```bash
    uvicorn backend.main:app --reload
    ```

2.  **Access the Interface:**
    - Open your browser and navigate to `http://localhost:8000`.

## Architecture

-   **Backend:** FastAPI (`backend/main.py`) handles file uploads and acts as a proxy to the LLM.
-   **Extraction:** `backend/utils.py` uses Google's Generative AI to extract structured JSON from images.
-   **Frontend:** Simple HTML/JS (`frontend/templates/index.html`) and CSS (`frontend/static/style.css`) for uploading and viewing results.
