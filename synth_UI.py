import streamlit as st
import anthropic
from db import MongoEngine

# Assuming claude library is used to interface with Claude API and initialized similarly to OpenAI's library
client = anthropic.Anthropic(api_key="st.secrets["api_key"]")
mongo_engine = MongoEngine()

# Getting Response from Anthropic's LLM
def get_llm_response(chat_context, user_examples, user_query):
    """Get a response from the LLM using the chat history and knowledge list."""
    system_prompt = "[system prompt here]"
    user_messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Chat history: {chat_context}\nUser query: {user_query}\nExamples: {user_examples}"
                }
            ]
        }
    ]

    try:
        # Send the message to the Anthropic API and capture the response
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            temperature=0,
            messages=user_messages,
            system=system_prompt
        )

        # Extract text from the response if available
        if message and hasattr(message, 'content'):
            response_texts = [getattr(block, 'text', 'No text found') for block in message.content]
            return ' '.join(response_texts)
        elif hasattr(message, 'error'):
            error_message = getattr(message.error, 'message', 'Unknown error')
            return f"Error: {error_message}"
        else:
            return "No response from Claude."

    except Exception as e:
        # Log the exception for debugging
        print(f"Failed to get a response: {str(e)}")
        return "Failed to process your request."



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
    mongo_engine.save_form(response)
    st.session_state.chat_messages.append(f"AI: {response}")
    # Reset flag to prevent duplicate messages
    st.session_state.submit_flag = False
    # Refresh the page to show new messages
    st.experimental_rerun()
