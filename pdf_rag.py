# Import libraries

import os
import PyPDF2
from dotenv import load_dotenv
import uuid  # For generating unique IDs
from langchain_core.documents import Document
from langchain.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

load_dotenv()

# Configuration
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
GROQ_MODEL_NAME = "llama3-70b-8192"

# Custom Prompt Template
custom_prompt_template_str = """You are a helpful AI assistant designed to answer questions based on the provided context.
Use only the following pieces of context to answer the question at the end.
If the context does not contain the answer to the question, explicitly state that the information is not available in the provided document.
Do not make up an answer or use external knowledge.
Answer concisely and directly.

Context:
{context}

Question: {question}

Helpful Answer:"""

CUSTOM_QA_PROMPT = PromptTemplate(
    template=custom_prompt_template_str, input_variables=["context", "question"]
)

# Global variables
conversation_chain = None
vector_store = None  # This will hold the Chroma instance for the latest pdf


def initialize_groq_llm():
    """Initializes the Groq LLM."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY environment variable not set.")
    return ChatGroq(temperature=0.1, groq_api_key=api_key, model_name=GROQ_MODEL_NAME)


def load_and_process_pdf(pdf_path: str):
    """
    Loads a PDF, processes its text, creates embeddings, stores them in an
    in-memory vector store under a unique collection name.
    """
    global vector_store, conversation_chain

    # 1. Load PDF Text
    text = ""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            if not pdf_reader.pages:
                raise ValueError("PDF contains no pages.")
            for page_num, page in enumerate(pdf_reader.pages):
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text

        if not text.strip():
            raise ValueError("No text could be extracted from the PDF. It might be corrupted or image-based.")

        text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
        docs = [Document(page_content=text)]
    except Exception as e:
        print(f"Error during PDF loading: {e}")
        raise Exception(f"Error loading or initially processing PDF: {e}")

    # 2. Chunk Text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Characters per chunk
        chunk_overlap=150  # Overlap between chunks
    )
    split_docs = text_splitter.split_documents(docs)
    if not split_docs:
        raise ValueError("Text splitting resulted in no document chunks. Check PDF content.")
    print(f"PDF text split into {len(split_docs)} chunks.")

    # 3. Embed Text and Store in In-Memory Chroma
    try:
        embedding_model = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        current_collection_name = f"pdf_collection_{uuid.uuid4().hex}"
        print(f"Creating new in-memory Chroma collection: {current_collection_name}")

        vector_store = Chroma.from_documents(
            documents=split_docs,
            embedding=embedding_model,
            collection_name=current_collection_name
        )
        print(f"In-memory vector store '{current_collection_name}' created with {len(split_docs)} embedded chunks.")

    except Exception as e:
        import traceback
        print(f"Error during embedding or ChromaDB in-memory storage: {traceback.format_exc()}")
        raise Exception(f"Error during embedding or ChromaDB in-memory storage: {e}")

    # 4. Initialize a new Conversational Retrieval Chain with the custom prompt
    llm = initialize_groq_llm()
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={'k': 3}  # Retrieve top 3 relevant chunks
    )

    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True,
        output_key='answer'
    )

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=False,
        combine_docs_chain_kwargs={"prompt": CUSTOM_QA_PROMPT}
    )
    print(f"ConversationalRetrievalChain re-initialized for PDF '{os.path.basename(pdf_path)}' with custom prompt.")
    return f"PDF '{os.path.basename(pdf_path)}' processed. Ready for questions."


def get_answer_from_chain(question: str):
    """
    Gets an answer from the currently active chain.
    """
    global conversation_chain
    if not conversation_chain:
        return "Error: Please upload and process a PDF first."
    try:
        result = conversation_chain.invoke({"question": question})
        answer = result.get('answer', "Sorry, I couldn't generate an answer based on the provided document.")
        return answer
    except Exception as e:
        import traceback
        print(f"Error during chain invocation: {traceback.format_exc()}")
        raise Exception(f"Error generating answer: {e}")


def clear_conversation_memory():
    """Clears the memory of the current conversation."""
    global conversation_chain
    if conversation_chain and hasattr(conversation_chain, 'memory') and conversation_chain.memory:
        try:
            conversation_chain.memory.clear()
            print("Conversation memory cleared successfully for the current document.")
            return True
        except Exception as e:
            print(f"Error clearing conversation memory: {e}")
            return False
    else:
        print("No active conversation chain with memory to clear (or PDF not yet loaded).")
        return True
