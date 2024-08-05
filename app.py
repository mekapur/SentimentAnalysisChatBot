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
        {"role": "system", "content": "There is a database named DataBases.xlsx, which contains four tables: \n\nCatlogue (Item ID, item, In-Stock, Price, Colour, Sizes), \nOrder (Order Number, item, Size, Quantity, Price, Status), \nReturns (Order id, Item id, Tracking number, Status), \nShopping Cart (item id, item, quantity, price).\n\nYour task is to convert the user's input into an SQL query that accesses this database. For example, if the user asks, \"I want to know the status of my order,\" you should respond with an SQL query like SELECT Status FROM \"Order\" WHERE \"Order Number\" = 121348;. Ensure the query starts with SELECT and includes no extra quotations or words.\n\nIf the user's question doesn't require database access, respond warmly and kindly as a customer service chatbot for a clothing store would."
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