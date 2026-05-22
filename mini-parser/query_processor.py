import json
import re

class ECommerceQueryProcessor:
    """
    A simple query processor for e-commerce product data.
    """
    def __init__(self, data_file):
        """
        Initializes the processor and loads the product data.

        Args:
            data_file (str): The path to the JSON data file.
        """
        self.products = self._load_data(data_file)
        if self.products:
            print(f"Successfully loaded {len(self.products)} products.")
        else:
            print("Could not load product data.")

    def _load_data(self, data_file):
        """Loads product data from a JSON file."""
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading data file: {e}")
            return []

    def _normalize_value(self, value):
        """
        Normalizes a value for comparison by converting to string,
        lowercasing, and stripping whitespace.
        """
        return str(value).lower().strip()
    
    def _parse_numeric(self, value):
        """
        Extracts the first numeric part of a string.
        Example: "390 g" -> 390.0
        """
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Use regex to find the first number (integer or float)
            match = re.search(r'[-+]?\d*\.\d+|\d+', value)
            if match:
                return float(match.group())
        return None

    def query(self, query_str):
        """
        Parses a query string and filters products.

        Supported formats:
        - key:value (for partial string match, case-insensitive)
        - key:"exact value" (for exact string match, case-insensitive)
        - key>value, key<value, key>=value, key<=value (for numeric comparison)
        
        Args:
            query_str (str): The query string.

        Returns:
            list: A list of products matching the query.
        """
        if not self.products:
            return []

        # Regex to parse the query string
        # Captures: 1=key, 2=operator, 3=quoted value, 4=unquoted value
        match = re.match(r'^\s*([\w\s]+?)\s*([:><=]+)\s*(?:"([^"]*)"|(\S+))\s*$', query_str)
        
        if not match:
            print("Invalid query format. Use: key:value, key>value, etc.")
            return []

        key, op, quoted_val, unquoted_val = match.groups()
        key = key.strip()
        value = quoted_val if quoted_val is not None else unquoted_val

        results = []

        for product in self.products:
            # Check if the key exists in the product (case-insensitive check)
            product_key = next((pk for pk in product if pk.lower() == key.lower()), None)
            
            if product_key and product[product_key] is not None:
                product_value = product[product_key]

                # Handle numeric comparisons
                if op in ('>', '<', '>=', '<='):
                    product_num = self._parse_numeric(product_value)
                    query_num = self._parse_numeric(value)
                    
                    if product_num is not None and query_num is not None:
                        if op == '>' and product_num > query_num: results.append(product)
                        elif op == '<' and product_num < query_num: results.append(product)
                        elif op == '>=' and product_num >= query_num: results.append(product)
                        elif op == '<=' and product_num <= query_num: results.append(product)
                
                # Handle string comparisons
                elif op == ':':
                    normalized_product_val = self._normalize_value(product_value)
                    normalized_query_val = self._normalize_value(value)
                    
                    # Exact match for quoted values
                    if quoted_val is not None:
                        if normalized_product_val == normalized_query_val:
                            results.append(product)
                    # Partial match for unquoted values
                    else:
                        if normalized_query_val in normalized_product_val:
                            results.append(product)
        return results

def main():
    """Main function to run the interactive query processor."""
    processor = ECommerceQueryProcessor('data-set.json')
    if not processor.products:
        return

    print("\n--- E-commerce Product Query Processor ---")
    print("Enter a query, or type 'exit' to quit.")
    print("Examples:")
    print("  - Color:Blue")
    print('  - Type:"Quilted Jacket"')
    print("  - Weight:<400")
    print("  - id:1")
    print("------------------------------------------")

    while True:
        query_str = input("query> ")
        if query_str.lower() == 'exit':
            break
        
        matches = processor.query(query_str)
        
        print(f"\nFound {len(matches)} matching products.")
        if not matches:
            print("------------------------------------------")

        for i, product in enumerate(matches):
            print(f"\n--- Result {i+1} ---")
            # Pretty print the product details
            for key, value in product.items():
                if value: # Only print keys with non-empty values
                    print(f"  {key}: {value}")
            if i == len(matches) - 1:
                print("------------------------------------------")


if __name__ == "__main__":
    main()
