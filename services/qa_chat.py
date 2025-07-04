# qa_chat.py

import openai
import os
from dotenv import load_dotenv
from services.chat_memory_manager import ChatMemoryManager

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_answer_from_query(question: str) -> str:
    try:
        with ChatMemoryManager() as memory:
            # print("Fetching relevant chats...")
            # try:
            #     relevant_chats = memory.get_relevant_chats(question, top_k=3)
            #     print("Relevant chats fetched:", relevant_chats)
            # except Exception as e:
            #     print("Error fetching relevant chats:", e)
            #     return f"Error fetching relevant chats: {e}"

            print("🧠 Fetching last chat history...")
            try:
                last_chats = memory.get_last_n_chats(n=2)
                print("Last chats fetched:", last_chats)
            except Exception as e:
                print("Error fetching last chats:", e)
                return f"Error fetching last chats: {e}"
                
            #"If the question is about the RFP or related details, go ahead and answer. But if it seems off-topic, kindly reply with: 'That doesn't seem related to the RFP. Could you ask something specific to it?'"

            system_prompt = (
                """You are a helpful assistant tasked with explaining RFP documents clearly and simply.
                   You must only use the provided reference documents to answer questions.
                   If a user asks a content-based question, respond clearly using only the document text.
                   If a user asks a source-related question (e.g., "Which PDF is this from?", "Which part did you use?", "Where did you find this?"), include the PDF filename or section if available.
                   If the question is clearly unrelated to the RFP or documents (e.g., general tech or off-topic questions), respond with:
                   That doesn't seem related to the RFP or provided documents. Could you ask something specific to them?
                   Explain technical terms in plain English. Use tabular format and emojis when appropriate for clarity."""
)
            messages = [{"role": "system", "content": system_prompt}]

            for chat in last_chats:
                messages.append({"role": "user", "content": chat["question"]})
                messages.append({"role": "assistant", "content": chat["answer"]})

            # context = "\n\n".join([f"Q: {chat['question']}\nA: {chat['answer']}" for chat in relevant_chats])
            context_block = f"\nQuestion:\n{question}\n\nAnswer:"
            messages.append({"role": "user", "content": context_block})

            print("Sending to OpenAI...")
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.4,
                    max_tokens=1000
                )
                answer = response.choices[0].message.content.strip()
            except Exception as gpt_error:
                return f"OpenAI API error: {gpt_error}"

            print("Got response. Logging chat...")
            memory.log_chat(question, answer)
            return answer

    except Exception as e:
        return f"An error occurred: {e}"
