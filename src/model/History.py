import time
import uuid
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from src.model.model_architecture import chat_with_bot, initialize_groq_client

# Initialize BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)

def is_key_prompt(prompt: str, threshold: float = 0.5) -> bool:
    """
    Determine if a prompt is a key prompt using a pre-trained BERT model.
    
    Args:
    prompt (str): The input prompt to evaluate.
    threshold (float): The probability threshold for classification as a key prompt.

    Returns:
    bool: True if the prompt is classified as a key prompt, False otherwise.
    """
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
    return probabilities[0][1].item() > threshold

def extract_key_prompts(history: list) -> list:
    """
    Extract key prompts from conversation history using a pre-trained model.
    
    Args:
    history (list): The conversation history.

    Returns:
    list: A list of key prompts extracted from the history.
    """
    user_prompts = [msg["content"] for msg in history if msg["role"] == "user"]
    return [prompt for prompt in user_prompts if is_key_prompt(prompt)]

def store_conversation_history(history: list) -> dict:
    """
    Store conversation history with a unique ID and additional metadata.
    
    Args:
    history (list): The conversation history to store.

    Returns:
    dict: A dictionary containing the stored conversation data.
    """
    unique_id = str(uuid.uuid4())
    timestamp = int(time.time())
    
    key_prompts = extract_key_prompts(history)
    conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    
    stored_data = {
        "id": unique_id,
        "timestamp": timestamp,
        "key_prompts": key_prompts,
        "conversation": conversation_text,
        "summary": generate_summary(history)
    }
    
    return stored_data

def generate_summary(history: list, max_length: int = 200) -> str:
    """
    Generate a summary of conversation history using a pre-trained model.
    
    Args:
    history (list): The conversation history to summarize.
    max_length (int): The maximum length of the generated summary.

    Returns:
    str: A summary of the conversation.
    """
    conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    
    summary_prompt = (
        "Please provide a comprehensive yet concise summary of the following conversation. "
        "Capture the main topics discussed, key points made, and any conclusions reached. "
        "This summary should serve as an effective representation of the entire conversation "
        f"when retrieved as history. Limit the summary to approximately {max_length} words:\n\n" + conversation_text
    )
    
    client = initialize_groq_client()
    summary = chat_with_bot(summary_prompt, client, [])

    return summary.strip()
