import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.header("📈 Scatterplot with color coding")
st.markdown("""
On this page, you can create a **scatterplot** to visualize the relationship between two numerical variables. With the functionality of plotly you can do the following:  
            
- **Hover**: Hover over points to see their values.
- **Save**: Click the camera icon in the top right corner to save the plot as an image.
- **Zoom**: Click and drag to zoom in on a specific area of the plot or use the zoom buttons.
- **Pan**: Click and drag to move the plot around.
- **Autoscale**: Click the home icon or the autoscale button to reset the zoom level.
- **Fullscreen**: Click the full screen icon to view the plot in full screen mode.            
"""
)
with st.expander("**ℹ️ What is a scatterplot?**"):
    st.markdown("""
    A scatterplot displays the relationship between two numerical variables by showing points on a two-dimensional graph.  
    Each point represents a single observation in your dataset, with:

    - the **X-axis** representing one variable
    - the **Y-axis** representing another variable
    - (optionally) **color** indicating a third variable (either numerical or categorical)

    Scatterplots help detect patterns, clusters, and possible correlations.  
    They are especially useful to spot trends or outliers.
    """)

def interpret_corr(corr):
    if corr >= 0.75:
        return "Strong positive correlation"
    elif corr >= 0.5:
        return "Moderate positive correlation"
    elif corr >= 0.25:
        return "Weak positive correlation"
    elif corr > -0.25:
        return "No correlation"
    elif corr >= -0.5:
        return "Weak negative correlation"
    elif corr >= -0.75:
        return "Moderate negative correlation"
    else:
        return "Strong negative correlation"
# Navigation sidebar
# st.sidebar.page_link("Home.py", label="Home", icon="🏠")
# st.sidebar.page_link("Univariate.py", label="Univariate Analysis", icon="📏")
# st.sidebar.page_link("Correlation.py", label="Correlation Analysis", icon="🧮")

# if st.sidebar.button("🔄 Reset"):
#     for key in list(st.session_state.keys()):
#         del st.session_state[key]
#     # Datei-Upload-Widget neu initialisieren (zwingt Streamlit zur Neuerstellung)
#     st.session_state["file_uploader_key"] = str(pd.Timestamp.now().timestamp())
#     st.rerun()

# Check if DataFrame exists in Session State
# and if not, show a warning message
if "df" not in st.session_state:
    st.warning("Please upload a file to the homepage first.")
    st.stop()
# Load DataFrame and Column Types from Session State
df = st.session_state["df"]
col_types = st.session_state.get("column_types", {})
# Load column types from session state
column_types = st.session_state["column_types"]
# Spaltenauswahl
num_cols = [col for col, dtype in col_types.items() if dtype == "numerical"]
cat_cols = [col for col, dtype in col_types.items() if dtype == "categorical"]
df_numeric = df[num_cols]
# num_cols = df.select_dtypes(include="number").columns.tolist()
# cat_cols = df.select_dtypes(include="object").columns.tolist()

if len(num_cols) < 2:
    st.warning("At least 2 numerical values are necessary.")
    st.stop()

x_col = st.selectbox("X-Axis", num_cols)
y_col = st.selectbox("Y-Axis", num_cols, index=1)

# Farbvariable (optional)
color_col = st.selectbox("Coloring coding (optional)", [None] + num_cols + cat_cols)

# Filter (optional)
# filter_col = st.selectbox("Filterspalte (optional)", [None] + num_cols + cat_cols)
# filtered_df = df.copy()
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
    # Filter DataFrame even if no filter is selected
df_filtered = df
# if filter_col:
#     unique_vals = df[filter_col].dropna().unique()
#     selected_vals = st.multiselect("Filterwerte auswählen", unique_vals, default=unique_vals)
#     filtered_df = df[df[filter_col].isin(selected_vals)]
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
# Scatterplot mit Plotly
fig = px.scatter(
    df_filtered,
    x=x_col,
    y=y_col,
    color=color_col,
    title=f"Scatterplot: {x_col} vs {y_col}"
)

st.plotly_chart(fig, use_container_width=True)

x_col = df_filtered[x_col]
y_col = df_filtered[y_col]
# Correlation
correlation = x_col.corr(y_col)
# Interpretation
interpretation = interpret_corr(correlation)

# Correlation Interpretation DataFrame
df_result = pd.DataFrame({
    "Correlation": [f"{correlation:.4f}"],
    "Interpretation": [interpretation]
})
# Styling für DataFrame
df_result.index = ["Correlation between variables"]  # Index abändern

# Styling für Links-Ausrichtung
styled = df_result.style.set_properties(**{
    'text-align': 'left'
}).set_table_styles([
    dict(selector='th', props=[('text-align', 'left')])
])
st.markdown("### 🔍 Correlation Details")
st.dataframe(styled, use_container_width=True, height=70)
with st.expander("**ℹ️ What does correlation mean?**"):
    st.markdown("""
Correlation measures the strength and direction of a linear relationship between two numerical variables.  
It ranges from **-1** (perfect negative) to **+1** (perfect positive):

- **Positive correlation**: As one variable increases, the other tends to increase.
- **Negative correlation**: As one variable increases, the other tends to decrease.
- **Zero correlation**: No linear relationship.

Keep in mind: Correlation does **not** imply causation.
""")


