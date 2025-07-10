

# agents/retrieval_agent.py

import uuid
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class RetrievalAgent:
    def __init__(self):
        self.sender = "RetrievalAgent"
        self.receiver = "LLMResponseAgent"
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.text_chunks = []

    def build_index(self, text, chunk_size=300):
        if not text:
            raise ValueError("Empty text received for indexing.")

        # Simple fixed-size chunking
        self.text_chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        embeddings = self.model.encode(self.text_chunks, show_progress_bar=False)
        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings))

    def run(self, mcp_message):
        try:
            trace_id = mcp_message.get("trace_id", str(uuid.uuid4()))
            msg_type = mcp_message.get("type", "")
            payload = mcp_message.get("payload", {})

            if msg_type == "CONTEXT_DOCUMENT_PARSED":
                raw_text = payload.get("text", "")
                self.build_index(raw_text)
                return {
                    "sender": self.sender,
                    "receiver": "UI",
                    "type": "CONTEXT_INDEX_BUILT",
                    "trace_id": trace_id,
                    "payload": {
                        "status": "Index successfully built",
                        "num_chunks": len(self.text_chunks)
                    }
                }

            elif msg_type == "QUERY_REQUEST":
                query = payload.get("query", "")
                top_k = payload.get("top_k", 8)  # 👈 Optional override

                if self.index is None:
                    raise ValueError("Index not built yet. Cannot perform retrieval.")

                query_embedding = self.model.encode([query])
                distances, indices = self.index.search(np.array(query_embedding), top_k)

                valid_indices = [i for i in indices[0] if 0 <= i < len(self.text_chunks)]
                top_chunks = [self.text_chunks[i] for i in valid_indices]

                return {
                    "sender": self.sender,
                    "receiver": self.receiver,
                    "type": "CONTEXT_RESPONSE",
                    "trace_id": trace_id,
                    "payload": {
                        "top_chunks": top_chunks,
                        "query": query
                    }
                }

            else:
                raise ValueError(f"Unknown message type: {msg_type}")

        except Exception as e:
            return {
                "sender": self.sender,
                "receiver": "UI",
                "type": "CONTEXT_ERROR",
                "trace_id": mcp_message.get("trace_id", str(uuid.uuid4())),
                "payload": {
                    "error": str(e)
                }
            }
