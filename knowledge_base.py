import os
import glob
import pdfplumber
import tiktoken
import numpy as np
from openai import OpenAI

class KnowledgeBase:
    """Manages the creation and retrieval of the regulatory knowledge base."""

    def __init__(self, client: OpenAI, embedding_model="text-embedding-3-small"):
        self.client = client
        self.embedding_model = embedding_model
        self.chunks = []
        self.embeddings = None
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def build(self, docs_path="docs"):
        """Builds the knowledge base from PDF documents."""
        print("Building knowledge base...")
        doc_files = glob.glob(os.path.join(docs_path, "*.pdf"))
        for doc_path in doc_files:
            try:
                with pdfplumber.open(doc_path) as pdf:
                    file_name = os.path.basename(doc_path)
                    full_text = "".join(page.extract_text() or "" for page in pdf.pages)
                    self._chunk_text(full_text, file_name)
            except Exception as e:
                print(f"Error reading PDF {doc_path}: {e}")

        if self.chunks:
            self._embed_chunks()
            print(f"Knowledge base built successfully with {len(self.chunks)} chunks.")
        else:
            print("No text chunks were created. Knowledge base is empty.")

    def _chunk_text(self, text: str, source: str, max_tokens=512):
        """Splits text into smaller chunks based on token count."""
        tokens = self.tokenizer.encode(text)
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i:i + max_tokens]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            self.chunks.append({"text": chunk_text, "source": source})

    def _embed_chunks(self):
        """Creates vector embeddings for all text chunks."""
        texts = [chunk["text"] for chunk in self.chunks]
        response = self.client.embeddings.create(input=texts, model=self.embedding_model)
        self.embeddings = np.array([item.embedding for item in response.data])

    def retrieve_relevant_chunks(self, query: str, top_k=5):
        """Retrieves the most relevant text chunks for a given query."""
        if self.embeddings is None or len(self.embeddings) == 0:
            return ""

        query_embedding_response = self.client.embeddings.create(input=[query], model=self.embedding_model)
        query_embedding = np.array(query_embedding_response.data[0].embedding)

        # Calculate cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding))
        
        # Get top_k most similar chunks
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        relevant_context = "\n\n--- INICIO DEL CONTEXTO NORMATIVO RELEVANTE ---"
        for i in top_indices:
            relevant_context += f"\n--- Fuente: {self.chunks[i]['source']} ---"
            relevant_context += self.chunks[i]["text"]
        relevant_context += "\n--- FIN DEL CONTEXTO NORMATIVO RELEVANTE ---"
        
        return relevant_context
