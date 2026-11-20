import streamlit as st
# sets browser tab title, icon, and layout
st.set_page_config(
    page_title="AI Agent Security Incidents",
    page_icon="🛡️",
    layout="wide",
)
# Title 
st.title("AI Agent Security and Real-World Incidents (2024–26)")
st.subheader("A data visualization portfolio by Sayo Owolabi")
#Short Introduction to the app 
st.write(
    "This app explores real-world AI agent security incidents and vulnerabilities "
    "(217 records from a 395-record dataset). Use the sidebar to move between pages."
)
#Guide to pages 
st.markdown("""
**What's inside**
- **Bio**: who I am and how I approach data visualization
- **EDA Gallery**: five charts exploring the data, with guides on how to read them
- **Dashboard**: filter the data yourself and see the numbers update
- **Future Work**: what I will build next
""")
# Sidebar contact info (shows on every page)
st.sidebar.markdown("**Sayo Owolabi**")
st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/sayo-owolabi)")
