import uuid
from datetime import datetime
from services.weaviate_client_setup import get_weaviate_client, create_chat_history_collection
from services.rfp_generator import get_openai_embedding


class ChatMemoryManager:
    def __init__(self):
        self.collection_name = "ChatHistory"
        self.client = get_weaviate_client()
        create_chat_history_collection(self.client)
        self.collection = self.client.collections.get(self.collection_name)

    # --- context‑manager helpers ------------------------------------------------
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close Weaviate connection."""
        self.client.close()

    # ---------------------------------------------------------------------------

    # ── Helpers ----------------------------------------------------------------
    def is_duplicate_question(self, question: str, within_last_n: int = 5) -> bool:
        """True if identical question appears in last N chats (case‑insensitive)."""
        recent_chats = self.get_last_n_chats(n=within_last_n)
        question_norm = question.strip().lower()
        return any(chat["question"].strip().lower() == question_norm for chat in recent_chats)

    # ── Logging ----------------------------------------------------------------
    def log_chat(self, question: str, answer: str):
        if self.is_duplicate_question(question):
            print("Skipping log: duplicate question detected.")
            return

        vector = get_openai_embedding(f"{question} {answer}")  # flat 1‑D list

        self.collection.data.insert(
            properties={
                "question": question,
                "answer": answer,
                "timestamp": datetime.utcnow().isoformat()
            },
            vector=vector,              # inserts still accept raw list
            uuid=str(uuid.uuid4())
        )

    # ── Retrieval --------------------------------------------------------------
    def get_last_n_chats(self, n: int = 3):
        """Return last n chats (most recent last)."""
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

    # def get_relevant_chats(self, query: str, top_k: int = 3):
    #     """Semantic similarity search for GPT context."""
    #     vector = get_openai_embedding(query)          # flat list

    #     results = self.collection.query.near_vector(
    #         near_vector={"vector": vector},           # ← FIX: wrap in dict
    #         limit=top_k,
    #         return_properties=["question", "answer"]
    #     )

    #     return [
    #         {
    #             "question": obj.properties["question"],
    #             "answer": obj.properties["answer"]
    #         }
    #         for obj in results.objects
    #     ]
