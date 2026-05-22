import streamlit as st
import pandas as pd
import re
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="E-commerce Query Processor",
    page_icon="🛒",
    layout="wide",
)

# --- Data Loading ---
@st.cache_data
def load_cleaned_data(data_file):
    """Loads the pre-cleaned product data from a CSV file."""
    if not os.path.exists(data_file):
        st.error(f"Error: Cleaned data file '{data_file}' not found.")
        st.info("Please run the `explore_and_clean.py` script first to generate it.")
        return None
    try:
        df = pd.read_csv(data_file)
        return df
    except Exception as e:
        st.error(f"Error loading cleaned data file: {e}")
        return None

# --- Query Logic ---
def parse_numeric(value):
    """Extracts the first numeric part of a value."""
    if isinstance(value, (int, float)): return float(value)
    if isinstance(value, str):
        match = re.search(r'[-+]?\d*\.\d+|\d+', value)
        if match: return float(match.group())
    return None

def query_dataframe(df, query_str):
    """Parses a query and filters the DataFrame."""
    if not query_str.strip(): return df

    match = re.match(r'^\s*([\w\s]+?)\s*([:><=]+)\s*(?:"([^"]*)"|(\S+))\s*$', query_str)
    if not match:
        st.warning("Invalid query format. Please use 'key:value', 'key:\"value\"', or 'key>value'.")
        return pd.DataFrame()

    key, op, quoted_val, unquoted_val = match.groups()
    key, value = key.strip(), quoted_val if quoted_val is not None else unquoted_val
    
    target_column = next((col for col in df.columns if col.lower() == key.lower()), None)
    if not target_column:
        st.warning(f"Field '{key}' not found in the data.")
        return pd.DataFrame()

    filtered_df = df.dropna(subset=[target_column]).copy()

    if op in ('>', '<', '>=', '<='):
        query_num = parse_numeric(value)
        if query_num is None:
            st.warning(f"Could not parse numeric value from '{value}'.")
            return pd.DataFrame()
        
        numeric_series = filtered_df[target_column].apply(parse_numeric)
        valid_entries = numeric_series.notna()

        if op == '>': return filtered_df[valid_entries & (numeric_series > query_num)]
        if op == '<': return filtered_df[valid_entries & (numeric_series < query_num)]
        if op == '>=': return filtered_df[valid_entries & (numeric_series >= query_num)]
        if op == '<=': return filtered_df[valid_entries & (numeric_series <= query_num)]

    elif op == ':':
        str_series = filtered_df[target_column].astype(str).str.lower()
        query_val_lower = value.lower()

        if quoted_val is not None:
            return filtered_df[str_series == query_val_lower]
        else:
            return filtered_df[str_series.str.contains(query_val_lower, na=False)]
    
    return pd.DataFrame()

# --- Main Application UI ---
st.title("🛒 E-commerce Query Processor")
st.write("This tool queries the `cleaned_data.csv` file.")

df = load_cleaned_data('cleaned_data.csv')

if df is not None:
    # --- Sidebar for Instructions ---
    with st.sidebar:
        st.header("How to Query")
        st.markdown("""
        Use the search box to filter products. Supported formats:
        - `key:value` (Partial match)
        - `key:"exact value"` (Exact match)
        - `key>value` (Numeric comparison)
        """)
        st.divider()
        st.header("Available Fields")
        st.write(", ".join(f"`{col}`" for col in df.columns if col.strip()))

    # --- Main Content ---
    query_str = st.text_input(
        "Enter your query on the cleaned data",
        placeholder="e.g., Fabric:Denim or id:2",
        label_visibility="collapsed"
    )

    results_df = query_dataframe(df, query_str)
    
    st.metric("Products Found", len(results_df))

    # --- NEW: Improved Display Logic ---
    if results_df.empty and query_str:
        st.info("No products found matching your query.")
    elif results_df.empty and not query_str:
        st.info("Showing all products. Enter a query above to filter.")

    # Display each result in an expander for a cleaner look
    for index, row in results_df.iterrows():
        product_id = row.get('id', index)
        product_type = row.get('Type')

        # Gracefully handle missing 'Type' value for the title
        if pd.isna(product_type):
            expander_title = f"ID: {product_id}"
        else:
            expander_title = f"ID: {product_id} - {product_type}"

        with st.expander(expander_title):
            # Clean and display all product details inside the expander
            product_details = row.dropna().to_dict()
            st.json(product_details)
            
else:
    st.warning("Could not display data. Please ensure 'cleaned_data.csv' exists.")

