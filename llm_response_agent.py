

# agents/llm_response_agent.py

import uuid
import os
import google.generativeai as genai

class LLMResponseAgent:
    def __init__(self, model_name="models/gemini-1.5-flash-latest", temperature=0.3):
        self.sender = "LLMResponseAgent"
        self.receiver = "UI"
        self.model_name = model_name
        self.temperature = temperature

        # Configure Gemini API key
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        # Load Gemini model
        self.model = genai.GenerativeModel(model_name=self.model_name)

    def run(self, mcp_message):
        # Extract fields from MCP input
        trace_id = mcp_message.get("trace_id", str(uuid.uuid4()))
        payload = mcp_message.get("payload", {})
        query = payload.get("query", "")
        chunks = payload.get("top_chunks", [])

        # Construct context and prompt
        context = "\n---\n".join(chunks)
        prompt = f"""You are a helpful assistant. Use the context below to answer the user's question.

Context:
{context}

Question: {query}
Answer:"""

        try:
            response = self.model.generate_content(prompt)
            answer = response.text

            # MCP-compliant output
            return {
                "sender": self.sender,
                "receiver": self.receiver,
                "type": "FINAL_ANSWER",
                "trace_id": trace_id,
                "payload": {
                    "answer": answer,
                    "query": query,
                    "used_chunks": chunks
                }
            }

        except Exception as e:
            return {
                "sender": self.sender,
                "receiver": self.receiver,
                "type": "CONTEXT_ERROR",
                "trace_id": trace_id,
                "payload": {
                    "error": str(e),
                    "query": query
                }
            }






















