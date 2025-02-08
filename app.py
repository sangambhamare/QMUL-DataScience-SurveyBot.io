import streamlit as st
import requests
import json
import pandas as pd
import os

# vLLM API Endpoint
VLLM_API_URL = "http://localhost:8000/v1/chat/completions"

# Define survey questions
survey_questions = [
    "How would you rate the teaching quality of this module? (1-5)",
    "How would you rate the module supervisor’s effectiveness? (1-5)",
    "How effective was the teaching method? (1-5)",
    "Was the behaviour of the teaching staff professional and helpful? (Yes/No)",
    "What improvements would you suggest for this module?"
]

# List of modules
modules = [
    "Applied Statistics",
    "Principles of Machine Learning",
    "Natural Language Processing",
    "Data Mining",
    "Big Data Processing",
    "Neural Network and Deep Learning",
    "Digital Media and Social Network",
    "Risk and Decision-Making for Data Science and AI"
]

# File path for storing responses
FEEDBACK_FILE = "survey_feedback.csv"

# Function to save feedback to CSV
def save_feedback(module, responses):
    df = pd.DataFrame([responses])  # Convert responses to DataFrame
    df.insert(0, "Module", module)  # Add module as the first column
    
    if os.path.exists(FEEDBACK_FILE):
        df.to_csv(FEEDBACK_FILE, mode='a', header=False, index=False)  # Append without header
    else:
        df.to_csv(FEEDBACK_FILE, index=False)  # Create a new file with headers

# Streamlit UI
st.title("Master's Student Survey Chatbot")
st.write("This chatbot collects feedback on your modules at QMUL. Please answer the questions honestly.")

# Select Module
target_module = st.selectbox("Select the module you want to provide feedback for:", modules)

# Survey responses
responses = {}
for question in survey_questions:
    if "(1-5)" in question:
        responses[question] = st.slider(question, 1, 5, 3)
    elif "(Yes/No)" in question:
        responses[question] = st.radio(question, ["Yes", "No"])
    else:
        responses[question] = st.text_area(question, "Enter your response here...")

# Submit button
if st.button("Submit Feedback"):
    save_feedback(target_module, responses)  # Store feedback in CSV
    
    # Format the input for vLLM model
    chat_input = {
        "model": "deepseek-ai/DeepSeek-R1",
        "messages": [
            {"role": "user", "content": f"Here is feedback for {target_module}: {json.dumps(responses)}"}
        ]
    }
    
    # Send request to vLLM API
    try:
        response = requests.post(VLLM_API_URL, headers={"Content-Type": "application/json"}, data=json.dumps(chat_input))
        if response.status_code == 200:
            output = response.json()["choices"][0]["message"]["content"]
            st.success("Thank you for your feedback! Your response has been recorded.")
            st.write("AI Response:", output)
        else:
            st.error("Error in processing your response. Please try again later.")
    except Exception as e:
        st.error(f"Error connecting to AI model: {e}")
