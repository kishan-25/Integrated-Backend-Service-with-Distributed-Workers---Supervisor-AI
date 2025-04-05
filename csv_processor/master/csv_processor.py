# master/csv_processor.py
import csv
import io

def parse_csv(csv_content):
    """
    Parse CSV content into a list of dictionaries.
    
    Args:
        csv_content (str): CSV content as a string
        
    Returns:
        list: List of dictionaries, where each dictionary represents a row in the CSV
    """
    try:
        # Create a file-like object from the CSV string
        csv_file = io.StringIO(csv_content)
        
        # Parse the CSV file
        reader = csv.DictReader(csv_file)
        
        # Convert to list of dictionaries
        rows = [row for row in reader]
        
        # Validate the CSV data (basic validation)
        if not rows:
            raise ValueError("CSV contains no data")
            
        return rows
    except Exception as e:
        raise ValueError(f"Error parsing CSV: {str(e)}")

def validate_csv(data, required_columns=None):
    """
    Validate CSV data against required columns.
    
    Args:
        data (list): List of dictionaries representing CSV data
        required_columns (list): List of required column names
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not data:
        return False
        
    if required_columns:
        # Check if all required columns exist in the first row
        first_row = data[0]
        for column in required_columns:
            if column not in first_row:
                return False
                
    return True