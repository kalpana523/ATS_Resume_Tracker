import streamlit as st
import cohere
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import re
import json
import pandas as pd
import altair as alt

# Load environment variables
load_dotenv()

# Configure Cohere API
co = cohere.Client(os.getenv("COHERE_API_KEY"))

# Function to generate response using Cohere
def get_cohere_response(prompt):
    response = co.generate(
        model='command-r-plus',  # Use 'command-r' if 'command-r-plus' isn't accessible
        prompt=prompt,
        max_tokens=500,
        temperature=0.3,
        stop_sequences=["}"]
    )
    return response.generations[0].text.strip()

# Extract text from uploaded PDF resume
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Simple keyword extraction from text
def extract_keywords(text):
    # Lowercase, split words, remove common stopwords
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = {"and", "or", "with", "a", "the", "to", "of", "in", "on", "for", "is", "are", "as", "an", "your", "you", "must"}
    keywords = set([w for w in words if w not in stop_words])
    return sorted(list(keywords))

# Prompt template
input_prompt = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resumes. Assign the percentage Matching based 
on JD and the missing keywords with high accuracy.
resume: {text}
description: {jd}

I want the response in one single string having the structure:
{{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
"""

# Streamlit UI
st.title("Smart ATS")
st.text("Improve Your Resume ATS")

# Job Description Input
jd = st.text_area("📄 Paste the Job Description")

# Resume PDF Upload
uploaded_file = st.file_uploader("📎 Upload Your Resume", type="pdf", help="Please upload the PDF")

# Submit Button
submit = st.button("🚀 Submit")

if submit:
    if not jd:
        st.warning("⚠️ Please paste the job description.")
    elif not uploaded_file:
        st.warning("⚠️ Please upload your resume.")
    else:
        with st.spinner("🔍 Analyzing your resume..."):
            text = input_pdf_text(uploaded_file)
            final_prompt = input_prompt.format(text=text, jd=jd)
            response = get_cohere_response(final_prompt)

            import json
            import pandas as pd
            import altair as alt

            st.subheader("📊 ATS Analysis Result")

            try:
                parsed_result = json.loads(response)

                # JD Match
                st.metric(label="✅ JD Match", value=parsed_result["JD Match"])

                # Columns for Keywords and Profile
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.markdown("### 🔍 Missing Keywords")
                    if parsed_result["MissingKeywords"]:
                        for kw in parsed_result["MissingKeywords"]:
                            st.markdown(f"- ❌ `{kw}`")
                    else:
                        st.success("✅ All required keywords are present!")

                with col2:
                    st.markdown("### 🧾 Profile Summary")
                    st.write(parsed_result["Profile Summary"])

            except Exception as e:
                st.error("⚠️ Error parsing the response. Showing raw text:")
                st.code(response)
