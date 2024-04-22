
import streamlit as st
import openai
import os
# Initialize OpenAI client
openai.api_key = 'YOUR API KEY'
os.environment["openai.api_key"]


#Getting Response from LLM
def get_llm_response(chat_context, user_examples, user_query):
    """Get a response from the LLM using the last 5 chat messages and knowledge_list."""
    messages = [
        {"role": "system", "content": f""" 

You are an AI assistant helping users order custom synthetic datasets. Please initiate a friendly conversation flow to gather the necessary details, following these steps:

1. Ask the user about the intended purpose or use case for the dataset they need - whether it's for classification or fine-tuning language models

2. If the purpose is classification, request the user to describe the classification task and provide any specific label sets they need.

3. If the purpose is fine-tuning in purpose of translation, instruction following, planning, tool usage, or reasoning - ask the user to describe the details of the task they need the dataset for.

4. Ask if the user would prefer aligning the dataset content to any particular human preferences or values by prompting with examples such as "Gender Bias",

    "Racial Bias",

    "Political Bias",

    "Religious Bias"

5. Request the user to specify the desired language for the dataset.

6. Inquire about the preferred entry count or size of the dataset.

7. Once all details are provided, summarize the overall request including a set of example entries to confirm with the user.

8. If the user approves the summary and examples, inform them that you'll send a recap of the finalized order via email.

9. Provide options to either save the order as a draft or proceed to payment and order initialization.

Get confirmation from the user by providing example entries within the 3rd, 4th, and 5th steps. Once you get all the answers just type "Thank you! I will inform you when your data is ready."
         
         """},
        {"role": "user", "content": f"Chat history: {chat_context}\nUser query: {user_query}\nExamples: {user_examples}"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo-2024-04-09",  # Replace with your model
        messages=messages
    )
    return response.choices[0].message['content'] if response else "No response from LLM."


# Streamlit App
st.title("Request Synthetic Data")

col1, col2, col3 = st.columns([6, 1, 2])

# Initialize chat messages and user entries in session state
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'user_examples' not in st.session_state:
    st.session_state.user_examples = ["", "", ""]
if 'submit_flag' not in st.session_state:
    st.session_state.submit_flag = False

with col1:
    st.subheader("Hello! I'm excited to help you create a custom synthetic dataset. Please let me know when you want to start.")
    for message in st.session_state.chat_messages:
        st.write(message)

    user_query = st.text_input("Enter your query:", key="user_query")
    submit_button = st.button("Submit", on_click=lambda: setattr(st.session_state, 'submit_flag', True))

with col3:
    st.write("Provide up to 3 examples:")
    for i in range(3):
        st.session_state.user_examples[i] = st.text_input(f"Example {i+1}:", key=f"example_{i}", value=st.session_state.user_examples[i])

if submit_button and user_query and st.session_state.submit_flag:
    # Append user query to chat context
    st.session_state.chat_messages.append(f"User: {user_query}")
    # Get response from LLM
    response = get_llm_response(st.session_state.chat_messages[-10:], st.session_state.user_examples, user_query)
    st.session_state.chat_messages.append(f"AI: {response}")
    # Reset flag to prevent duplicate messages
    st.session_state.submit_flag = False
    # Refresh the page to show new messages
    st.experimental_rerun()
