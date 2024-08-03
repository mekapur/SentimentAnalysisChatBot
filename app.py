import streamlit as st
import os
import requests

# Set the API token environment variable
os.environ['LLMFOUNDRY_TOKEN'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im1laGFrLmthcHVyQGdyYW1lbmVyLmNvbSJ9.HEuZlu0iPELnQfsjr15zoKwGZeQLQIAMcqOj42Qj4gQ'

# Define the API endpoint and headers
url = "https://llmfoundry.straive.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.environ['LLMFOUNDRY_TOKEN']}:my-test-project",
    "Content-Type": "application/json"
}

# Initialize conversation history
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = [
        {"role": "system", "content": "You are a helpful assistant for a clothing store."}
    ]

def get_response(user_input):
    # Add the user input to the conversation history
    st.session_state["conversation_history"].append({"role": "user", "content": user_input})
    
    # Define the payload with the updated conversation history
    payload = {
        "model": "gpt-4o-mini",
        "messages": st.session_state["conversation_history"]
    }

    # Make the API request
    response = requests.post(url, headers=headers, json=payload)

    # Extract the response content
    response_content = response.json()['choices'][0]['message']['content']
    
    # Add the assistant's response to the conversation history
    st.session_state["conversation_history"].append({"role": "assistant", "content": response_content})
    
    return response_content

# Sidebar for links
with st.sidebar:
    st.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")
    st.markdown("[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)")
    st.markdown("[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)")

# Title of the app
st.title("🛍️ Clothing Store Chatbot")

# Display all messages in the chat
for msg in st.session_state["conversation_history"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Input prompt for user
if prompt := st.chat_input("You: "):
    st.session_state["conversation_history"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    response = get_response(prompt)
    st.chat_message("assistant").write(response)
