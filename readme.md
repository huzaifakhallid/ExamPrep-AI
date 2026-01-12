# ExamPrep AI: Intelligent Assessment Generation Engine

ExamPrep AI is an end-to-end Retrieval-Augmented Generation (RAG) application designed to automate the creation of educational assessments. By ingesting unstructured data from lecture slides and documents, the system generates scenario-based case studies and objective questions using Large Language Models (LLMs).

This project demonstrates a full-stack AI engineering workflow, including document ingestion, vector database management, prompt engineering, and API development.

## Project Overview

**The Problem:** Creating high-quality, scenario-based exam questions from lecture materials is time-consuming and often lacks depth when done manually.

**The Solution:** ExamPrep AI allows users to upload course materials (PDF, PPTX, DOCX). It extracts the textual content, indexes it semantically using vector embeddings, and uses a Fine-Tuned LLM (Mistral-7B) to synthesize realistic case studies and corresponding multiple-choice questions (MCQs) with an answer key.

## Key Features

*   **Multi-Format Document Ingestion:** Robust extraction pipeline supporting PDF, PowerPoint, and Word documents.
*   **Semantic Search (RAG):** Utilizes FAISS (Facebook AI Similarity Search) to retrieve the most relevant context for question generation, reducing model hallucinations.
*   **Scenario-Based Evaluation:** Engineered to produce higher-order thinking questions (application/analysis level) rather than simple rote memorization queries.
*   **Modular Architecture:** Decoupled backend (FastAPI) and frontend (Streamlit) ensuring scalability and separation of concerns.
*   **Sanitized Output:** Implements post-processing logic to ensure clean, structured output from the LLM, preventing generation loops.

## Technical Architecture

The application follows a standard RAG pipeline architecture:

1.  **Ingestion Layer:** Uses `PyMuPDF` and `python-pptx` to parse raw binary files into text.
2.  **Preprocessing:** Cleans text and splits it into manageable chunks (500 tokens) to optimize context window usage.
3.  **Embedding & Retrieval:**
    *   Model: `sentence-transformers/all-MiniLM-L6-v2`
    *   Database: FAISS (Vector Store)
4.  **Generation Layer:**
    *   Model: `Mistral-7B-Instruct-v0.2` (via Hugging Face Inference API)
    *   Technique: Chain-of-Thought Prompting with strict constraint enforcement.
5.  **Application Layer:**
    *   Backend: FastAPI (Async REST Endpoints)
    *   Frontend: Streamlit (Reactive UI with custom CSS styling)

## Technology Stack

*   **Language:** Python 3.9+
*   **API Framework:** FastAPI, Uvicorn
*   **Interface:** Streamlit
*   **AI/ML Libraries:** PyTorch (via HuggingFace), FAISS, Sentence-Transformers, NumPy
*   **Data Processing:** PyMuPDF (Fitz), python-docx, python-pptx

## Installation and Usage

Follow these steps to deploy the application locally.

### Prerequisites
*   Python 3.8 or higher
*   A Hugging Face API Token (Free Tier)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ExamPrep-AI.git
cd ExamPrep-AI
```
### 2. Set Up Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
Create a file named `.env` in the root directory and add your API key:

```env
HF_API_KEY=your_huggingface_token_here
```

### 5. Running the Application
The application requires two services running concurrently. Open two terminal windows:

**Terminal 1 (Backend API):**
```bash
uvicorn app:app --reload
```
*The API will start at http://127.0.0.1:8000*

**Terminal 2 (Frontend UI):**
```bash
streamlit run frontend.py
```
*The UI will launch automatically in your default browser at http://localhost:8501*

## Project Structure

```text
ExamPrep-AI/
├── src/
│   ├── __init__.py     # Package initialization
│   ├── ingest.py       # Logic for parsing PDF/PPTX/DOCX
│   ├── preprocess.py   # Text cleaning and chunking algorithms
│   ├── models.py       # Vector database (FAISS) and Embedding logic
│   └── llm_engine.py   # Interface with Hugging Face API & Prompt Engineering
├── data/               # Temporary storage for uploaded files
├── app.py              # FastAPI backend entry point
├── frontend.py         # Streamlit frontend user interface
├── requirements.txt    # Project dependencies
├── .env                # Environment variables (API Keys)
└── README.md           # Documentation
```

## Future Improvements

*   **Persistent Storage:** Integrate PostgreSQL or ChromaDB to save user exam history.
*   **Export Functionality:** Add support to export generated exams to PDF or CSV formats.
*   **Custom Fine-Tuning:** Fine-tune a LLaMA-3 model specifically on educational datasets for improved pedagogical output.

## License

This project is licensed under the MIT License.
```