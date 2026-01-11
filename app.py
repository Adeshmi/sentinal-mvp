import streamlit as st
import json
import os
from openai import OpenAI

# Page Config
st.set_page_config(page_title="Sentinal AI", page_icon="🛡️", layout="wide")

try:
    api_key = st.secrets["OPENAI_API_KEY"]
except:
    # If running locally without st.secrets, look for .env or env var
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ OpenAI API Key missing. Please add it to Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# --- THE BRAIN (Formerly backend.py) ---
SYSTEM_PROMPT = """
### ROLE
You are "Sentinal," an elite AI Chief Information Security Officer (CISO).
Your goal is to audit contracts for security risks.

### OUTPUT FORMAT
You must respond in this EXACT JSON structure. Do not change the keys.
{
  "summary": "One sentence summary of the document's safety.",
  "risk_score": 15, 
  "critical_flags": [
    {
      "clause": "The exact text from the document",
      "issue": "Why this is dangerous",
      "recommendation": "The exact legal text to replace it with"
    }
  ]
}

### SCORING RULES
- If "Liability Cap" < $10,000 -> Risk Score is under 50.
- If "Data Ownership" is not Client -> Risk Score is under 20.
- If "Jurisdiction" is Cayman/Offshore -> Risk Score minus 10 points.
"""

def analyze_contract(text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Audit this contract:\n\n{text}"}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content

# --- THE FRONTEND ---
with st.sidebar:
    st.title("🛡️ Sentinal")
    st.write("AI Chief Security Officer")
    st.info("Beta v1.0 - Contract Scanner Module")

st.title("Upload Vendor Contract")
st.markdown("Instantly audit contracts for **GDPR, SOC2, and Liability Risks**.")

# Input
contract_text = st.text_area("Paste Contract Text Here", height=300)
uploaded_file = st.file_uploader("Or upload a .txt file", type=["txt"])

if uploaded_file is not None:
    contract_text = uploaded_file.read().decode("utf-8")

# Button
if st.button("Run Security Audit", type="primary"):
    if not contract_text:
        st.error("Please provide a contract to scan.")
    else:
        with st.spinner("Sentinal is analyzing legal risks..."):
            try:
                # Direct call to the brain function
                raw_response = analyze_contract(contract_text)
                result = json.loads(raw_response)

                # --- RESULTS DISPLAY ---
                st.success("Audit Complete")
                
                # Score
                score = result.get("risk_score", "N/A")
                st.metric("Risk Score", score)
                
                # Summary
                st.info(f"**Summary:** {result.get('summary', 'No summary provided')}")
                
                # Critical Flags
                st.subheader("🚩 Critical Risks Found")
                flags = result.get("critical_flags", [])
                
                if not flags:
                    st.write("No critical flags detected.")
                else:
                    for flag in flags:
                        with st.expander(f"Risk: {flag.get('issue', 'Unknown')}", expanded=True):
                            st.error(f"**Problem Clause:** \"{flag.get('clause')}\"")
                            st.code(f"Fix: {flag.get('recommendation')}", language="text")
                            
            except Exception as e:
                st.error(f"Error analyzing contract: {e}")