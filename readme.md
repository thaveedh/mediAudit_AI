# Prescription Audit & Drug Information System

An AI-powered medical information system that combines FDA drug-label data, semantic search, Retrieval-Augmented Generation (RAG), ChromaDB, and Qwen LLM to provide simple and understandable medicine-related information.

The system is designed to retrieve reliable drug information from FDA documents while also allowing the local Qwen model to handle general medical questions that are not directly available in the retrieved documents.

---

# 1. System Overview

The system combines two major approaches:

1. FDA-based Retrieval-Augmented Generation (RAG)
2. Qwen LLM-based general medical response

The application can retrieve medicine-specific information from the stored FDA documents and generate a user-friendly response.

For general questions that are not directly available in the FDA documents, Qwen can provide a general response.

---

# 2. Complete System Workflow

```text
                         USER
                           |
                           v
                  Enter Medical Query
                           |
                           v
                  Query Normalization
                           |
                           v
                  Generate Embedding
                           |
                           v
                     ChromaDB
                  Semantic Retrieval
                           |
                           v
                Relevant FDA Documents
                           |
                           v
                    Query Analysis
                           |
             +-------------+-------------+
             |                           |
             v                           v
       FDA/RAG Response             General Query
             |                           |
             v                           v
     Retrieved FDA Context          Qwen LLM
             |                           |
             +-------------+-------------+
                           |
                           v
                    Response Generator
                           |
                           v
                 Simple User-Friendly
                       Response
                           |
                           v
                         USER


                         3. Detailed RAG Workflow
Step 1 - User Query

The user enters a question such as:

What are the side effects of Ibuprofen?

or:

What foods should I avoid while taking Warfarin?

or:

Why is Warfarin prescribed?
Step 2 - Query Normalization

The system first normalizes the user query.

Example:

User Input:
Paracetamol

Normalized:
acetaminophen

This helps match different names or forms of the same medicine.

The normalization logic is located in:

backend/utils/query_normalizer.py
4. Embedding Generation

The normalized query is converted into a numerical vector using:

BAAI/bge-small-en-v1.5

The embedding model is implemented in:

backend/vector_db/embedding.py

Example:

User Query
    ↓
Text
    ↓
BGE Embedding Model
    ↓
384-dimensional vector
5. ChromaDB Retrieval

The generated embedding is searched against the stored FDA medical documents.

ChromaDB is used as the vector database.

Main files:

backend/vector_db/chroma_db.py
backend/vector_db/ingest.py
backend/vector_db/retriever.py

The retriever finds documents that are semantically similar to the user's question.

Example:

Question:
What are the side effects of Ibuprofen?

        ↓

Embedding

        ↓

ChromaDB

        ↓

Relevant FDA document

Section:
ADVERSE REACTIONS
6. FDA Document Data

The system uses FDA drug-label information as the main source for medicine-specific information.

The parser extracts useful information such as:

DESCRIPTION
INDICATIONS AND USAGE
DOSAGE AND ADMINISTRATION
CONTRAINDICATIONS
WARNINGS
PRECAUTIONS
ADVERSE REACTIONS
DRUG INTERACTIONS
USE IN SPECIFIC POPULATIONS

The ingestion logic is located in:

backend/parser/ingest_all.py
7. RAG Pipeline

After retrieving relevant FDA information, the retrieved documents are passed into the RAG pipeline.

Main file:

backend/rag.py

The workflow is:

User Question
      ↓
Normalize Query
      ↓
Generate Embedding
      ↓
Retrieve Relevant FDA Documents
      ↓
Build Context
      ↓
Send Context + Question to LLM
      ↓
Generate Answer
8. Qwen LLM

The project uses:

Qwen 2.5 3B

through:

Ollama

The LLM generation code is located in:

backend/llm/generator.py

Qwen is used to convert retrieved medical information into a more understandable response.

Instead of directly showing complicated FDA terminology, the model can produce simpler explanations for users.

Example:

Technical:
Anticoagulant that inhibits vitamin K-dependent coagulation factors.

Simple:
Warfarin is a medicine that helps prevent harmful blood clots.
9. General Query Handling

Not every question will have a direct answer in the FDA documents.

For example:

What healthy habits can help me manage this condition?

or:

What are some natural supportive ways to manage this condition?

These questions may not have a direct answer in the retrieved FDA documents.

The system can use Qwen for general informational responses where appropriate.

However, medicine-specific information such as:

Dosage
Drug interactions
Contraindications
Warnings
FDA-approved uses
Adverse reactions
Prescription-related information

should prioritize retrieved FDA information.

10. User-Friendly Response

The final answer should be written in simple language.

The goal is that a normal user should be able to understand:

What is this medicine?
Why is it used?
What are common side effects?
What serious problems should I watch for?
What medicines can interact with it?
What foods or drinks should I be careful with?
What precautions should I know?

The system should avoid unnecessary technical medical terminology.

11. Project Structure
prescription-audit/
│
├── README.md
├── .gitignore
│
└── backend/
    │
    ├── app/
    │   ├── main.py
    │   └── routes.py
    │
    ├── llm/
    │   └── generator.py
    │
    ├── parser/
    │   ├── ingest_all.py
    │   └── test_parser.py
    │
    ├── utils/
    │   └── query_normalizer.py
    │
    ├── vector_db/
    │   ├── chroma_db.py
    │   ├── embedding.py
    │   ├── ingest.py
    │   ├── retriever.py
    │   ├── test_chroma.py
    │   ├── test_embedding.py
    │   └── test_retrieval.py
    │
    ├── medical_assist.py
    ├── rag.py
    ├── search_medicine.py
    └── requirements.txt
12. Technologies Used
Python

Main programming language.

ChromaDB

Used as the vector database for storing and searching medical document embeddings.

Sentence Transformers

Used to convert user queries and medical documents into embeddings.

BAAI/bge-small-en-v1.5

Embedding model used for semantic search.

Ollama

Used to run the Qwen model locally.

Qwen 2.5 3B

Local language model used to generate natural-language responses.

FastAPI

Used for backend API development.

LXML

Used to parse FDA XML documents.

13. Installation
Step 1 - Clone Repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd prescription-audit
14. Create Virtual Environment

Go into the backend folder:

cd backend

Create the virtual environment:

python -m venv venv
15. Activate Virtual Environment

Windows PowerShell:

venv\Scripts\activate

After activation you should see:

(venv) PS D:\Rag\prescription-audit\backend>
16. Install Dependencies

Run:

pip install -r requirements.txt

This installs the required Python packages.

17. Install and Run Ollama

Install Ollama on the system.

Then download the Qwen model:

ollama pull qwen2.5:3b

Check the installed model:

ollama list

You should see:

qwen2.5:3b
18. FDA Dataset

The FDA dataset is not stored inside this Git repository because the dataset can be very large.

The dataset should be obtained separately.

After obtaining the dataset, configure the appropriate dataset path in:

backend/parser/ingest_all.py
19. Ingest FDA Data

From:

prescription-audit/backend

run:

python parser/ingest_all.py

The ingestion process performs:

FDA XML Files
     ↓
XML Parser
     ↓
Extract Medicine Information
     ↓
Extract Relevant Sections
     ↓
Generate Embeddings
     ↓
Store in ChromaDB
20. Run Medicine Search

To check whether medicines exist in the database:

python search_medicine.py

This can be used to verify that the FDA dataset was successfully ingested.

21. Run the Medical Assistant

From:

prescription-audit/backend

activate the environment:

venv\Scripts\activate

Then run:

python medical_assist.py

You should see:

Ask a medical question (type 'exit' to quit):
22. Example Questions
Medicine Usage
Why is Warfarin prescribed?
Side Effects
What are the side effects of Ibuprofen?
Food
What foods should I avoid while taking Warfarin?
Drug Interaction
Can Warfarin interact with other medicines?
General Information
What is Warfarin?
Natural / Supportive Questions
What lifestyle changes can support this condition?

The system should distinguish between medicine-specific FDA information and general informational questions.

23. Testing
Test Embeddings
python vector_db/test_embedding.py

Expected output should show that the embedding is generated successfully.

Test ChromaDB
python vector_db/test_chroma.py

This checks the ChromaDB connection and collection.

Test Retrieval
python vector_db/test_retrieval.py

This checks whether relevant documents can be retrieved from ChromaDB.

Test Parser
python parser/test_parser.py

This checks the document parsing process.

24. Important Files
File	Purpose
medical_assist.py	Main command-line medical assistant
rag.py	Main RAG pipeline
llm/generator.py	Qwen response generation
vector_db/embedding.py	Generates embeddings
vector_db/retriever.py	Retrieves relevant documents
vector_db/chroma_db.py	ChromaDB configuration
vector_db/ingest.py	Inserts data into ChromaDB
parser/ingest_all.py	FDA dataset ingestion
parser/test_parser.py	Parser testing
search_medicine.py	Medicine database search
utils/query_normalizer.py	Query normalization
app/main.py	FastAPI application
app/routes.py	API routes
requirements.txt	Python dependencies
25. GitHub Team Setup

Do NOT push the following:

venv/
__pycache__/
*.pyc
chroma_storage/
.env
*.zip

These files should be ignored using .gitignore.

Every team member should create their own environment:

python -m venv venv

Activate it:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Install Qwen:

ollama pull qwen2.5:3b

The FDA dataset and ChromaDB database should be generated locally.

26. Recommended .gitignore
# Virtual Environment
venv/

# Python Cache
__pycache__/
*.py[cod]

# ChromaDB
chroma_storage/

# Environment Variables
.env

# IDE
.vscode/
.idea/

# Archives
*.zip

# OS files
.DS_Store
Thumbs.db
27. Git Commands

After making changes:

git status

Add files:

git add .

Commit:

git commit -m "Update project"

Push:

git push

For the first push:

git push -u origin main
28. Team Development Workflow

Each team member should:

Clone Repository
       ↓
Create Virtual Environment
       ↓
Install requirements.txt
       ↓
Install Qwen using Ollama
       ↓
Obtain FDA Dataset
       ↓
Generate Local ChromaDB
       ↓
Run Tests
       ↓
Develop Feature
       ↓
git add .
       ↓
git commit
       ↓
git push

Before starting new work:

git pull

After completing work:

git status
git add .
git commit -m "Describe your changes"
git push
29. Medical Safety

This project is intended for educational and informational purposes.

The system should not be treated as a replacement for a qualified doctor, pharmacist, or other healthcare professional.

Users should consult healthcare professionals before:

Starting a medicine
Stopping a medicine
Changing dosage
Replacing prescribed medication
Combining medicines
Making treatment decisions

General information generated by an LLM should not override prescription or FDA-based information.

30. Current Project Status
 FDA XML parsing
 Medicine data extraction
 Embedding generation
 ChromaDB integration
 Semantic retrieval
 Query normalization
 RAG pipeline
 Qwen LLM integration
 Medical question answering
 Side-effect retrieval
 Drug interaction retrieval
 Food and dietary guidance
 General supportive guidance
 Testing utilities
 Frontend integration
 Complete API integration
 Evaluation and benchmarking
 Final deployment
31. Future Improvements

Planned improvements include:

Web-based user interface
Better medicine name recognition
Improved query classification
Better FDA document ranking
Citation/source display
More robust medical safety checks
User-friendly response formatting
Automated evaluation of retrieval quality
API and frontend integration
Production deployment
Disclaimer

This application is an educational project and is not intended to provide medical diagnosis, treatment, or professional medical advice.

Always consult a qualified healthcare professional for medical decisions.


### Then save it as

```text
D:\Rag\prescription-audit\README.md

Then run:

git add README.md
git commit -m "Add complete project documentation"
git push