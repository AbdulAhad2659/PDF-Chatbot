# Import libraries

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

# Import functions and constants from pdf_rag file
from pdf_rag import (
    load_and_process_pdf,
    get_answer_from_chain,
    clear_conversation_memory,
    EMBEDDING_MODEL_NAME,
    GROQ_MODEL_NAME
)

load_dotenv()

app = FastAPI(title="PDF Question Answer Chatbot")

# Configure CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the 'frontend' directory to serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")


# API Endpoints

@app.post("/upload_pdf/", response_model=dict)
async def upload_pdf_endpoint(file: UploadFile = File(...)):
    """
    Uploads a PDF file, processes it, and prepares it for question answering.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid MIME type. Please upload a PDF file.")

    # Create temporary file to store pdf contents
    temp_pdf_path = f"temp_{file.filename}"
    try:
        pdf_content = await file.read()
        if not pdf_content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        with open(temp_pdf_path, "wb") as temp_file:
            temp_file.write(pdf_content)

        message = load_and_process_pdf(temp_pdf_path)
        return {"message": message}

    except ValueError as ve:
        print(f"ValueError processing PDF: {ve}")

        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        print(f"Unexpected error processing PDF: {e}")

        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)


@app.post("/ask_question/", response_model=dict)
async def ask_question_endpoint(question: str = Form(...)):
    """
    Asks a question about the currently processed PDF.
    """
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        answer = get_answer_from_chain(question)
        return {"answer": answer}

    except Exception as e:
        print(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")


@app.post("/clear_chat/", response_model=dict)
async def clear_chat_endpoint():
    """Clears the chat history."""
    try:
        if clear_conversation_memory():
            return {"message": "Chat history cleared successfully."}
        else:
            return JSONResponse(status_code=409,
                                content={"detail": "Could not clear chat history or no active session."})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error clearing chat history: {str(e)}")



# Serve index.html at the root path
@app.get("/", response_class=FileResponse)
async def read_index():
    return "frontend/index.html"

# Starting the Fastapi app
@app.on_event("startup")
async def startup_event():
    print("FastAPI application startup complete.")
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        print("WARNING: GROQ_API_KEY environment variable is not set.")
    else:
        print("GROQ_API_KEY found.")
    print(f"Using embedding model: {EMBEDDING_MODEL_NAME}")
    print(f"Using Groq model: {GROQ_MODEL_NAME}")
