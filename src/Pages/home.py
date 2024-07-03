import streamlit as st
from datetime import datetime
from src.model.model_architecture import initialize_groq_client, chat_with_bot, get_title_from_groq
from src.Tools.Load import load_configuration
from src.model.History import store_conversation_history
from src.Tools.Prompt import load_templates
import os
import json

CONFIG_FILE_PATH = 'configs/model_config.yaml'
config = load_configuration(CONFIG_FILE_PATH)
Bot_name = config.get('bot_name')
DATA_DIRECTORY = 'data/History/'
INITIAL_MESSAGE = f"Hello! I'm {Bot_name}, your personal assistant. How can I help you today?"

def ensure_directory_exists(directory: str):
    os.makedirs(directory, exist_ok=True)

def store_llm_interaction(messages: list, title: str, timestamp: datetime):
    file_path = os.path.join(DATA_DIRECTORY, f"{timestamp}.json")
    ensure_directory_exists(os.path.dirname(file_path))
    interaction = store_conversation_history(messages)
    interaction["title"] = title
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            interactions = json.load(file)
    except FileNotFoundError:
        interactions = []
    interactions.append(interaction)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(interactions, file, indent=4)

def update_chat(role: str, content: str):
    st.session_state.messages.append({"role": role, "content": content})
    st.chat_message(role).write(content)

def process_input_with_template(user_input, templates):
    for wake_word, template in templates.items():
        if isinstance(template, str) and user_input.startswith(f"@{wake_word}"):
            query = user_input[len(wake_word)+2:].strip()
            return template.format(query=query)
        elif isinstance(template, list):
            for prompt in template:
                if user_input.startswith(f"@{prompt['title']}"):
                    query = user_input[len(prompt['title'])+2:].strip()
                    return prompt['prompt'].format(query=query)
    return user_input

def handle_user_input(client, session_timestamp):
    templates = load_templates()
    if prompt := st.chat_input():
        original_prompt = prompt
        prompt = process_input_with_template(prompt, templates)
        update_chat("user", original_prompt)
        bot_response = chat_with_bot(prompt, client, st.session_state.messages)
        update_chat("assistant", bot_response)
        title = get_title_from_groq(client, st.session_state.messages)
        store_llm_interaction(st.session_state.messages, title, session_timestamp)

def run():
    st.title(f"{Bot_name}.AI")
    session_timestamp = datetime.now().strftime('%Y-%m-%d_%H')  
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": INITIAL_MESSAGE}]
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
    client = initialize_groq_client()
    handle_user_input(client, session_timestamp)
    if st.button("Clear Conversation"):
        st.session_state.messages = [{"role": "assistant", "content": INITIAL_MESSAGE}]
        st.rerun()