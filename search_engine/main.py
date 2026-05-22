"""
Main Interface for Kintsugi E-commerce Search Engine
===================================================

This is the main entry point for the search engine. It provides both
a command-line interface and programmatic access to the search functionality.

Author: Search Engine Implementation
Date: 2025
"""

import sys
import json
import argparse
from typing import Dict, Any, List
from pathlib import Path

from search_engine import KintsugiSearchEngine


class SearchEngineCLI:
    """
    Command-line interface for the Kintsugi search engine.
    """
    
    def __init__(self, data_file: str):
        """
        Initialize the CLI.
        
        Args:
            data_file (str): Path to the data file
        """
        self.data_file = data_file
        self.search_engine = None
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """Initialize the search engine."""
        try:
            print("🔍 Initializing Kintsugi Search Engine...")
            self.search_engine = KintsugiSearchEngine(self.data_file)
            print("✅ Search engine initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing search engine: {e}")
            sys.exit(1)
    
    def interactive_search(self) -> None:
        """Start interactive search session."""
        print("\n" + "="*60)
        print("🌟 KINTSUGI E-COMMERCE SEARCH ENGINE 🌟")
        print("="*60)
        print("Welcome! This search engine treats 'imperfect' queries as valuable.")
        print("Even misspelled, partial, or broken queries can find beautiful results!")
        print("\nCommands:")
        print("  search <query>     - Search for products")
        print("  details <id>       - Show detailed product information")
        print("  suggest <partial>  - Get search suggestions")
        print("  field <name>       - Get field suggestions")
        print("  stats              - Show engine statistics")
        print("  config             - Show configuration")
        print("  help               - Show this help")
        print("  quit/exit          - Exit the program")
        print("="*60)
        
        while True:
            try:
                command = input("\n🔍 Enter command: ").strip()
                
                if not command:
                    continue
                
                parts = command.split(' ', 1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""
                
                if cmd in ['quit', 'exit', 'q']:
                    print("👋 Goodbye! Thanks for using Kintsugi Search Engine!")
                    break
                elif cmd == 'search':
                    self._handle_search(arg)
                elif cmd == 'details':
                    self._handle_product_details(arg)
                elif cmd == 'suggest':
                    self._handle_suggestions(arg)
                elif cmd == 'field':
                    self._handle_field_suggestions(arg)
                elif cmd == 'stats':
                    self._handle_stats()
                elif cmd == 'config':
                    self._handle_config()
                elif cmd == 'help':
                    self._show_help()
                else:
                    print(f"❌ Unknown command: {cmd}. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _handle_search(self, query: str) -> None:
        """Handle search command."""
        if not query:
            print("❌ Please provide a search query.")
            return
        
        print(f"\n🔍 Searching for: '{query}'")
        print("-" * 50)
        
        try:
            # Use the new formatted display method
            self.search_engine.search_and_display(query, max_results=15)
        
        except Exception as e:
            print(f"❌ Search error: {e}")
    
    def _handle_product_details(self, product_id: str) -> None:
        """Handle product details command."""
        if not product_id:
            print("❌ Please provide a product ID.")
            return
        
        try:
            # Use the search engine's method to get product details
            result = self.search_engine.get_product_details(product_id)
            
            if not result['success']:
                print(f"❌ {result['error']}")
                return
            
            product_data = result['product']
            
            print(f"\n📦 Product Details for ID: {product_id}")
            print("=" * 60)
            
            # Display basic info
            if product_data['basic_info']:
                print("\n🏷️  Basic Information:")
                for key, value in product_data['basic_info'].items():
                    print(f"   • {key}: {value}")
            
            # Display features
            if product_data['features']:
                print("\n✨ Features:")
                for key, value in product_data['features'].items():
                    print(f"   • {key}: {value}")
            
            # Display specifications
            if product_data['specifications']:
                print("\n🔧 Specifications:")
                for key, value in product_data['specifications'].items():
                    print(f"   • {key}: {value}")
            
            # Display Kintsugi notes
            if product_data['kintsugi_notes']:
                print("\n✨ Kintsugi Notes:")
                for note in product_data['kintsugi_notes']:
                    print(f"   {note}")
            
            # Display insights
            print("\n📊 Kintsugi Insights:")
            for insight in result['kintsugi_insights']:
                print(f"   {insight}")
            
            print("\n" + "=" * 60)
        
        except Exception as e:
            print(f"❌ Product details error: {e}")
    
    def _handle_suggestions(self, partial: str) -> None:
        """Handle suggestions command."""
        if not partial:
            print("❌ Please provide a partial query.")
            return
        
        try:
            suggestions = self.search_engine.get_search_suggestions(partial)
            
            if suggestions:
                print(f"\n💡 Suggestions for '{partial}':")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"   {i}. {suggestion}")
            else:
                print(f"😔 No suggestions found for '{partial}'")
        
        except Exception as e:
            print(f"❌ Suggestions error: {e}")
    
    def _handle_field_suggestions(self, field_name: str) -> None:
        """Handle field suggestions command."""
        if not field_name:
            print("❌ Please provide a field name.")
            return
        
        try:
            suggestions = self.search_engine.get_field_suggestions(field_name)
            
            if suggestions:
                print(f"\n📋 Values for field '{field_name}':")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"   {i}. {suggestion}")
            else:
                print(f"😔 No values found for field '{field_name}'")
        
        except Exception as e:
            print(f"❌ Field suggestions error: {e}")
    
    def _handle_stats(self) -> None:
        """Handle stats command."""
        try:
            stats = self.search_engine.get_stats()
            
            print("\n📊 Search Engine Statistics:")
            print("-" * 40)
            
            parser_stats = stats['parser_stats']
            print(f"📦 Total Products: {parser_stats['total_products']}")
            print(f"🏷️  Total Fields: {parser_stats['total_fields']}")
            
            index_stats = stats['index_stats']
            print(f"🔍 Indexed Terms: {index_stats['total_terms']}")
            print(f"📏 Avg Doc Length: {index_stats['average_doc_length']:.1f}")
            
            print(f"\n⚙️  Configuration:")
            config = stats['search_config']
            print(f"   Max Results: {config['max_results']}")
            print(f"   Fuzzy Threshold: {config['fuzzy_threshold']}")
            print(f"   Highlighting: {config['enable_highlighting']}")
        
        except Exception as e:
            print(f"❌ Stats error: {e}")
    
    def _handle_config(self) -> None:
        """Handle config command."""
        try:
            stats = self.search_engine.get_stats()
            config = stats['search_config']
            
            print("\n⚙️  Search Configuration:")
            print("-" * 30)
            for key, value in config.items():
                print(f"   {key}: {value}")
        
        except Exception as e:
            print(f"❌ Config error: {e}")
    
    def _show_help(self) -> None:
        """Show help information."""
        print("\n📖 Kintsugi Search Engine Help:")
        print("-" * 40)
        print("This search engine implements the Japanese art of Kintsugi,")
        print("treating 'imperfect' queries as valuable rather than discarding them.")
        print("\nSearch Types:")
        print("  • Exact: Perfect matches")
        print("  • Fuzzy: Approximate matches with typos")
        print("  • Combined: Both exact and fuzzy results")
        print("\nFeatures:")
        print("  • Handles misspellings gracefully")
        print("  • Highlights matches with Kintsugi symbols")
        print("  • Provides search suggestions")
        print("  • Shows field-specific suggestions")
        print("\nExamples:")
        print("  search iPhone 14")
        print("  search samsng galaxy  (misspelled)")
        print("  suggest headph")
        print("  field Brand")


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Kintsugi E-commerce Search Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --data data-set.json --interactive
  python main.py --data data-set.json --query "iPhone 14"
  python main.py --data data-set.json --query "samsng galaxy" --fuzzy
        """
    )
    
    parser.add_argument(
        '--data', '-d',
        required=True,
        help='Path to the JSON data file'
    )
    
    parser.add_argument(
        '--query', '-q',
        help='Search query (if not provided, starts interactive mode)'
    )
    
    parser.add_argument(
        '--fuzzy', '-f',
        action='store_true',
        help='Use fuzzy search mode'
    )
    
    parser.add_argument(
        '--max-results', '-m',
        type=int,
        default=10,
        help='Maximum number of results to return'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file for results (JSON format)'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Start interactive mode'
    )
    
    args = parser.parse_args()
    
    # Check if data file exists
    if not Path(args.data).exists():
        print(f"❌ Data file not found: {args.data}")
        sys.exit(1)
    
    # Initialize CLI
    cli = SearchEngineCLI(args.data)
    
    # Handle different modes
    if args.interactive or not args.query:
        # Interactive mode
        cli.interactive_search()
    else:
        # Command-line search mode
        try:
            search_type = "fuzzy" if args.fuzzy else "auto"
            
            # Use formatted display
            cli.search_engine.search_and_display(
                args.query, 
                search_type=search_type,
                max_results=args.max_results
            )
            
            # Save raw results to file if requested
            if args.output:
                results = cli.search_engine.search(
                    args.query, 
                    search_type=search_type,
                    max_results=args.max_results
                )
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Results saved to {args.output}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
