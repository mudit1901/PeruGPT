# bulk_pdf_ingest.py

import os
import fitz
import re
import uuid
from dotenv import load_dotenv
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.weaviate_client_setup import get_weaviate_client
from weaviate.classes.query import Filter

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# -------------------- Text Extraction -------------------- #
def extract_text_from_pdf(pdf_path: str) -> str:
    with fitz.open(pdf_path) as doc:
        return "\n".join([page.get_text() for page in doc])

# -------------------- Text Cleaning -------------------- #
def clean_text(text: str) -> str:
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r'[^A-Za-z0-9.,:;?!()\n ]+', '', text)
    return re.sub(r' +', ' ', text).strip()

# -------------------- Chunking -------------------- #
def chunk_text(text: str, chunk_size=500, chunk_overlap=50) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return splitter.split_text(text)

# -------------------- Embedding -------------------- #
def get_openai_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    try:
        response = openai.embeddings.create(model=model, input=text)
        return response.data[0].embedding
    except Exception as e:
        print("Embedding Error:", e)
        return []

# -------------------- Check if Already Ingested -------------------- #
def pdf_already_ingested(client, filename: str) -> bool:
    collection = client.collections.get("PDFChunk")

    response = collection.query.fetch_objects(
        filters=Filter.by_property("filename").equal(filename),
        limit=1,
        return_properties=["filename"]
    )

    return len(response.objects) > 0

# -------------------- Store Chunks -------------------- #
def store_chunks_in_weaviate(client, chunks: list, filename: str):
    collection = client.collections.get("PDFChunk")
    for i, chunk in enumerate(chunks):
        vector = get_openai_embedding(chunk)
        if not vector:
            continue
        collection.data.insert(
            properties={"text": chunk, "filename": filename},
            vector=vector,
            uuid=str(uuid.uuid4())
        )
        print(f"Stored chunk {i+1}/{len(chunks)} from {filename}")

# -------------------- Main Ingestion Function -------------------- #
def ingest_folder(folder_path: str):
    client = get_weaviate_client()

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith('.pdf'):
            continue

        print(f"\nProcessing: {filename}")
        if pdf_already_ingested(client, filename):
            print(f"Already ingested: {filename} — skipping.")
            continue

        pdf_path = os.path.join(folder_path, filename)
        raw_text = extract_text_from_pdf(pdf_path)
        cleaned = clean_text(raw_text)
        chunks = chunk_text(cleaned)

        store_chunks_in_weaviate(client, chunks, filename)

    print("\nAll PDFs processed.")

# -------------------- Run -------------------- #
if __name__ == "__main__":
    ingest_folder("C:\Evolvision Technologies\PeruGPT\data") 
