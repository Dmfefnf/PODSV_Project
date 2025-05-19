import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.header("📏 Univariate analysis – Numerical Variables")
st.markdown("""
On this page, you can explore the **distribution and key statistics of individual numerical variables**.

You can:
- Select any numerical variable in your dataset
- (Optionally) apply a filter to focus on specific subgroups
- View basic **descriptive statistics** (mean, standard deviation, min/max, etc.)
- See **quantile statistics** (min, Q1, median, Q3, max)
- Explore the **distribution visually** via a histogram
- Identify potential **outliers** using a boxplot

With the functionality of plotly you can do the following with the plots:
- **Hover**: Hover over points to see their values.
- **Save**: Click the camera icon in the top right corner to save the plot as an image.
- **Zoom**: Click and drag to zoom in on a specific area of the plot or use the zoom buttons.
- **Pan**: Click and drag to move the plot around.
- **Autoscale**: Click the home icon or the autoscale button to reset the zoom level.
- **Fullscreen**: Click the full screen icon to view the plot in full screen mode.   
""")

# # Sidebar navigation
# st.sidebar.page_link("Home.py", label="Home", icon="🏠")
# st.sidebar.page_link("Scatterplot.py", label="Scatterplot", icon="📈")
# st.sidebar.page_link("Correlation.py", label="Correlation Analysis", icon="🧮")

# if st.sidebar.button("🔄 Reset"):
#     for key in list(st.session_state.keys()):
#         del st.session_state[key]
#     # Datei-Upload-Widget neu initialisieren (zwingt Streamlit zur Neuerstellung)
#     st.session_state["file_uploader_key"] = str(pd.Timestamp.now().timestamp())
#     st.rerun()

# Lade DataFrame aus Session State
if "df" not in st.session_state:
    st.warning("Please upload a file to the homepage first.")
    st.stop()

df = st.session_state["df"]
# Numerische Spalten filtern
# num_cols = df.select_dtypes(include="number").columns.tolist()
# col_types = st.session_state.get("column_types", {})
# Load column types from session state
column_types = st.session_state["column_types"]
num_cols = [col for col, dtype in column_types.items() if dtype == "numerical"]
cat_cols = [col for col, dtype in column_types.items() if dtype == "categorical"]

if not num_cols:
    st.warning("No numerical rows in dataset found.")
    st.stop()
df_numeric = df[num_cols]
# Spaltenauswahl
selected_col = st.selectbox("Choose a numerical variable", num_cols)
# Is necessary so that race condition is not triggered
# st.write(f"Selected column: {selected_col}")
with st.expander("**ℹ️ Why filter?**"):
    st.markdown("""
    Filtering allows you to focus on specific subsets of your data. This can help uncover correlations that might be hidden in the full dataset, especially when different groups behave differently.

    There are two types of filtering:

    - **Filtering by a categorical variable** (e.g., gender, region, product type):  
      Only rows that match one or more selected categories will be included.  
      Example: *Analyze data only for female respondents.*

    - **Filtering by a numerical variable** (e.g., age, income, temperature):  
      Only rows within a selected range will be included.  
      Example: *Analyze data only for ages between 30 and 50.*

    You can leave the filter empty to use the full dataset.
    """)

filter_col = st.selectbox("Filter using another Variable (optional)",
                              [None] + list(df.columns), 
                              format_func=lambda x: "None" if x is None else x
                              )

df_filtered = df

if filter_col is not None:
        # Check if the selected filter column is numerical or categorical
        # and apply the appropriate filter
        # If the filter column is numerical, use a slider
        if column_types[filter_col] == "numerical":
            min_val = float(df[filter_col].min())
            max_val = float(df[filter_col].max())
            range_val = st.slider("Choose value range", min_val, max_val, (min_val, max_val))
            df_filtered = df[df[filter_col].between(*range_val)]
        # If the filter column is categorical, use a multiselect
        elif column_types[filter_col] == "categorical":
            options = sorted(df[filter_col].dropna().unique().tolist())
            selected = st.multiselect("Choose a category (multiple possible)", options, default=options)
            df_filtered = df[df[filter_col].isin(selected)]

if selected_col and selected_col in df.columns:
    # Deskriptive Statistiken
    st.subheader("📊 Descriptive statistics")
    with st.expander("**ℹ️ What do descriptive statistics tell us?**"):
        st.markdown("""
            Descriptive statistics provide a summary of the main characteristics of a dataset. They include measures such as:
            - **Count**: The number of non-null entries.
            - **Mean**: The average value.
            - **Standard deviation (std)**: A measure of the amount of variation or dispersion in the dataset.
            - **Minimum and maximum**: The smallest and largest values, respectively.
            """)
    # Descriptive statistics without the 25th, 50th and 75th percentiles (since they are shown in the quantile statistics)
    st.write(df_filtered[selected_col].describe().drop(["25%", "50%", "75%"]))
    # st.write(df_filtered[selected_col].describe())

    # Quantile
    st.subheader("📏 Quantile statistics")
    with st.expander("**ℹ️ What do quantile statistics tell us?**"):
        st.markdown("""
            Quantile statistics provide insights into the distribution of the data. They include:
            - **0%**: The minimum value.
            - **25% (Q1)**: The first quartile, which is the median of the lower half of the dataset.
            - **50% (Q2)**: The median, which divides the dataset into two equal halves.
            - **75% (Q3)**: The third quartile, which is the median of the upper half of the dataset.
            - **100%**: The maximum value.
            """)
    st.write(df_filtered[selected_col].quantile([0, 0.25, 0.5, 0.75, 1.0]))

    # Histogramm
    # st.subheader("📊 Histogram")
    # fig, ax = plt.subplots()
    # ax.hist(df[selected_col].dropna(), bins=20, color="skyblue", edgecolor="black")
    # ax.set_title(f"Histogramm von {selected_col}")
    # st.pyplot(fig)

    st.subheader("📊 Histogram")
    with st.expander("**ℹ️ What does a histogram tell us?**"):
        st.markdown("""
            A histogram is a graphical representation of the **distribution** of numerical data.   
            It divides the data into bins and shows the frequency of data points in each bin.  
            This helps to visualize the **shape**, **spread**, and **central tendency** of the data.
            """)
    fig_hist = px.histogram(df_filtered, x=selected_col, nbins=20, title=f"Histogram of {selected_col}")
    st.plotly_chart(fig_hist)

    # Boxplot
    # st.subheader("📦 Boxplot")
    # fig2, ax2 = plt.subplots()
    # ax2.boxplot(df[selected_col].dropna(), vert=False)
    # ax2.set_title(f"Boxplot von {selected_col}")
    # st.pyplot(fig2)

    st.subheader("📦 Boxplot")
    with st.expander("**ℹ️ What does a boxplot tell us?**"):
        st.markdown("""
            A boxplot (or whisker plot) provides a visual summary of the **central tendency**, **spread**, and **skewness** of the data.  
            It displays the median, quartiles (q1 and q3), and potential outliers.  
            The box represents the interquartile range (IQR), while the lines (whiskers) extend to the minimum and maximum values within 1.5 times the IQR.
            """)
    fig_box = px.box(df_filtered, x=selected_col, title=f"Boxplot of {selected_col}", points="outliers")
    st.plotly_chart(fig_box)
else:
    st.warning("Please select a numerical variable to analyze.")
