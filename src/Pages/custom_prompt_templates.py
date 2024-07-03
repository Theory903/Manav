import streamlit as st
from src.model.prompt_model import load_templates, save_templates

def display_section_prompts(section, templates):
    """Display prompts for a given section."""
    st.subheader(f"{section} Prompts")
    if section in templates:
        for prompt in templates[section]:
            st.write(f"**Title:** {prompt['title']}")
            st.write(f"**Prompt:** {prompt['prompt']}")
            st.write("---")
        return True
    else:
        st.info("Select a section or create a new section to add prompts.")
        return False

def create_new_section(templates):
    """Create a new section based on user input."""
    new_section = st.text_input("Enter new section name:")
    if st.button("Create Section"):
        if new_section:
            if new_section not in templates:
                templates[new_section] = []
                save_templates(templates)
                st.success(f"Section '{new_section}' created successfully!")
            else:
                st.warning(f"Section '{new_section}' already exists.")
        else:
            st.error("Please enter a section name.")

def add_prompt_to_section(section, templates):
    """Add a new prompt to a selected section."""
    new_title = st.text_input(f"Enter new prompt title for '{section}':")
    new_prompt = st.text_area(f"Enter new prompt template for '{section}':")

    if st.button(f"Add to '{section}'"):
        if new_title and new_prompt:
            templates[section].append({"title": new_title, "prompt": new_prompt})
            save_templates(templates)
            st.success(f"Developer prompt '{new_title}' added to '{section}' successfully!")
        else:
            st.error("Please enter both title and prompt.")

def delete_section(section, templates):
    """Delete a selected section."""
    if st.button(f"Delete {section}"):
        if section in templates:
            del templates[section]
            save_templates(templates)
            st.success(f"Section '{section}' deleted successfully!")
            st.rerun()

def custom_prompt_templates():
    st.title("Custom Prompt Templates")
    templates = load_templates()

    st.write("""
    Create custom prompt templates with wake words. 
    Use the wake word with '@' prefix in the chat to activate the template.
    """)

    sections = list(templates.keys())
    section = st.selectbox("Choose section:", sections + ["Create New"])

    if section == "Create New":
        create_new_section(templates)
    else:
        add_prompt_to_section(section, templates)
        display_section_prompts(section, templates)
        delete_section(section, templates)

    st.subheader("Saved Templates")
    for sec, prompts in templates.items():
        st.write(f"**Section:** {sec}")
        for prompt in prompts:
            st.write(f"  - **Title:** {prompt['title']}")
            st.write(f"    **Prompt:** {prompt['prompt']}")
            st.write("---")
def run():
    custom_prompt_templates()
