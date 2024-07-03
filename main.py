import streamlit as st
from src.Pages import home, custom_prompt_templates, conversation_history_page

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Custom Prompt Templates", "Conversation History"])
    if page == "Home":
        home.run()
    elif page == "Custom Prompt Templates":
        custom_prompt_templates.run()
    elif page == "Conversation History":
        conversation_history_page.run()

if __name__ == "__main__":
    main()
