import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io

st.title("🧮 Correlation Analysis")
st.markdown(
    """
    This page allows you to analyze the **correlation** between different numerical columns in your dataset.  
    As standard, all numerical columns are selected for the analysis. You can choose specific columns for the correlation analysis by using the multiselect option.  
    You can also **filter** the data based on a categorical or numerical variable.  
    Below the correlation matrix, you will find a **download button** to save the correlation matrix as a CSV file and the correlation graph as a PNG file.
    """
)
with st.expander("**ℹ️ What does correlation mean?**"):
    st.markdown("""
    Correlation measures the strength and direction of a linear relationship between two numerical variables.  
    It ranges from **-1** (perfect negative) to **+1** (perfect positive):
    
    - **Positive correlation**: As one variable increases, the other tends to increase.
    - **Negative correlation**: As one variable increases, the other tends to decrease.
    - **Zero correlation**: No linear relationship.
    
    Keep in mind: Correlation does **not** imply causation.
    """)

# if st.sidebar.button("🔄 Reset"):
#     for key in list(st.session_state.keys()):
#         del st.session_state[key]
#     # Datei-Upload-Widget neu initialisieren (zwingt Streamlit zur Neuerstellung)
#     st.session_state["file_uploader_key"] = str(pd.Timestamp.now().timestamp())
#     st.rerun()

# Only show this page if a DataFrame is available
if "df" in st.session_state:
    # Load DataFrame from session state
    df = st.session_state["df"]
    # Load column types from session state
    column_types = st.session_state["column_types"]
    # Select only numeric columns
    col_types = st.session_state.get("column_types", {})
    numeric_cols = [col for col, dtype in col_types.items() if dtype == "numerical"]
    df_numeric = df[numeric_cols]

    # Select columns for correlation analysis
    selected_cols = st.multiselect(
        "Choose columns for correlation analysis",
        options=numeric_cols,
        default=numeric_cols
    )
    # Filter using another variable
    with st.expander("**ℹ️ Why filter?**"):
        st.markdown("""
    Filtering allows you to focus on specific subsets of your data. This can help uncover correlations that might be hidden in the full dataset, especially when different groups behave differently.

    There are two types of filtering:

    - **Filtering by a categorical variable** (e.g., gender, region, product type):  
      Only rows that match one or more selected categories will be included.  
      Example: *Analyze correlations only for female respondents.*

    - **Filtering by a numerical variable** (e.g., age, income, temperature):  
      Only rows within a selected range will be included.  
      Example: *Analyze correlations only for ages between 30 and 50.*

    You can leave the filter empty to use the full dataset.
    """)
    # Select Variable for filtering
    filter_col = st.selectbox("Filter using another Variable (optional)",
                              [None] + list(df.columns), 
                              format_func=lambda x: "None" if x is None else x
                              )
    # Filter DataFrame even if no filter is selected
    df_filtered = df
    # Apply filter if a filter column is selected
    if filter_col is not None:
        # Check if the selected filter column is numerical or categorical
        # and apply the appropriate filter
        # If the filter column is numerical, use a slider
        if column_types[filter_col] == "numerical":
            min_val = float(df[filter_col].min())
            max_val = float(df[filter_col].max())
            range_val = st.slider("Chosse value range", min_val, max_val, (min_val, max_val))
            df_filtered = df[df[filter_col].between(*range_val)]
        # If the filter column is categorical, use a multiselect
        elif column_types[filter_col] == "categorical":
            options = sorted(df[filter_col].dropna().unique().tolist())
            selected = st.multiselect("Choose a category (multiple possible)", options, default=options)
            df_filtered = df[df[filter_col].isin(selected)]
    # num_df = df.select_dtypes(include="number")
    # Check if there are at least two numeric columns
    if len(numeric_cols) >= 2:
        # Check if at least two columns are selected
        if len(selected_cols) >= 2:
            st.subheader("📈 Correlation Matrix")
            # Only keep selected columns
            df_selected = df_filtered[selected_cols]
            # Calculate the correlation matrix
            corr = df_selected.corr()
            # Display the correlation matrix
            fig, ax = plt.subplots(figsize=(12, 10))

            # Optional: Maske für obere Dreieck-Hälfte
            mask = np.triu(np.ones_like(corr, dtype=bool))

            # Nur Werte > 0.5 oder < -0.5 beschriften
            sns.heatmap(
                corr,
                mask=mask,
                annot=True,
                fmt=".2f",
                cmap="coolwarm",
                center=0,
                linewidths=0.5,
                linecolor="white",
                annot_kws={"fontsize": 8},
                cbar_kws={"shrink": 0.75},
            )

            plt.xticks(rotation=45, ha='right', fontsize=9)
            plt.yticks(fontsize=9)
            st.pyplot(fig)
            # Save the figure to a BytesIO object for download
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight')
            buf.seek(0)
            # Download buttons for CSV and PNG
            st.download_button(label="Download Correlation Matrix as CSV", 
                               data=corr.to_csv(), 
                               file_name="correlation_matrix.csv", 
                               mime="text/csv")
            st.download_button(label="Download Correlation Graph as PNG", 
                               data=buf, 
                               file_name="correlation_graph.png", 
                               mime="image/png")
        # Warning if not enough columns are selected
        else:
            st.warning("Please select at least two columns for correlation analysis.")
    # Warning if not enough numeric columns are available
    else:
        st.warning("Not enough numeric columns for correlation analysis.")
    # Warning if no DataFrame is available
else:
    st.warning("Please upload a file to the homepage first.")


