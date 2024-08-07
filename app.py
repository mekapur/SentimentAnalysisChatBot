import streamlit as st
import os
import requests
import sqlite3
import pandas as pd
 
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
        {"role": "system", "content": "Whenever you need to print an SQL query, ensure that you only print the query itself without any additional text, so it can be directly fed back into the code.There is a database named DataBases.xlsx, which contains four tables: Catalogue (item_id, item, quantity, price, colour, sizes), Order (order_id, item, size, quantity, price, status), Returns (order_id, item_id, tracking_number, status), Cart (item_id, item, quantity, price). Your task is to understand the user's request and ensure all necessary information is obtained before converting it into an SQL query that accesses this database. For example, if the user asks about the status of their order, first ask for the order ID. Only after receiving the order ID should you respond with an SQL query like SELECT status FROM \"Order\" WHERE order_id = 121348;. Ensure the query starts with SELECT and includes no extra quotations or words. If the user's question doesn't require database access, respond warmly and kindly as a customer service chatbot for a clothing store would. It is crucial to wait for all the necessary information from the user before generating an SQL query to avoid errors."
}
    ]
 
def get_response(user_input,context=None):
    # Add the user input to the conversation history
    st.session_state["conversation_history"].append({"role": "user", "content": user_input})
   
    # Define the payload with the updated conversation history
    payload = { 
        "model": "gpt-4o-mini",
        "messages": st.session_state["conversation_history"]
    }
 
    # Make the API request
    if context:
        payload["messages"].append({"role": "system", "content": context})
 
    response = requests.post(url, headers=headers, json=payload)
 
    # Extract the response content
    response_content = response.json()['choices'][0]['message']['content']
   
    # Add the assistant's response to the conversation history
    st.session_state["conversation_history"].append({"role": "assistant", "content": response_content})
   
    return response_content
 
def execute_query(query):
    conn = sqlite3.connect('your_database.db')
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result
 
# Sidebar for links
with st.sidebar:
    st.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")
    st.markdown("[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)")
    st.markdown("[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)")
 
# Title of the app
st.title("🛍️ Clothing Store Chatbot TESTING")
 
# Display all messages in the chat
for msg in st.session_state["conversation_history"]:
    st.chat_message(msg["role"]).write(msg["content"])
 
# Input prompt for user
if prompt := st.chat_input("You: "):
    st.session_state["conversation_history"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
   
    response = get_response(prompt)
 
    if "SELECT" in response:
        result = execute_query(response)
        context = f"The result of the query is: {result.to_dict(orient='records')}"
        final_response = get_response(prompt, context)
        st.chat_message("assistant").write(final_response)
    else:
        st.chat_message("assistant").write(response)