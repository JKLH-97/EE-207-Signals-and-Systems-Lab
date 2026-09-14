import streamlit as st

def render(title):
    st.title(f"EE-207 : {title}")
    st.info("This interactive module is coming soon.")
    st.write("Return to **Home** to choose another course topic.")
