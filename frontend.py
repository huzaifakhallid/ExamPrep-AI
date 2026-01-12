import streamlit as st
import requests
import re
import time

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="ExamPrep AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS ---
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #E0E0E0;
    }

    /* --- ANIMATIONS --- */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* --- COMPONENT STYLES --- */
    
    /* 1. Case Study Card (Blue Theme) */
    .case-container {
        background: linear-gradient(145deg, #1e2024, #23252b);
        border-left: 6px solid #4b6cb7;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 25px;
        animation: slideIn 0.5s ease-out;
    }
    
    .case-header {
        color: #6a89cc;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
    
    .case-body {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #cfd8dc;
        background-color: rgba(255,255,255,0.03);
        padding: 15px;
        border-radius: 8px;
    }

    /* 2. Question Block (Green/Dark Theme) */
    .question-container {
        background-color: #16171a;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 10px;
        margin-top: 15px;
        margin-left: 15px;
        animation: slideIn 0.6s ease-out;
    }
    
    .question-header {
        font-weight: 600;
        color: #81c784;
        margin-bottom: 8px;
        font-size: 1.1rem;
    }

    /* 3. Answer Key (Hidden by default or styled subtly) */
    .answer-key {
        margin-top: 10px;
        padding: 10px;
        background-color: #1b2e1e;
        border-radius: 6px;
        font-size: 0.9rem;
        color: #a5d6a7;
        border-left: 3px solid #4CAF50;
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        border: none;
        color: white;
        padding: 12px 28px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        border-radius: 8px;
        transition: all 0.3s;
        width: 100%;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 14px rgba(0,0,0,0.3);
    }
    
</style>
""", unsafe_allow_html=True)

# --- BACKEND URL ---
API_URL = "http://127.0.0.1:8000"

# --- STATE MANAGEMENT ---
if 'processed' not in st.session_state: st.session_state.processed = False
if 'quiz_content' not in st.session_state: st.session_state.quiz_content = ""

# --- PARSING LOGIC ---
def render_beautiful_exam(raw_text):
    """
    Splits the text by '###' to separates Case Studies, 
    then finds questions using Regex.
    """
    
    # 1. Split by "###" (The marker for Case Studies)
    sections = raw_text.split("###")
    
    for section in sections:
        section = section.strip()
        if not section: continue
        
        # Check if this section is a Case Study
        if "CASE STUDY" in section.upper():
            lines = section.splitlines()
            title = lines[0].replace("CASE STUDY", "").replace(":", "").strip()
            
            # Separate body text from questions (Questions start with numbers like "1.")
            body_text = []
            questions_text = []
            capture_questions = False
            
            for line in lines[1:]:
                if re.match(r'^\d+\.', line.strip()): # Detects "1. ", "2. "
                    capture_questions = True
                
                if capture_questions:
                    questions_text.append(line)
                else:
                    body_text.append(line)
            
            # RENDER CASE STUDY CARD
            st.markdown(f"""
            <div class="case-container">
                <div class="case-header">📂 Case Study: {title}</div>
                <div class="case-body">{' '.join(body_text)}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # RENDER QUESTIONS (If any found in this section)
            if questions_text:
                q_block = "\n".join(questions_text)
                # Split questions by number to make individual cards
                # This regex looks for a digit followed by a dot at start of line
                individual_qs = re.split(r'(?=\d+\.)', q_block)
                
                for q in individual_qs:
                    if q.strip():
                        # Highlight Answer if present
                        q_html = q.replace("\n", "<br>")
                        # Style the answer part green if possible
                        if "Answer:" in q_html:
                            parts = q_html.split("Answer:")
                            q_html = f"{parts[0]}<div class='answer-key'>✅ <b>Answer:</b> {parts[1]}</div>"
                        
                        st.markdown(f"""
                        <div class="question-container">
                            <div class="question-header">Question</div>
                            <div style="color: #ccc;">{q_html}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        else:
            # Fallback for text that isn't a case study (Intro/Outro)
            st.markdown(f"<div style='padding:10px;'>{section}</div>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=70)
    st.markdown("## ExamPrep AI")
    st.caption("v1.0.0 | Student Edition")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📂 Upload Slides (PDF/PPTX)", type=["pdf", "pptx", "docx"])
    
    if uploaded_file and not st.session_state.processed:
        with st.spinner("🔄 Ingesting Content..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                res = requests.post(f"{API_URL}/upload", files=files)
                if res.status_code == 200:
                    st.success("✅ File Processed!")
                    st.session_state.processed = True
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Upload Failed")
            except:
                st.error("❌ Backend Offline")

    st.markdown("---")
    st.markdown("### 🛠️ Controls")
    st.toggle("Deep Context Mode", value=True)
    st.toggle("Show Explanations", value=True)

# --- MAIN PAGE ---
st.title("Exam Simulation")
st.markdown("Generate real-world scenarios and test your knowledge.")

if st.session_state.processed:
    if st.button("✨ Generate New Exam"):
        with st.spinner("🧠 Analyzing content & drafting questions..."):
            try:
                res = requests.post(f"{API_URL}/generate", json={"request_type": "quiz"})
                st.session_state.quiz_content = res.json().get("result", "")
            except:
                st.error("Backend Connection Error")

    # --- RENDER RESULTS ---
    if st.session_state.quiz_content:
        st.markdown("---")
        render_beautiful_exam(st.session_state.quiz_content)
        
        st.markdown("---")
        st.download_button(
            "📥 Download Exam (.txt)", 
            st.session_state.quiz_content, 
            file_name="My_Exam_Prep.txt"
        )

else:
    # Empty State (Welcome Screen)
    st.info("👈 Upload your lecture slides to get started.")
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; color: #555;">
        <h3>How it works</h3>
        <p>1. Upload PDF • 2. AI Reads It • 3. Get Scenarios & MCQs</p>
    </div>
    """, unsafe_allow_html=True)