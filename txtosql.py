import streamlit as st
import os
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
from langchain.chains import create_sql_query_chain, RunnablePassthrough
from langchain.prompts import ChatPromptTemplate

# Set the API token environment variable
os.environ['LLMFOUNDRY_TOKEN'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im1laGFrLmthcHVyQGdyYW1lbmVyLmNvbSJ9.HEuZlu0iPELnQfsjr15zoKwGZeQLQIAMcqOj42Qj4gQ'
openai_api_key = os.getenv('LLMFOUNDRY_TOKEN')

# Initialize OpenAI LLM
llm = OpenAI(model="gpt-3.5-turbo-1106", api_key=openai_api_key)

# Connect to the database
engine = create_engine('sqlite:///your_database.db')

# Define the Text-to-SQL prompt
text_to_sql_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", 
         "You are a PostgreSQL expert. Given an input question, create a syntactically correct PostgreSQL query to run and return ONLY the generated Query and nothing else. Unless otherwise specified, do not return more than {top_k} rows.\n\nHere is the relevant table info: {table_info}\nPay close attention on which column is in which table. if context contains more than one tables then create a query by performing JOIN operation only using the column unitid for the tables.\nFollow these Instructions for creating syntactically correct SQL query:\n- Be sure not to query for columns that do not exist in the tables and use alias only where required.\n- Always use the column 'instnm' associated with the 'unitid' in the generated query.\n- Whenever asked for Institute Names, return the institute names using column 'instnm' associated with the 'unitid' in the generated query.\n- Likewise, when asked about the average (AVG function) or ratio, ensure the appropriate aggregation function is used.\n- Pay close attention to the filtering criteria mentioned in the question and incorporate them using the WHERE clause in your SQL query.\n- If the question involves multiple conditions, use logical operators such as AND, OR to combine them effectively.\n- When dealing with date or timestamp columns, use appropriate date functions (e.g., DATE_PART, EXTRACT) for extracting specific parts of the date or performing date arithmetic.\n- If the question involves grouping of data (e.g., finding totals or averages for different categories), use the GROUP BY clause along with appropriate aggregate functions.\n- Consider using aliases for tables and columns to improve readability of the query, especially in case of complex joins or subqueries.\n- If necessary, use subqueries or common table expressions (CTEs) to break down the problem into smaller, more manageable parts."),
        ("human", "{input}")
    ]
)

# Create the SQL Query Chain
generate_sql_query = create_sql_query_chain(llm, engine, text_to_sql_prompt)

def execute_sql(query):
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return pd.DataFrame(result.fetchall(), columns=result.keys())

# Streamlit UI
st.title('Text-to-SQL Query Generator')

# User input
question = st.text_area('Enter your question:', 'List of Institutes accepting secondary school GPA for getting admission in Undergrad program')

if st.button('Generate SQL Query'):
    with st.spinner('Generating SQL query...'):
        query = generate_sql_query(question)
        st.code(query, language='sql')

        # Execute the query and display the results
        with st.spinner('Executing SQL query...'):
            results = execute_sql(query)
            st.dataframe(results)
