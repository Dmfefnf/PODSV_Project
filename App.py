import streamlit as st

pages = {
    "Home" : [st.Page("Home.py", default=True, title=None, icon="🏠")],
    "Analysis": [
        st.Page("pages/Univariate.py", title="Univariate Analysis", icon="📏"),
        st.Page("pages/Scatterplot.py", title="Scatterplot", icon="📈"),
        st.Page("pages/Correlation.py", title="Correlation Analysis", icon="🧮")
        ]
}
pg = st.navigation(pages)
pg.run()