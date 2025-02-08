import streamlit as st
import json
import pandas as pd
import os
import subprocess
import requests

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

# GitHub Raw URL for token file
TOKEN_URL = "https://raw.githubusercontent.com/sangambhamare/QMUL-DataScience-SurveyBot.io/master/token.txt"

# Function to fetch the GitHub token from a private file
def get_github_token():
    try:
        response = requests.get(TOKEN_URL)
        if response.status_code == 200:
            return response.text.strip()
        else:
            print("Error: Unable to fetch token from GitHub.")
            return None
    except Exception as e:
        print(f"Failed to retrieve GitHub token: {e}")
        return None

# Function to save feedback to CSV and push to GitHub
def save_feedback(module, responses):
    df = pd.DataFrame([responses])  # Convert responses to DataFrame
    df.insert(0, "Module", module)  # Add module as the first column
    
    if os.path.exists(FEEDBACK_FILE):
        df.to_csv(FEEDBACK_FILE, mode='a', header=False, index=False)  # Append without header
    else:
        df.to_csv(FEEDBACK_FILE, index=False)  # Create a new file with headers

    # Fetch GitHub token from file
    GITHUB_TOKEN = get_github_token()
    if not GITHUB_TOKEN:
        print("Error: GitHub token not found.")
        return
    
    GITHUB_REPO = f"https://sangambhamare:{GITHUB_TOKEN}@github.com/sangambhamare/QMUL-DataScience-SurveyBot.io.git"
    
    try:
        subprocess.run(["git", "config", "--global", "user.email", "bhamaresangam@gmail.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "sangambhamare"], check=True)
        
        subprocess.run(["git", "add", FEEDBACK_FILE], check=True)
        subprocess.run(["git", "commit", "-m", "Update survey feedback CSV"], check=True)
        subprocess.run(["git", "push", GITHUB_REPO, "master"], check=True)
    except Exception as e:
        print(f"Git push failed: {e}")

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
    save_feedback(target_module, responses)  # Store feedback in CSV and push to GitHub
    st.success("Thank you for your feedback! Your response has been recorded and uploaded.")
