
import streamlit as st
import os
import uuid

from dotenv import load_dotenv
load_dotenv()

from agents.ingestion_agent import IngestionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.llm_response_agent import LLMResponseAgent

def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

st.set_page_config(page_title="📄 Agentic RAG Chatbot", layout="wide")
st.title("📄 Agentic RAG Chatbot using MCP")

uploaded_files = st.file_uploader("Upload documents", type=["pdf", "pptx", "docx", "csv", "txt", "md"], accept_multiple_files=True)

if uploaded_files:
    ingestion = IngestionAgent()
    retrieval = RetrievalAgent()
    llm = LLMResponseAgent()

    trace_id = str(uuid.uuid4())  # Unique session ID

    all_chunks = []

    for file in uploaded_files:
        # Save uploaded file
        file_path = os.path.join("uploaded_docs", file.name)
        with open(file_path, "wb") as f:
            f.write(file.getvalue())

        # === STEP 1: IngestionAgent with MCP ===
        mcp_ingest_msg = {
            "sender": "UI",
            "receiver": "IngestionAgent",
            "type": "FILE_UPLOAD",
            "trace_id": trace_id,
            "payload": {
                "file_path": file_path
            }
        }

        ingest_response = ingestion.run(mcp_ingest_msg)

        if ingest_response["type"] == "CONTEXT_ERROR":
            st.error(f"❌ Error ingesting {file.name}: {ingest_response['payload']['error']}")
            continue

        parsed_text = ingest_response["payload"]["text"]
        filename = ingest_response["payload"]["filename"]

        chunks = chunk_text(parsed_text)
        st.write(f"📦 {len(chunks)} chunks created from: {filename}")
        all_chunks.extend(chunks)

    if not all_chunks:
        st.error("No valid chunks found in the uploaded documents.")
    else:
        # === STEP 2: RetrievalAgent (build index) ===
        mcp_index_msg = {
            "sender": "IngestionAgent",
            "receiver": "RetrievalAgent",
            "type": "CONTEXT_DOCUMENT_PARSED",
            "trace_id": trace_id,
            "payload": {
                "text": "\n".join(all_chunks),
                "filename": "all_documents"
            }
        }

        index_response = retrieval.run(mcp_index_msg)

        if index_response["type"] == "CONTEXT_ERROR":
            st.error("Indexing error: " + index_response["payload"]["error"])
        else:
            st.success(f"✅ Index built with {index_response['payload']['num_chunks']} chunks.")

            # === STEP 3: Ask question ===
            query = st.text_input("Ask a question:", key="query_input")
            top_k = st.slider("How many chunks should the bot use?", 1, 10, 3)
            if query:
                mcp_query_msg = {
                    "sender": "UI",
                    "receiver": "RetrievalAgent",
                    "type": "QUERY_REQUEST",
                    "trace_id": trace_id,
                    "payload": {
                        "query": query
                    }
                }

                with st.spinner("🔎 Retrieving relevant chunks..."):
                    retrieval_response = retrieval.run(mcp_query_msg)

                if retrieval_response["type"] == "CONTEXT_ERROR":
                    st.error("❌ Retrieval error: " + retrieval_response["payload"]["error"])
                else:
                    top_chunks = retrieval_response["payload"]["top_chunks"]

                    st.subheader("🔍 Top Relevant Chunks")
                    for i, chunk in enumerate(top_chunks):
                        st.markdown(f"**{i+1}.** {chunk}")

                    # === STEP 4: LLMResponseAgent ===
                    with st.spinner("💬 Generating answer..."):
                        llm_response = llm.run(retrieval_response)

                    if llm_response["type"] == "CONTEXT_ERROR":
                        st.error("❌ LLM error: " + llm_response["payload"]["error"])
                    else:
                        st.markdown("---")
                        st.subheader("🧠 Final Answer")
                        st.success(llm_response["payload"]["answer"])
else:
    st.info("📤 Please upload one or more documents to begin.")
