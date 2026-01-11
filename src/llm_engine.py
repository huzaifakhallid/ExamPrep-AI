import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load API Key
load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

if not HF_API_KEY:
    raise ValueError("HF_API_KEY not found in .env file.")

# Using Zephyr model from Hugging Face
repo_id = "HuggingFaceH4/zephyr-7b-beta"
client = InferenceClient(token=HF_API_KEY)

def generate_response(messages, max_tokens=1500):
    """
    Helper to send chat messages to HF API.
    """
    try:
        response = client.chat_completion(
            model=repo_id,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error communicating with HF API: {e}"

def generate_scenario_mcqs(text_chunk):
    """
    Generates 2 distinct Case Studies and 3 MCQs per case study.
    """
    
    system_msg = (
        "You are a strict academic examiner. "
        "Your job is to generate advanced exam content based on the provided text. "
        "Do NOT use placeholders like '(insert text here)'. "
        "WRITE THE FULL SCENARIO NARRATIVE YOURSELF."
    )
    
    user_prompt = f"""
    STUDY MATERIAL:
    "{text_chunk}"
    
    INSTRUCTIONS:
    1. Write TWO unique, detailed "Case Studies" (Scenario A and Scenario B) based on the material.
    2. The Case Study must be a full paragraph describing a realistic workplace or academic situation.
    3. For EACH Case Study, generate 3 difficult Scenario-Based MCQs.
    
    CRITICAL: Do not simply describe what the case study is about. WRITE the case study.
    
    FORMAT:
    
    ### CASE STUDY A: [Title]
    [Write the full 3-4 sentence scenario story here...]
    
    #### QUESTIONS (Case A)
    1. [Question]
       a) ...
       b) ...
       c) ...
       d) ...
       Answer: [Option]
       Explanation: [Reason]
       
    2. [Question]...
    3. [Question]...
    
    ---
    
    ### CASE STUDY B: [Title]
    [Write the full 3-4 sentence scenario story here...]
    
    #### QUESTIONS (Case B)
    4. [Question]...
    5. [Question]...
    6. [Question]...
    """
    
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_prompt}
    ]
    
    return generate_response(messages, max_tokens=1500)

def generate_summary(text_chunk):
    """
    Generates a plain-english summary.
    """
    messages = [
        {"role": "system", "content": "You are a helpful tutor."},
        {"role": "user", "content": f"Explain this concept clearly for a student:\n\n{text_chunk}"}
    ]
    return generate_response(messages, max_tokens=600)

# Testing Block
if __name__ == "__main__":
    print("Testing Hugging Face Integration\n")
    
    sample_text = """
    Phishing is a type of social engineering where an attacker sends a fraudulent 
    message designed to trick a human victim into revealing sensitive information 
    to the attacker or to deploy malicious software on the victim's infrastructure 
    like ransomware. Phishing attacks have become increasingly sophisticated 
    and often mirror the site being targeted.
    """
    
    print("\nGenerating Scenarios & MCQs")
    result = generate_scenario_mcqs(sample_text)
    print(result)