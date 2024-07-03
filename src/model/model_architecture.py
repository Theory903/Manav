import logging
import os
from typing import List, Dict, Optional, Tuple
from groq import Groq
from src.Tools.Load import load_configuration
from src.model.prompt_model import find_prompt_by_title, load_templates

# Constants
CONFIG_FILE_PATH = 'configs/model_config.yaml'                                                
LOG_FILE_PATH = 'data/Logs/app.log'

# Load configuration
config = load_configuration(CONFIG_FILE_PATH)

# Configuration values
DEFAULT_API_KEY = config.get('api_key')
MODEL_NAME = config.get('model_name')
MAX_TOKENS = config.get('max_tokens')
TEMPERATURE = config.get('temperature')
TOP_P = config.get('top_p')
STREAM = config.get('stream')
AGENTS = config.get('agent')
BOT_NAME = config.get('bot_name')
DEFAULT_SYSTEM_PROMPT = config.get('default_system_message')

# Logging setup
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=LOG_FILE_PATH,
    filemode='a'
)

def log_configuration():
    """Log configuration details."""
    logging.info("Configuration loaded from model_config.yaml:")
    for key, value in config.items():
        logging.info(f"{key.capitalize()}: {value}")

log_configuration()

def initialize_groq_client(api_key: Optional[str] = None) -> Groq:
    """Initialize the Groq client."""
    api_key = api_key or os.environ.get("GROQ_API_KEY", DEFAULT_API_KEY)
    return Groq(api_key=api_key)

def generate_optimized_system_prompt(client: Groq, question: str) -> str:
    """Generate an optimized system prompt based on the user's question."""
    prompt_generator_message = f"""
    Analyze the following user question and generate a concise,
    effective system prompt that will guide the AI to provide the best possible answer. 
    The system prompt should be tailored to the question type and domain.

    User question: {question}

    Generate a system prompt that:
    1. Identifies the type of question (e.g., coding, history, science, creative writing)
    2. Specifies the appropriate tone and style for the answer
    3. Includes any necessary domain-specific instructions
    4. Is concise and direct (50 words or less)

    Respond with only the generated system prompt, without any additional text.
    """

    messages = [
        {"role": "system", "content": "You are an AI assistant that generates optimized system prompts."},
        {"role": "user", "content": prompt_generator_message}
    ]

    try:
        response = client.chat.completions.create(
            messages=messages,
            model=MODEL_NAME,
            max_tokens=100,
            temperature=0.7
        )
        optimized_prompt = response.choices[0].message.content.strip()
        # Combine the optimized prompt with the default prompt
        combined_prompt = f"{optimized_prompt}\n\n{DEFAULT_SYSTEM_PROMPT.format(Bot_name=BOT_NAME, Agents=AGENTS)}"
        return combined_prompt
    except Exception as e:
        logging.error(f"Error generating optimized system prompt: {e}", exc_info=True)
        return DEFAULT_SYSTEM_PROMPT.format(Bot_name=BOT_NAME, Agents=AGENTS)

def process_wake_word(prompt: str) -> Tuple[str, Optional[str]]:
    """Process wake word and return the updated prompt and custom system message."""
    if prompt.startswith('@'):
        parts = prompt.split(maxsplit=1)
        if len(parts) > 1:
            wake_word, user_query = parts
            wake_word = wake_word[1:]  # Remove the '@' symbol
            
            templates = load_templates()
            prompt_text = find_prompt_by_title(wake_word, templates)
            
            if prompt_text:
                # Combine the wake word prompt with the default prompt
                combined_prompt = f"{prompt_text.format(query=user_query)}\n\n{DEFAULT_SYSTEM_PROMPT.format(Bot_name=BOT_NAME, Agents=AGENTS)}"
                return user_query, combined_prompt
            else:
                return "", f"No prompt found for wake word '{wake_word}'."
        else:
            return "", "Please provide a query after '@'."
    return prompt, None

def chat_with_bot(prompt: str, client: Groq, history: List[Dict[str, str]]) -> str:
    """Simulate a conversation with a bot."""
    prompt, custom_system_message = process_wake_word(prompt)
    
    if not prompt:
        return custom_system_message or "Invalid input. Please try again."

    optimized_system_prompt = generate_optimized_system_prompt(client, prompt)
    
    system_message = {
        "role": "system",
        "content": custom_system_message or optimized_system_prompt
    }

    messages = [system_message] + history + [{"role": "user", "content": prompt}]
    
    logging.info(f"System Prompt: {system_message['content']}")
    logging.info(f"User Prompt: {prompt}")
    logging.info(f"Conversation history: {messages}")

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=MODEL_NAME,
            max_tokens=MAX_TOKENS,
            stream=STREAM,
            temperature=TEMPERATURE,
            top_p=TOP_P
        )
        return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        logging.error(f"Error occurred during chat completion: {e}", exc_info=True)
        return f"I apologize, but an error occurred while processing your request. Please try again later."

def get_title_from_groq(client: Groq, messages: List[Dict[str, str]]) -> str:
    """Get the title from Groq based on conversation history."""
    conversation_text = "\n".join(msg["content"] for msg in messages)
    title_prompt = f"Please provide a concise and relevant title (5 words or less) for the following conversation:\n{conversation_text}"
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": title_prompt}],
            model=MODEL_NAME,
            max_tokens=20,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error generating title: {e}", exc_info=True)
        return "Untitled Conversation"