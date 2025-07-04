# Weaviate client setup and collection management

import os
from dotenv import load_dotenv
import weaviate
from weaviate.classes.init import Auth
from weaviate.collections.classes.config import (Property, Configure, DataType)

load_dotenv()

def get_weaviate_client():
    # Check required environment variables
    required_vars = ["WEAVIATE_URL", "WEAVIATE_API_KEY", "OPENAI_API_KEY"]
    if not all(os.getenv(var) for var in required_vars):
        raise EnvironmentError("Missing one or more required environment variables: WEAVIATE_URL, WEAVIATE_API_KEY, OPENAI_API_KEY")

    # Connect to Weaviate Cloud
    try:
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=os.getenv("WEAVIATE_URL"),
            auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
            headers={
                "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
            }
        )
    except Exception as e:
        raise ConnectionError(f"Failed to connect to Weaviate: {e}")

    # Create PDFChunk collection if it doesn't exist
    if not client.collections.exists("PDFChunk"):
        client.collections.create(
            name="PDFChunk",
            description="Stores chunks of PDFs",
            vectorizer_config=Configure.Vectorizer.none(),
            properties=[
                Property(name="text", data_type=DataType.TEXT, description="Chunk text"),
                Property(name="filename", data_type=DataType.TEXT, description="Source PDF filename")
            ]
        )
        print("Created 'PDFChunk' collection.")
    else:
        print("Collection 'PDFChunk' already exists.")

    return client


def create_chat_history_collection(client):
    if not client.collections.exists("ChatHistory"):
        client.collections.create(
            name="ChatHistory",
            description="Stores user and assistant chats",
            vectorizer_config=Configure.Vectorizer.none(),
            properties=[
                Property(name="question", data_type=DataType.TEXT, description="User input"),
                Property(name="answer", data_type=DataType.TEXT, description="Assistant reply"),
                Property(name="timestamp", data_type=DataType.TEXT, description="UTC ISO timestamp")
            ]
        )
        print("✅ Created 'ChatHistory' collection.")
    else:
        print("✅ 'ChatHistory' collection already exists.")
