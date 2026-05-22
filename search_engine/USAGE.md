# 🎨 Kintsugi Search Engine - Usage Guide

## 🌟 What is Kintsugi Search Engine?

The Kintsugi Search Engine implements the Japanese art of **Kintsugi** - treating "imperfect" or broken queries as valuable rather than discarding them. Just like how broken pottery is repaired with gold to make it more beautiful, this search engine finds value in misspelled, partial, or incomplete queries.

## 🚀 Quick Start

### 1. Command Line Interface

#### Interactive Mode (Recommended)
```bash
cd search_engine
python main.py --data ../data-set.json --interactive
```

#### Single Search
```bash
# Exact search
python main.py --data ../data-set.json --query "iPhone 14"

# Fuzzy search (handles misspellings)
python main.py --data ../data-set.json --query "samsng galaxy" --fuzzy

# Save results to file
python main.py --data ../data-set.json --query "laptop" --output results.json
```

### 2. Web Interface

#### Start the Web UI
```bash
cd search_engine
python start_web.py
```

Then open your browser and go to: **http://localhost:5000**

#### Features of Web UI:
- 🔍 Real-time search with suggestions
- 🎨 Beautiful Kintsugi-inspired design
- 📱 Mobile-friendly responsive interface
- ⚡ Fast search with live results
- 🌟 Visual highlighting of matches

### 3. Programmatic Usage

```python
from search_engine import KintsugiSearchEngine

# Initialize engine
engine = KintsugiSearchEngine('data-set.json')

# Search for products
results = engine.search("iPhone 14 Pro Max")

# Access results
for result in results['results']:
    print(f"Score: {result['score']}")
    print(f"Product: {result['document']}")
    print(f"Kintsugi Quality: {result['kintsugi_quality']}")
```

## 🎨 Kintsugi Quality Levels

The search engine categorizes matches using Kintsugi-inspired quality levels:

- **✨ Perfect** - Exact matches, no repair needed
- **🌟 Excellent** - Near-perfect matches with minor variations  
- **⭐ Good** - Strong fuzzy matches with some differences
- **💫 Fair** - Partial matches that still provide value
- **✨ Poor** - Weak matches that require more "repair"

## 🔍 Search Types

### 1. Auto Search (Default)
- Automatically determines the best search strategy
- Combines exact and fuzzy matching
- Recommended for most use cases

### 2. Exact Search
- Perfect string matching
- Case-insensitive
- Handles quoted phrases
- Use when you want precise matches

### 3. Fuzzy Search
- Approximate matching with typos
- Phonetic matching
- Abbreviation expansion
- Character sequence matching
- Use when you expect misspellings

## 🎯 Interactive Commands

When using interactive mode, you can use these commands:

| Command | Description | Example |
|---------|-------------|---------|
| `search <query>` | Search for products | `search iPhone 14` |
| `suggest <partial>` | Get search suggestions | `suggest headph` |
| `field <name>` | Get field suggestions | `field Brand` |
| `stats` | Show engine statistics | `stats` |
| `config` | Show configuration | `config` |
| `help` | Show help information | `help` |
| `quit` | Exit the program | `quit` |

## 🌟 Example Searches

### Perfect Matches
```bash
search "iPhone 14 Pro Max"
search "Samsung Galaxy S23"
search "Sony WH-1000XM4"
```

### Kintsugi Magic (Misspellings)
```bash
search "samsng galaxy"      # Finds Samsung Galaxy
search "iphne 14"           # Finds iPhone 14
search "noise cancling"     # Finds noise cancelling
search "blutooth hedphones" # Finds bluetooth headphones
```

### Partial Queries
```bash
search "laptop i7"          # Finds laptops with Intel i7
search "wireless headphones" # Finds wireless audio devices
search "gaming mouse"        # Finds gaming peripherals
```

## 📊 Understanding Results

### Result Information
- **Score**: Relevance score (higher = more relevant)
- **Type**: Match type (exact, kintsugi_exact, kintsugi_fuzzy, etc.)
- **Quality**: Kintsugi quality level
- **Document**: Full product information
- **Highlighted Text**: Search preview with highlighting

### Kintsugi Insights
The engine provides insights about your search:
- "Found perfect matches - no repair needed!"
- "Found 5 Kintsugi matches - imperfect queries reveal hidden treasures!"
- "High-quality matches found - the golden seams are strong!"

## ⚙️ Configuration

You can customize the search behavior:

```python
# Update search configuration
engine.update_config(
    fuzzy_threshold=0.7,    # Lower = more fuzzy matches
    max_results=50,         # Maximum results to return
    enable_highlighting=True # Enable result highlighting
)
```

## 🔧 Advanced Features

### Field-Specific Search
```python
# Get suggestions for specific fields
brands = engine.get_field_suggestions('Brand')
colors = engine.get_field_suggestions('Color')
```

### Search Suggestions
```python
# Get search suggestions
suggestions = engine.get_search_suggestions('headph')
```

### Statistics
```python
# Get engine statistics
stats = engine.get_stats()
print(f"Total products: {stats['parser_stats']['total_products']}")
print(f"Indexed terms: {stats['index_stats']['total_terms']}")
```

## 🎨 Web UI Features

### Search Interface
- **Real-time suggestions** as you type
- **Search type selector** (Auto/Exact/Fuzzy)
- **Responsive design** for mobile and desktop
- **Beautiful animations** and transitions

### Results Display
- **Kintsugi symbols** for match quality
- **Highlighted text** showing matches
- **Product details** in organized format
- **Search insights** explaining results

### Performance
- **Fast search** with sub-second response times
- **Efficient indexing** for large datasets
- **Cached results** for better performance

## 🚀 Performance Tips

1. **Use exact search** when you know the exact terms
2. **Use fuzzy search** when you expect typos
3. **Use auto search** for general queries
4. **Limit results** with `max_results` parameter
5. **Use field suggestions** for better queries

## 🐛 Troubleshooting

### Common Issues

1. **"Data file not found"**
   - Make sure `data-set.json` is in the parent directory
   - Check the file path in your command

2. **"No results found"**
   - Try different search terms
   - Use fuzzy search for misspellings
   - Check if the product exists in the dataset

3. **"Search error"**
   - Check your internet connection (for web UI)
   - Restart the application
   - Check the console for error messages

### Getting Help

- Check the console output for error messages
- Use the `help` command in interactive mode
- Check the README.md for more information
- Review the code comments for technical details

## 🎉 Enjoy Your Kintsugi Search Experience!

Remember: In the art of Kintsugi, broken pottery is repaired with gold, making it more beautiful than before. This search engine applies the same philosophy to search - treating imperfect queries as opportunities to create something more valuable.

Happy searching! 🌟✨
