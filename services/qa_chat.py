# qa_chat.py

import os
from dotenv import load_dotenv
import openai
from services.weaviate_client_setup import get_weaviate_client
from services.rfp_generator import get_openai_embedding

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_answer_from_query(question: str) -> str:
    # Convert question to embedding for semantic search
    vector = get_openai_embedding(question)
    client = get_weaviate_client()
    collection = client.collections.get("PDFChunk")

    # Find most relevant document chunks
    results = collection.query.near_vector(
        near_vector=vector,
        limit=10,
        return_properties=["text"]
    )

    # Extract and combine context from search results
    context_chunks = [obj.properties["text"] for obj in results.objects]
    context = "\n\n".join(context_chunks)
    client.close()

    # Configure AI to provide clear, user-friendly explanations
    system_prompt = (
        """You are a helpful assistant tasked with explaining documents to users in a clear and simple way.
           Use the provided reference to answer the user's question accurately.
           Your explanation should be descriptive, easy to understand, and leave no room for confusion.
           Assume the user has no prior knowledge—explain any technical terms if needed.
           Always aim to make the user feel confident and well-informed after reading your answer."""
    )

    prompt = f"""Reference:
{context}

Question: {question}

Answer:"""

    # Generate answer using GPT-4o-mini
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()
