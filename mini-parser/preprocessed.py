import pandas as pd
import json

def explore_and_clean_data(input_filepath, output_filepath):
    """
    Loads raw e-commerce data, performs exploration and cleaning,
    prints a report, and saves the cleaned data.
    """
    print("--- Starting Data Exploration and Cleaning Process ---")

    # 1. Load the data
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        print(f"\n✅ Successfully loaded {len(df)} records from '{input_filepath}'.")
    except Exception as e:
        print(f"\n❌ Error loading data: {e}")
        return

    # --- Initial Exploration ---
    print("\n--- 1. Basic Exploration of Raw Data ---")
    
    print("\n[a] First 5 rows (.head()):")
    print(df.head())
    
    print("\n[b] Data types and non-null counts (.info()):")
    df.info()
    
    print("\n[c] Descriptive statistics (.describe()):")
    # Using .fillna to make the output cleaner for mixed types
    print(df.describe(include='all').fillna("N/A"))

    # --- Data Cleaning ---
    print("\n--- 2. Identifying and Cleaning Data Quality Issues ---")
    
    # [Issue 1] Check for and remove columns with empty names (like "")
    if "" in df.columns:
        print("\n[a] Found a column with an empty string as its name. Removing it.")
        df = df.drop(columns=[""])
    else:
        print("\n[a] No columns with empty names found.")

    # [Issue 2] Check for duplicates
    duplicate_count = df.duplicated().sum()
    print(f"\n[b] Found {duplicate_count} duplicate rows.")
    if duplicate_count > 0:
        df = df.drop_duplicates()
        print(f"   Action: Removed {duplicate_count} duplicates. New row count: {len(df)}.")
    
    # [Issue 3] Check for missing values
    print("\n[c] Analyzing missing values (NaNs)...")
    missing_values = df.isnull().sum()
    missing_df = missing_values[missing_values > 0].sort_values(ascending=False)
    if not missing_df.empty:
        print("   Columns with missing values:")
        print(missing_df)
        # For this dataset, we will keep NaNs as they signify features a product doesn't have.
        # In other scenarios, one might use df.dropna() or df.fillna().
        print("   Action: Keeping missing values for now, as they represent product-specific attributes.")
    else:
        print("   No missing values found.")

    # [Issue 4] Trim whitespace from object/string columns
    print("\n[d] Trimming leading/trailing whitespace from text columns.")
    str_cols = df.select_dtypes(include=['object']).columns
    for col in str_cols:
        df[col] = df[col].str.strip()
    print("   Action: Whitespace trimming complete.")

    # --- Final Verification ---
    print("\n--- 3. Verifying Cleaned Data ---")
    print("\nFinal data info after cleaning:")
    df.info()
    
    # --- Save Cleaned Data ---
    try:
        df.to_csv(output_filepath, index=False)
        print(f"\n✅ Successfully saved cleaned data to '{output_filepath}'.")
    except Exception as e:
        print(f"\n❌ Error saving cleaned data: {e}")
        
    print("\n--- Process Complete ---")


if __name__ == "__main__":
    # Define file paths
    raw_data_file = 'data-set.json'
    cleaned_data_file = 'cleaned_data.csv'
    
    # Run the main function
    explore_and_clean_data(raw_data_file, cleaned_data_file)
