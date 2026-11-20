import streamlit as st

st.set_page_config(layout="wide")
st.title("🧭 Future Work")
st.write("What I would build next, and how this project changed along the way.")

# ------------------------------------------------------------
# NEXT STEPS — 5 concrete improvements, each tied to a limit
# found while building this app
# ------------------------------------------------------------
st.subheader("Next steps")

st.markdown("""
1. **Stronger forecasting.** The 2028 projection is a straight line fitted to about 21 months, with a wide uncertainty range. With more months of data, I would compare models (e.g., seasonal trends) and test them on held-back months before showing them.
2. **Text analysis of incident summaries.** Every record has a written `summary`. I would group these by topic (for example, using keyword or topic modeling) to find attack patterns the type labels miss.
3. **Add a second dataset with exact locations.** Most records are tagged "Global," and map positions for regions are approximate. Joining a source like the NVD vulnerability database could add precise locations and severity scores (CVSS) for a true histogram.
4. **Automatic data refresh.** Pull new records from Kaggle on a schedule so the dashboard stays current, and show the real download date instead of the file date.
5. **Accessibility audit.** Test the app with a screen reader and a color-blindness simulator, and add a high-contrast mode.
""")

# ------------------------------------------------------------
# REFLECTION — what changed from the Lab 4.3 paper prototype
# (2–4 bullets, in my own words)
# ------------------------------------------------------------
st.subheader("Reflection: from paper prototype to final app")

st.markdown("""
- TODO: what my prototype planned vs. what I built
- TODO: a chart I changed and why
- TODO: something the data taught me that I didn't expect
""")

# Sidebar contact info (same on every page)
st.sidebar.markdown("**Sayo Owolabi**")
st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/sayo-owolabi)")
