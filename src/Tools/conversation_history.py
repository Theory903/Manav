import os
import json
import streamlit as st
from datetime import datetime

_DATA_DIRECTORY = 'data/History/'

def load_conversation_history() -> list[dict]:
    """Loads conversation history from JSON files in the data directory."""
    conversations = []
    for filename in os.listdir(_DATA_DIRECTORY):
        if filename.endswith('.json'):
            with open(os.path.join(_DATA_DIRECTORY, filename), 'r', encoding='utf-8') as file:
                conversations.extend(json.load(file))
    return sorted(conversations, key=lambda x: x.get('timestamp', ''), reverse=True)

def parse_timestamp(timestamp: str) -> datetime:
    """Parses a timestamp string into a datetime object."""
    if isinstance(timestamp, int):
        return datetime.fromtimestamp(timestamp)
    if not isinstance(timestamp, str):
        return datetime.min

    try:
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(timestamp, "%Y-%m-%d_%H")
        except ValueError:
            return datetime.min

def display_conversation(conversation: dict):
    """Displays a conversation with title, timestamp, and messages."""
    st.subheader(conversation.get('title', 'Untitled Conversation'))
    timestamp = parse_timestamp(conversation.get('timestamp'))
    st.write(f"Date: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown(f"**Summary:** {conversation.get('summary', 'No summary available')}")
    st.markdown(f"**Conversation:**\n```\n{conversation.get('conversation', 'No conversation available')}\n```")
    st.divider()

def conversation_history_page():
    """Displays conversation history with filters."""
    st.title("Conversation History")

    conversations = load_conversation_history()

    if not conversations:
        st.write("No conversation history found.")
        return

    # Add a date filter
    timestamps = [parse_timestamp(conv.get('timestamp', '')) for conv in conversations]
    valid_timestamps = [ts for ts in timestamps if ts != datetime.min]

    if not valid_timestamps:
        st.write("No valid timestamps found in the conversation history.")
        return

    min_date = min(valid_timestamps).date()
    max_date = max(valid_timestamps).date()

    date_filter = st.date_input("Filter by date", 
                                value=(min_date, max_date),
                                min_value=min_date,
                                max_value=max_date)

    # Add a search box
    search_query = st.text_input("Search conversations", placeholder="Enter search query")

    filtered_conversations = [
        conv for conv in conversations
        if date_filter[0] <= parse_timestamp(conv.get('timestamp', '')).date() <= date_filter[1]
        and (search_query.lower() in conv.get('title', '').lower() or
             search_query.lower() in conv.get('summary', '').lower() or
             search_query.lower() in conv.get('conversation', '').lower())
    ]

    for conversation in filtered_conversations:
        display_conversation(conversation)

if __name__ == "__main__":
    conversation_history_page()
