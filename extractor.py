import pandas as pd
from io import StringIO
import os

OUTPUT_DIR = "outputs"

def extract_tables(content):
    """
    Extracts tables from HTML content string.
    Returns a list of DataFrames.
    """
    try:
        if not content:
            print("No content provided to extractor.")
            return []
        
        # Check against Cloudflare or empty content before parsing
        if "Just a moment..." in content:
            print("Warning: Content appears to be a Cloudflare challenge page.")
        
        tables = pd.read_html(StringIO(content))
        
        if not tables:
            print("No tables found in the content.")
            return []
            
        print(f"Found {len(tables)} tables.")
        return tables
        
    except ValueError as e:
        print(f"No tables found (ValueError): {e}")
        return []
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return []

def save_tables(tables, filename_prefix):
    """
    Saves a list of DataFrames to an Excel file.
    """
    if not tables:
        print("No tables to save.")
        return None
        
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    output_filename = f"{filename_prefix}.xlsx"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for i, table in enumerate(tables):
                sheet_name = f"Table_{i+1}"
                
                # Flatten MultiIndex columns if present
                if isinstance(table.columns, pd.MultiIndex):
                    table.columns = [' '.join(col).strip() for col in table.columns.values]
                
                # Truncate sheet name to 31 chars (Excel limit)
                sheet_name = sheet_name[:31]
                
                table.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"Successfully saved {len(tables)} tables to {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error saving tables to Excel: {e}")
        return None
