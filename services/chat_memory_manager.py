# chat_memory_manager.py

import uuid
from datetime import datetime
from services.weaviate_client_setup import get_weaviate_client,create_chat_history_collection
from services.rfp_generator import get_openai_embedding


class ChatMemoryManager:
    def __init__(self):
        self.collection_name = "ChatHistory"
        self.client = get_weaviate_client()
        create_chat_history_collection(self.client)
        self.collection = self.client.collections.get(self.collection_name)
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.client.close()
    
    def is_duplicate_question(self, question: str, within_last_n: int = 5) -> bool:
     recent_chats = self.get_last_n_chats(n=within_last_n)
     for chat in recent_chats:
         if chat["question"].strip().lower() == question.strip().lower():
             return True
     return False 

    def log_chat(self, question: str, answer: str):
        if self.is_duplicate_question(question):
         print(f"Skipping log: duplicate question detected.")
         return  # Do not store duplicate question
        vector = get_openai_embedding(f"{question} {answer}")
        self.collection.data.insert(
            properties={
                "question": question,
                "answer": answer,
                "timestamp": datetime.utcnow().isoformat()
            },
            vector=vector,
            uuid=str(uuid.uuid4())
        )

    def get_last_n_chats(self, n: int = 3):
        """Get last n chat turns by timestamp (for meta-questions)"""
        response = self.collection.query.fetch_objects(
            limit=n,
            return_properties=["question", "answer", "timestamp"]
        )
        return list(reversed([
            {
                "question": obj.properties["question"],
                "answer": obj.properties["answer"],
                "timestamp": obj.properties["timestamp"]
            }
            for obj in response.objects
        ]))

    def get_relevant_chats(self, query: str, top_k: int = 3):
        """Get semantically similar chats to use as GPT context"""
        vector = get_openai_embedding(query)
        results = self.collection.query.near_vector(
            near_vector=vector,
            limit=top_k,
            return_properties=["question", "answer"]
        )
        print(results)
        return [
            {
                "question": obj.properties["question"],
                "answer": obj.properties["answer"]
            }
            for obj in results.objects
        ]

    def close(self):
        self.client.close()
