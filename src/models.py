from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os

# Initialize the embedding model (downloads on first run)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

class VectorDB:
    def __init__(self, index_file="faiss_index.bin", metadata_file="metadata.pkl"):
        self.index = None
        self.metadata = []  # To store the actual text alongside vectors
        self.index_file = index_file
        self.metadata_file = metadata_file

    def create_index(self, chunks):
        """
        Takes a list of text chunks, embeds them, and adds them to a FAISS index.
        """
        if not chunks:
            return
        
        # 1. Generate Embeddings
        print("Generating embeddings...")
        embeddings = embedding_model.encode(chunks)
        
        # 2. Initialize FAISS Index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        
        # 3. Add to Index
        self.index.add(np.array(embeddings))
        
        # 4. Store Metadata (the actual text)
        self.metadata = chunks
        
        print(f"Index created with {len(chunks)} chunks.")

    def search(self, query, k=3):
        """
        Searches the index for the 'k' most similar chunks to the query.
        Returns a list of text chunks.
        """
        if self.index is None:
            print("Index is empty.")
            return []

        # Convert query to vector
        query_vector = embedding_model.encode([query])
        
        # Search FAISS
        distances, indices = self.index.search(np.array(query_vector), k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.metadata):
                results.append(self.metadata[idx])
        
        return results

    def save(self):
        """Saves the FAISS index and metadata to disk."""
        if self.index:
            faiss.write_index(self.index, self.index_file)
            with open(self.metadata_file, "wb") as f:
                pickle.dump(self.metadata, f)
            print("Index and metadata saved.")

    def load(self):
        """Loads the FAISS index and metadata from disk."""
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.metadata_file, "rb") as f:
                self.metadata = pickle.load(f)
            print("Index loaded from disk.")
        else:
            print("No index found on disk.")

# --- Testing Block ---
if __name__ == "__main__":
    # Dummy data
    chunks = [
        "Photosynthesis is the process by which green plants create food using sunlight.",
        "The mitochondria is the powerhouse of the cell.",
        "Newton's first law states that an object in motion stays in motion.",
        "Python is a high-level programming language."
    ]
    
    # Initialize DB
    db = VectorDB()
    
    # Create Index
    db.create_index(chunks)
    
    # Test Search
    query = "How do plants make food?"
    results = db.search(query, k=1)
    
    print(f"\nQuery: {query}")
    print(f"Result: {results[0]}")
    
    # Test Save/Load
    db.save()