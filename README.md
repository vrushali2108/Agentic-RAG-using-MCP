Agentic RAG Chatbot using Model Context Protocol (MCP)

This project implements a Retrieval-Augmented Generation (RAG) chatbot with a modular agent-based architecture, where each agent (Ingestion, Retrieval, and LLM Response) communicates using structured Model Context Protocol (MCP) messages.
It supports answering questions based on multi-format uploaded documents (PDF, DOCX, PPTX, CSV, TXT/Markdown).



🧠 Features
✅ Upload and parse multiple document types

✅ Agent-based architecture: Ingestion, Retrieval, and LLM Response agents

✅ MCP-style communication between agents

✅ Chunking and embedding of text using Sentence Transformers

✅ Fast vector retrieval using FAISS

✅ Response generation using Gemini 1.5 API (or OpenAI-compatible LLM)

✅ Clean Streamlit UI with context + answers











📂 Supported File Types
PDF (.pdf)

Word Docs (.docx)

PowerPoint (.pptx)

CSV (.csv)

Text / Markdown (.txt, .md)

