# PDF-Chatbot

This project is a web-based chatbot application that allows users to upload PDF documents and ask questions related to their content. The backend is built with FastAPI and leverages Langchain with Groq for Large Language Model (LLM) powered question answering and ChromaDB for in-memory vector storage. The frontend is a simple HTML, CSS, and JavaScript interface.

## Features

*   Upload PDF documents.
*   Ask questions about the content of the uploaded PDF.
*   View chat history (questions and answers).
*   Clear chat history for the current PDF.
*   Upload a new PDF, which resets the context.
*   Utilizes Retrieval Augmented Generation (RAG) for answering questions based on the PDF content.
*   Custom prompt templating to guide the LLM's responses.

## Tech Stack

*   **Backend:**
    *   Python 3.11
    *   FastAPI (for an efficient and modern API)
    *   Uvicorn (ASGI server)
    *   Langchain (framework for LLM applications)
    *   Groq (for fast LLM inference)
    *   Sentence-Transformers (for text embeddings)
    *   ChromaDB (in-memory vector store)
    *   PyPDF2 (for PDF text extraction)
    *   python-dotenv (for environment variable management)
*   **Frontend:**
    *   HTML
    *   CSS
    *   JavaScript
*   **Containerization:**
    *   Docker
    *   Docker Compose

## Prerequisites

Before you begin, ensure you have the following installed on your system:
*   [Git](https://git-scm.com/downloads)
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) (which includes Docker Engine and Docker Compose)

## Getting Started

Follow these steps to get the application running locally using Docker.

### 1. Clone the Repository

Clone this repository to your local machine:
```bash
git clone https://github.com/AbdulAhad2659/PDF-Chatbot
cd PDF-Chatbot
```
Install requisite libraries by running in the terminal:
```bash
pip install -r requirements.txt

```

### 2. Build and Run with Docker Compose

Docker Compose is the recommended way to build and run the application as it handles the image building and container setup defined in `docker-compose.yml` and `Dockerfile`.

From the root directory of the project, run:
```bash
docker-compose up --build
```
This command will build the Docker image for the app service and then start the container. You will see logs from the application in your terminal.

### 3. Access the Application

Once the container is running and you see output similar to this in your terminal:
```text
app_1  | FastAPI application startup complete.
app_1  | GROQ_API_KEY found.
app_1  | Using embedding model: all-MiniLM-L6-v2
app_1  | Using Groq model: llama3-70b-8192
app_1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```
Open your web browser and navigate to:
```text
http://localhost:8000
```
Or, you can access the deployed application by going to the following address:
```text
http://52.45.76.247:8000/
```

You should now be able to use the PDF Question Answering Chatbot.

### Stopping the Application
To stop the application, press CTRL+C in the terminal where docker-compose up is running.
To remove the containers (if you ran docker-compose up -d previously or want to clean up):
```bash
docker-compose down
```

### Project Structure
```text
.
├── Dockerfile              # Defines the Docker image for the application
├── docker-compose.yml      # Defines services, networks, and volumes for Docker
├── frontend/               # Contains static frontend files
│   ├── index.html          # Main HTML page
│   ├── script.js           # Client-side JavaScript
│   └── styles.css          # CSS styles
├── main.py                 # FastAPI application, API endpoints
├── pdf_rag.py              # Core RAG logic, PDF processing, LLM interaction
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (e.g., API keys)
└── README.md               # This file
```
### Environment Variables
The application uses the following environment variables:
```text
GROQ_API_KEY
```
Your API key for accessing Groq LLM services. This must be set in the .env file or passed directly to the Docker container.
