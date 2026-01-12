import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load API Key
load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

if not HF_API_KEY:
    raise ValueError("HF_API_KEY not found in .env file. Please add it.")

# Using Zephyr model from Hugging Face
repo_id = "HuggingFaceH4/zephyr-7b-beta"
client = InferenceClient(token=HF_API_KEY)

def clean_model_output(text):
    """
    Cuts off text immediately when the model starts hallucinating or
    tries to generate a 7th question.
    """
    stop_markers = ["[/USER]", "[/ASSISTANT]", "User:", "### END"]
    for marker in stop_markers:
        if marker in text:
            text = text.split(marker)[0]
    
    # Force stop if it tries to write question 7
    if "7." in text:
        text = text.split("7.")[0]

    return text.strip()
def generate_response(messages, max_tokens=1500):
    """
    Helper to send chat messages to HF API.
    Removed 'repetition_penalty' to fix the TypeError.
    """
    try:
        response = client.chat_completion(
            model=repo_id,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3, # Low temperature to prevent hallucination loops
            top_p=0.9
        )
        return response.choices[0].message.content.strip()
        return clean_model_output(raw_text)
    except Exception as e:
        return f"Error communicating with HF API: {e}"

def generate_scenario_mcqs(text_chunk):
    """
    Generates 2 distinct Case Studies and 3 MCQs per case study.
    """
    
    system_msg = (
        "You are a strict academic examiner. "
        "Your goal is to test application of knowledge. "
        "Output ONLY the requested exam content. "
        "Do not repeat questions. "
        "Do not output filler text like 'Here are the questions'. "
        "STOP writing immediately after Question 6."
    )
    
    user_prompt = f"""
    Based on the text below, generate a Scenario-Based Exam.
    
    TEXT MATERIAL:
    "{text_chunk[:2500]}"
    
    ---
    
    TASK 1: CASE STUDY A
    Write a realistic workplace scenario (Case Study A) applying the concepts.
    Then, write 3 Multiple Choice Questions (numbered 1-3) based on Case Study A.
    
    TASK 2: CASE STUDY B
    Write a DIFFERENT scenario (Case Study B) applying the concepts.
    Then, write 3 Multiple Choice Questions (numbered 4-6) based on Case Study B.
    
    FORMAT:
    
    ### CASE STUDY A: [Title]
    [Scenario Paragraph]
    
    1. [Question]
       a) [Option]
       b) [Option]
       c) [Option]
       d) [Option]
       Answer: [Correct Option]
       Explanation: [Reason]
       
    2. [Question]...
    3. [Question]...
    
    ### CASE STUDY B: [Title]
    [Scenario Paragraph]
    
    4. [Question]...
    5. [Question]...
    6. [Question]...

    ### END
    """
    
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt}
    ]
    
    return generate_response(messages, max_tokens=2000)

def generate_summary(text_chunk):
    """
    Generates a plain-english summary.
    """
    messages = [
        {"role": "system", "content": "You are a helpful tutor."},
        {"role": "user", "content": f"Summarize the key concepts from this text in simple bullet points:\n\n{text_chunk[:3000]}"}
    ]
    return generate_response(messages, max_tokens=800)

# --- Testing Block ---
if __name__ == "__main__":
    print("Testing Hugging Face Integration...")
    sample_text = "Photosynthesis is the process used by plants to convert light energy into chemical energy."
    print(generate_scenario_mcqs(sample_text))