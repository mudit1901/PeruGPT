import os
from dotenv import load_dotenv
import openai
from services.weaviate_client_setup import get_weaviate_client
from weaviate.classes.query import Filter
from docx import Document


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# -------------------- Embedding -------------------- #
def get_openai_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    try:
        response = openai.embeddings.create(model=model, input=text)
        return response.data[0].embedding
    except Exception as e:
        print("Embedding Error:", e)
        return []

# -------------------- Retrieve Context -------------------- #
def retrieve_context(query, top_k=10):
    # Get embedding for semantic search
    vector = get_openai_embedding(query)
    client = get_weaviate_client()
    collection = client.collections.get("PDFChunk")

    # Find most relevant document chunks
    results = collection.query.near_vector(
        near_vector=vector,
        limit=top_k,
        return_properties=["text"]
    )
    chunks = [obj.properties["text"] for obj in results.objects]
    client.close()
    return "\n\n".join(chunks)

# -------------------- Generate RFP -------------------- #
def generate_rfp(requirement_prompt: str) -> str:
    # Get relevant context from knowledge base
    context = retrieve_context(requirement_prompt)

    system_prompt = (
        "You are a professional proposal writer. Based on the following reference content "
        "and the requirement, generate a detailed RFP (Request for Proposal). "
        "The RFP should include Project Overview, Objectives, Scope of Work, "
        "Feature Requirements, Design Requirements, Proposal Requirements, "
        "Evaluation Criteria."
    )

    prompt = f"""
Reference Material:
{context}

Requirement:
{requirement_prompt}

Generate the RFP:
"""

    # Generate RFP using GPT-4o-mini
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()




