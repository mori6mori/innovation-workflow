import streamlit as st
import pdfplumber# PyMuPDF to extract text from PDFs
from openai import OpenAI
from PIL import Image
import pytesseract

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# Function to identify challenges using GPT
def identify_problem_with_gpt(text, territory, api_key):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI that identifies specific challenges or opportunity space from user interview transcripts. Limited the response for each challenge and opportunity space to 3 bullet points."},
            {"role": "user", "content": f"Identify the challenges or opportunity space in {territory} based on the following questions:\n{text}"}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content

# Streamlit UI
st.title("Problem & Opportunity Identifier")
st.write("Upload a PDF or enter your user interview transcript manually. The interviews can be uploaded as a single PDF/ text block. The app will identify problem and opportunity space using LLM.")

# Input for OpenAI API key
api_key = st.text_input("Enter your OpenAI API key:", type="password")

# Input for territory
territory = st.text_input("**Enter the territory you are researching:**")

# Choose between PDF upload or manual text input
option = st.radio(
    "Select Input Method:",
    ("Upload PDF", "Enter Text Manually")
)

input_text = ""

# Handle PDF Upload
if option == "Upload PDF":
    uploaded_file = st.file_uploader("Upload User Interview (PDF)", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            input_text = extract_text_from_pdf(uploaded_file)
        else:
            # For image files, use OCR to extract text
            image = Image.open(uploaded_file)
            input_text = pytesseract.image_to_string(image)

# Handle Manual Text Input
if option == "Enter Text Manually":
    input_text = st.text_area("Enter your interview questions below:")
    st.write("Enter questions, each on a new line.")

# Process the input using GPT
if st.button("Find the Problem NOW"):
    if input_text.strip() and territory and api_key:  # Ensure input text, territory, and API key are not empty
        with st.spinner("Identifying the problem and opportunity space..."):
            result = identify_problem_with_gpt(input_text, territory, api_key)
        st.subheader("Identified Problem + Opportunity Space:")
        st.write(result)

        # Provide option to download results as a text file
        st.download_button(
            label="Download Results",
            data=result,
            file_name="identified_challenges.txt",
            mime="text/plain",
        )
    else:
        st.warning("Please provide some input text or upload a PDF, enter the territory you are researching, and provide your OpenAI API key.")