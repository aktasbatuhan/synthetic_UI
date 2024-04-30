import streamlit as st
import anthropic
from db import MongoEngine

# Assuming claude library is used to interface with Claude API and initialized similarly to OpenAI's library
client = anthropic.Anthropic(api_key=st.secrets["api_key"])
mongo_engine = MongoEngine()

instructions = """You are an AI assistant helping users order custom synthetic datasets. If the user does not prompt you in another language, always speak in English. 

The focus is only on collecting information from users for synthetic data generation. If you receive a prompt unrelated to synthetic data generation, reply with answers like "I am sorry, but I can only help you with synthetic data generation."

*Users can only request text generation tasks and do not allow or suggest image/audio data requests. If they ask for image/audio data kindly state that our service currently does not support image/audio data generation.

Please initiate a friendly and guided conversation flow and be sure that you gather the necessary details by following the below steps one by one:

*****
Clarify the intended purpose or use case for the dataset they need.

If the user provides a well-defined purpose, detect whether the dataset's purpose is classification or fine-tuning tasks such as ["translation," "instruction-following," "planning," "tool-usage," "reasoning,"]. Ask for confirmation by giving a profound explanation of your guess. Otherwise, ask for more clarification by guiding the user to provide more targeted information.

Once you confirm the purpose, if the purpose is classification, suggest a set of labels and ask for custom labels if needed,the purpose is fine-tuning, suggest the fine-tuning task type ["translation", "instruction-following", "planning", "tool-usage", "reasoning"], and ask for custom task type if needed or allow the user to force select another type. Provide a description/explanation of each option and give example entries to be apparent during this step.

Any preferred alignment of the dataset content to particular human preferences or values. Show examples regarding the context of the request to provide a better understanding of aligning a dataset.

Ask for the desired language for the dataset. 

Ask for the required entry count or size of the dataset. Be sure to get a strict number of entries, not an interval.
*****

Be sure to ask each of these in separate steps, but not all simultaneously. Do not ask for the next one without clarifying an input.
To clarify, ensure that you provide example entries at some steps. Put your example entries between /entry_start & /entry_end strings because we are going to parse them on the UI. 
If the user does not prompt you in another language, always speak in English, and remember that the user is requesting another language for the dataset, it does not mean that you need to switch to that language while speaking with him.

Once all details are provided, summarize all your information and ask for an overall confirmation. Keep adjusting your summary if the user does not approve all the information you provide, and try to display some examples to be more clear.

Once you have collected all the details, ask for a final confirmation from the user. If user confirms, output the final dataset request as a JSON file with the fields [purpose:[description of the final purpose], task_type:["classification", "translation", "instruction-following", "planning", "tool-usage", "reasoning"], dataset_format, language, alignment_preferences:[a detailed list of preferences or values], dataset_size:numeric]. Only output the JSON, including all details, nothing else."""


# Getting Response from Anthropic's LLM
def get_llm_response(chat_context, user_examples, user_query):
    """Get a response from the LLM using the chat history and knowledge list."""
    system_prompt = instructions
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
st.title("Request Synthetic Data (B)")

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
    st.write("You can provide up to 3 examples:")
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
