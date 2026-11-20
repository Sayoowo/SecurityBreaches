
import streamlit as st
from pathlib import Path
st.set_page_config(layout="wide")
st.title("👋 My Bio")
Name = "Sayo Owolabi"


Summary = (
    "I am a computer science student with interests in data visualization, machine learning, and AI security. "
    "I enjoy exploring real-world datasets and creating visualizations that communicate insights effectively. "
    "It allows me to uncover untold stories. "
    "For this project, I focused on analyzing security incidents involving AI agents, using Python, Pandas, and Plotly to create interactive visualizations. "
    "My goal is to make complex data accessible and understandable to a wide audience, while adhering to ethical standards in data representation."
)

Highlights = (
    "- Coursework: Data Science, Machine Learning, AI Security\n"
    "- Tools: Python, Pandas, Plotly, Streamlit\n"
    "- Focus Areas: Data Visualization, AI Security, Real-World Incident Analysis\n"
)


Brief_Statement = (
    "I believe that effective data visualization is about clarity, accessibility, and ethical representation. "
    "Visualizations should tell a story that is easy to understand, while ensuring that the data is presented accurately and responsibly. "
    "I strive to create visualizations that are not only informative but also engaging and accessible to diverse audiences."
)



PHOTO_PATH = "my_pic_small.jpg"  # photo lives in the assets/ folder (resized to 600px)


def find_photo(filename=PHOTO_PATH):
    # Try common locations for multipage apps
    try:
        script_dir = Path(__file__).resolve().parent
    except NameError:
        script_dir = Path.cwd()

    candidates = [
        script_dir / "assets" / filename,          # pages/assets/...
        script_dir.parent / "assets" / filename,   # root/assets/... (common)
        Path("assets") / filename,                 # cwd/assets/...
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None

photo_src = find_photo(PHOTO_PATH)

# --- Layout: photo on the left, summary on the right ---
col1, col2 = st.columns([1, 3])

with col1:
    if photo_src:
        st.image(photo_src, caption="Sayo Owolabi, headshot", width=200)
    else:
        st.info("Add my_pic_small.jpg to the assets folder to show a photo.")

with col2:
    st.header(Name)
    st.write(Summary)

st.subheader("Highlights")
st.markdown(Highlights)

st.subheader("My Visualization Philosophy")
st.write(Brief_Statement)

# Sidebar contact info (same on every page)
st.sidebar.markdown("**Sayo Owolabi**")
st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/sayo-owolabi)")
