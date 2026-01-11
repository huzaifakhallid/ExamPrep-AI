import re

def clean_text(text):
    """
    Normalizes text:
    1. Removes multiple spaces and newlines.
    2. Removes specific symbols if needed.
    """
    # Replace multiple newlines/spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove extremely short useless segments (like page numbers standing alone)
    text = re.sub(r'^\d+\s*$', '', text) 
    
    return text.strip()

def chunk_text(text, chunk_size=300, overlap=50):
    """
    Splits text into chunks of approximately `chunk_size` words.
    Includes `overlap` words from the previous chunk to maintain context.
    """
    words = text.split()
    
    if not words:
        return []
    
    chunks = []
    
    # Iterate through words with a step size of (chunk_size - overlap)
    step = chunk_size - overlap
    
    for i in range(0, len(words), step):
        # Slice the list of words
        chunk_words = words[i : i + chunk_size]
        chunk_str = " ".join(chunk_words)
        chunks.append(chunk_str)
    
    return chunks

if __name__ == "__main__":
    # Test Data
    raw_sample = """
    Deep Learning is a subset of machine learning.

    

    It is based on artificial neural networks.
    These networks are inspired by the human brain.

    """
    
    print("--- Original ---")
    print(raw_sample)
    
    cleaned = clean_text(raw_sample)
    print("\n--- Cleaned ---")
    print(cleaned)
    
    # dummy chunking test
    long_text = "word " * 1000
    chunks = chunk_text(long_text, chunk_size=100, overlap=20)
    print(f"\n--- Chunking Test ---")
    print(f"Total words: 1000")
    print(f"Chunk size: 100, Overlap: 20")
    print(f"Generated {len(chunks)} chunks.")