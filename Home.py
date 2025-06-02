import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import re

def sanitize_column(col, i):
    if pd.isna(col) or str(col).strip() == "":
        return f"Unnamed_{i}"
    col = str(col).strip()
    col = re.sub(r"[^\w\s]", "_", col)  # Replaces special characters with underscores
    return col if col else f"Unnamed_{i}"

st.set_page_config(page_title="NoCodeExplorer", layout="wide")
st.title("📊 NoCodeExplorer – PODSV Project")
st.subheader("Introduction")
st.markdown("""
Welcome to **NoCodeExplorer**!  
This is a simple data exploration app that takes a dataset and lets you analyze and plot its numerical variables.  
Here on the homepage you can do the following steps:

- **Upload** your **CSV** or **Excel** data file on the sidebar  
- **Choose** the **header row** and **sheet name** (Excel) or the **delimiter** (CSV)  
- **Explore** your raw and cleaned data with a short little preview  
- **Download** the cleaned data as a CSV file for further analysis
- **Check** variable assignment **numerical** or **categorical**
- **Go to the other pages** on the sidebar to explore your data further 
- **Start over** by just clicking the **reset button** on the sidebar

You can use the sidebar to reset the app or navigate to other pages. And dont worry, you dont need to be a data scientist to use this app!  
We will guide you through the process of data exploration step by step and explain everything you need to know.  
With that in mind, have fun exploring your data!  
**Beware**: If you are trying to analyze a Excel file, please make sure that it is in the newest format (xlsx), older formats (xls) are not supported.
""")

# Session-Initialisierung
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None
if "selected_sheet" not in st.session_state:
    st.session_state["selected_sheet"] = None
if "header_row" not in st.session_state:
    st.session_state["header_row"] = 0
if "delimiter" not in st.session_state:
    st.session_state["delimiter"] = ","

# Datei-Upload (session-sicher)
file_uploader_key = st.session_state.get("file_uploader_key", "default")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"], key=file_uploader_key)

if uploaded_file is not None:
    st.session_state["uploaded_file"] = uploaded_file
else:
    uploaded_file = st.session_state["uploaded_file"]

# === STEP 1: Upload & Sheet Auswahl ===
if uploaded_file: # and "raw_df" not in st.session_state:
    sheet = None

    # --- Vorschau für Excel ---
    if uploaded_file.name.endswith(".xlsx"):
        xls = pd.ExcelFile(uploaded_file)

        # Sheet-Auswahl speichern
        if st.session_state["selected_sheet"] not in xls.sheet_names:
            st.session_state["selected_sheet"] = xls.sheet_names[0]

        st.session_state["selected_sheet"] = st.selectbox(
            "Choose the worksheet your data is in", 
            xls.sheet_names, 
            index=xls.sheet_names.index(st.session_state["selected_sheet"])
        )
        sheet = st.session_state["selected_sheet"]
        raw_df = pd.read_excel(xls, sheet_name=sheet, header=None)
        st.session_state["raw_df"] = raw_df
        
    elif uploaded_file.name.endswith(".csv"): # and "raw_df" not in st.session_state:
        # Gleiches Prinzip wie bei pd.ExcelFile, dadurch dass wir hier die Bytes des Uploads verwenden
        # und nicht den Upload selbst, kann die Datei immer wieder neu eingelesen werden, ist normalerweise
        # nicht möglich mit pd.read_csv(uploaded_file)
        file_bytes = uploaded_file.getvalue()
        st.session_state["csv_bytes"] = file_bytes
        # Select delimiter
        st.session_state["delimiter"] = st.selectbox(
            "Choose delimiter",
            [",", ";", "\t", "|"],
            index=[",", ";", "\t", "|"].index(st.session_state["delimiter"]),
            key="delimiter_select"
        )   
        delimiter = st.session_state["delimiter"]
        # max_header = len(raw_df) - 1
        # st.session_state["header_row"] = st.number_input(
        #     "Header Row (starting at 0)", 
        #     min_value=0, max_value=100, 
        #     value=st.session_state["header_row"], step=1
        # )
        # header_row = st.session_state["header_row"]
        raw_df = pd.read_csv(io.BytesIO(st.session_state["csv_bytes"]), delimiter=delimiter, header=0)
        # raw_df = pd.read_csv(uploaded_file, delimiter=delimiter, header=header_row)
        st.session_state["raw_df"] = raw_df
    # elif uploaded_file.name.endswith(".csv") and "raw_df" in st.session_state:
    #     raw_df = st.session_state["raw_df"]
    #     header_row = st.session_state["header_row"]
    else:
        st.error("❌ Invalid Datatype. Please Upload a CSV or Excel File.")

# if "raw_df" in st.session_state:
#     raw_df = st.session_state["raw_df"]
#     sheet = st.session_state["selected_sheet"]
    # === STEP 2: Vorschau der Rohdaten & Header-Zeile wählen ===
    if uploaded_file: # .name.endswith(".xlsx"):
        st.subheader("📄 Preview of raw data")
        st.dataframe(raw_df.head(30))
        max_header = len(raw_df) - 1
        st.session_state["header_row"] = st.number_input(
            "Header Row (starting at 0)", 
            min_value=0, max_value=max_header, 
            value=st.session_state["header_row"], step=1
        )
        header_row = st.session_state["header_row"]
        # Bedingung: Nur wenn die Header-Zeile geändert wird, dann auch die Typen zurücksetzen
        if "last_header_row" not in st.session_state:
            st.session_state["last_header_row"] = header_row
        if header_row != st.session_state["last_header_row"]:
            # Alte Typ-Auswahl-Widgets löschen, weil sich die Spalten geändert haben
            for key in list(st.session_state.keys()):
                if key.startswith("col_type_"):
                    del st.session_state[key]
            # Typen zurücksetzen
            if "column_types" in st.session_state:
                del st.session_state["column_types"]
            st.session_state["last_header_row"] = header_row
    # else:
    #     st.subheader("📄 Preview of raw data")
    #     st.dataframe(raw_df.head(30))
    

    # === STEP 3: Einlesen mit Header ===
    try:
        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(xls, sheet_name=sheet, header=header_row)
            # Cleaning Excel DataFrame
            df.columns = df.columns.map(str)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            df.dropna(how='all', inplace=True)
            df.dropna(how='all', axis=1, inplace=True)
        else:
            # raw_df = st.session_state["raw_df"]
            # df = raw_df.copy()
            df = pd.read_csv(io.BytesIO(st.session_state["csv_bytes"]), delimiter=delimiter, header=header_row)
            df.columns = [sanitize_column(col, i) for i, col in enumerate(df.columns)]
            # Cleaning CSV DataFrame
            df.dropna(how='all', axis=0, inplace=True)
            df.dropna(how='all', axis=1, inplace=True)
            
        # Speichern in Session
        st.session_state["df"] = df

        st.success(f"✅ File read successfully (Header Row: {header_row}, Sheet: {sheet if sheet else 'CSV'})")
        # === STEP 4: Bereinigte Datenvorschau ===
        st.subheader("📊 Preview cleaned data")
        st.markdown("#### 🧹 Cleaning Summary")
        st.table(pd.DataFrame({
            "Original rows": [raw_df.shape[0]],
            "Remaining rows": [df.shape[0]],
            "Remaining columns": [df.shape[1]],
            "Dropped rows": [raw_df.shape[0] - df.shape[0]],
            "Dropped columns": [raw_df.shape[1] - df.shape[1]]            
        }, index=["Summary"]))
        # Display cleaned DataFrame
        # st.write(df.shape[0], "rows and", df.shape[1], "columns")
        st.dataframe(df.head(30))
        st.download_button(label="Download cleaned data as CSV", 
                               data=df.to_csv(), 
                               file_name="clean_data.csv", 
                               mime="text/csv")

        # Optional: kleiner Plot
        # num_cols = df.select_dtypes(include="number").columns.tolist()
        # if len(num_cols) >= 2:
        #     x_col = st.selectbox("Wähle X-Achse", num_cols)
        #     y_col = st.selectbox("Wähle Y-Achse", num_cols, index=1)

        #     fig, ax = plt.subplots()
        #     ax.plot(df[x_col], label=x_col)
        #     ax.plot(df[y_col], label=y_col)
        #     ax.set_title(f"Plot von {x_col} und {y_col}")
        #     ax.set_xlabel("Index")
        #     ax.set_ylabel("Werte")
        #     ax.legend()
        #     st.pyplot(fig)
        # else:
        #     st.info("Nicht genügend numerische Spalten für Plot gefunden.")

        spalten_typen = {}

        st.subheader("🧠 Automatic column type detection (adjustable)")
        st.markdown("""  
NoCodeExplorer uses a self developed algorithm to detect the type of your variables (numerical or categorical).  
While it is broadly applicable and works well for most datasets, it is not perfect. So please make sure that the variables have been assigned correctly.  
You can adjust the type of your variables by selecting the desired type from the dropdown menu.  
At the end, you can see a **summary** of the assigned types.
                    
**Beware: The manual type changes will translate to the other pages of the app, but will reset if you return to the homepage.**
""")
        with st.expander("**ℹ️ What are numerical and categorical variables?**"):
            st.markdown("""
                - **Numerical variables** are measurable quantities represented by numbers.  
                 Examples:  
                 - Age (e.g., 23, 45, 67)  
                 - Temperature (e.g., 21.5°C, 36.7°C)  
                 - Income (e.g., 3200 CHF, 7800 CHF)  

                - **Categorical variables** represent groups, categories, or labels.  
                  Examples:  
                  - Gender (e.g., male, female, diverse)  
                  - Country (e.g., Switzerland, Germany, Italy)  
                  - Product category (e.g., electronics, clothing, food)

                If your data contains encoded categories (like 0 = male, 1 = female), make sure to manually adjust the type to categorical if it has not been detected as such.
""")
        # for col in df.columns:
        #     series = df[col]

        #     # Automatische Typ-Erkennung
        #     if pd.api.types.is_numeric_dtype(series) and series.nunique() > 15:
        #         detected_type = "numerical"
        #     else:
        #         detected_type = "categorical"

        #     # Anzeige als auswählbare Komponente
        #     selected_type = st.selectbox(
        #         f"Column '{col}' as:",
        #         options=["numerical", "categorical"],
        #         index=0 if detected_type == "numerical" else 1,
        #         key=f"col_type_{col}"
        #     )

        #     spalten_typen[col] = selected_type
        # st.session_state["column_types"] = spalten_typen
        if not any(f"col_type_{col}" in st.session_state for col in df.columns):
            # st.session_state["column_types"] = {}

            for col in df.columns:
                series = df[col]
    
                # Typ-Vorschlag
                if pd.api.types.is_numeric_dtype(series) and series.nunique() > 10:
                    detected_type = "numerical"
                else:
                    detected_type = "categorical"

                # Standardwert beim ersten Auftauchen setzen
                if f"col_type_{col}" not in st.session_state:
                    st.session_state[f"col_type_{col}"] = detected_type
            
            st.session_state["column_types"] = {
                col: st.session_state[f"col_type_{col}"] for col in df.columns
            }

        for col in df.columns:
            selected_type = st.selectbox(
                f"Column '{col}' as:",
                options=["numerical", "categorical"],
                index=0 if st.session_state[f"col_type_{col}"] == "numerical" else 1,
                key=f"col_type_{col}"
            )

            # Speichern aktuelle Auswahl
            # st.session_state["column_types"][col] = selected_type
        st.session_state["column_types"] = {
            col: st.session_state[f"col_type_{col}"] for col in df.columns
        }


        # Optional: Als Tabelle anzeigen oder speichern
        # st.write("📋 Aktuelle Auswahl:")
        # st.write(spalten_typen)
        column_types = st.session_state["column_types"]
        st.markdown("#### 🧠 Assigned Variable Types")
        types_df = pd.DataFrame(list(column_types.items()), columns=["Column", "Type"])
        types_df.index = [""] * len(types_df)  # Index ausblenden
        st.dataframe(types_df.set_index("Column"))

    except Exception as e:
        st.error(f"❌ Error reading the file: {e}")
else:
    st.info("Please upload a file to start.")

# st.sidebar.page_link("Univariate.py", label="Univariate Analysis", icon="📏")
# st.sidebar.page_link("Scatterplot.py", label="Scatterplot", icon="📈")
# st.sidebar.page_link("Correlation.py", label="Correlation Analysis", icon="🧮")

# === OPTIONAL: Zurücksetzen-Button ===
if st.sidebar.button("🔄 Reset"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # Datei-Upload-Widget neu initialisieren (zwingt Streamlit zur Neuerstellung)
    st.session_state["file_uploader_key"] = str(pd.Timestamp.now().timestamp())
    st.rerun()


