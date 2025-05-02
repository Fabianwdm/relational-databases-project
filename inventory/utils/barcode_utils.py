import re
import os
import csv
from datetime import datetime

def validate_barcode(barcode):
    """
    Validates barcode format.
    Supports common formats like:
    - UPC-A (12 digits)
    - EAN-13 (13 digits)
    - CODE-128 (variable length alphanumeric)
    - Custom format (BCD-XXXXXX)
    
    Returns:
    - (True, None) if valid
    - (False, error_message) if invalid
    """
    # If empty
    if not barcode:
        return False, "Barcode cannot be empty"
    
    # Check for custom format BCD-XXXXXX
    if re.match(r'^BCD-\d{6}$', barcode):
        return True, None
    
    # Check for UPC-A (12 digits)
    if re.match(r'^\d{12}$', barcode):
        return True, None
    
    # Check for EAN-13 (13 digits)
    if re.match(r'^\d{13}$', barcode):
        return True, None
    
    # Check for CODE-128 (alphanumeric)
    if re.match(r'^[A-Za-z0-9-_]{4,}$', barcode):
        return True, None
    
    return False, "Invalid barcode format"

def process_barcode_input(input_string):
    """
    Process barcode input which might contain extra characters from scanner
    Often barcode scanners add prefix/suffix characters or special keys
    
    Returns cleaned barcode string
    """
    # Strip whitespace
    input_string = input_string.strip()
    
    # Remove common scanner prefixes/suffixes
    # For example, some scanners add carriage return or tab characters
    input_string = input_string.replace('\r', '').replace('\n', '').replace('\t', '')
    
    # Remove any other non-alphanumeric characters except dash
    input_string = re.sub(r'[^A-Za-z0-9\-]', '', input_string)
    
    return input_string

def import_barcodes_from_csv(csv_path):
    """
    Import multiple barcodes from a CSV file
    Expected format: barcode,quantity
    
    Returns:
    - List of (barcode, quantity) tuples
    - Error message if file can't be processed
    """
    if not os.path.exists(csv_path):
        return None, f"File not found: {csv_path}"
    
    try:
        barcodes = []
        with open(csv_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            
            # Check for header row
            first_row = next(reader, None)
            if not first_row:
                return None, "CSV file is empty"
            
            # Determine if first row is header or data
            is_header = False
            if first_row and len(first_row) >= 2:
                if first_row[0].lower() in ['barcode', 'code', 'sku'] and \
                   first_row[1].lower() in ['quantity', 'qty', 'amount', 'count']:
                    is_header = True
            
            # Process first row if it's data
            if not is_header and first_row:
                try:
                    if len(first_row) >= 2:
                        barcode = process_barcode_input(first_row[0])
                        quantity = float(first_row[1])
                        valid, _ = validate_barcode(barcode)
                        if valid:
                            barcodes.append((barcode, quantity))
                except ValueError:
                    pass
            
            # Process rest of rows
            for row in reader:
                if len(row) >= 2:
                    try:
                        barcode = process_barcode_input(row[0])
                        quantity = float(row[1])
                        valid, _ = validate_barcode(barcode)
                        if valid:
                            barcodes.append((barcode, quantity))
                    except ValueError:
                        continue
        
        if not barcodes:
            return None, "No valid barcode entries found in CSV"
            
        return barcodes, None
    
    except Exception as e:
        return None, f"Error processing CSV: {str(e)}"

def export_barcodes_to_csv(barcodes, csv_path):
    """
    Export barcodes to a CSV file
    
    barcodes: List of (barcode, product_name, quantity) tuples
    csv_path: Path to save the CSV file
    
    Returns:
    - True if successful
    - False if an error occurred
    """
    try:
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Barcode', 'Product', 'Quantity', 'Export Date'])
            
            # Write data
            for barcode, product_name, quantity in barcodes:
                writer.writerow([
                    barcode,
                    product_name,
                    quantity,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ])
                
        return True
    
    except Exception:
        return False

def read_barcode_from_scanner(prompt="Scan barcode: "):
    """
    Read barcode input from scanner or manual entry
    
    Since barcode scanners usually act as keyboard input devices,
    this function simply reads from standard input but adds some
    processing to handle scanner-specific behavior.
    
    Returns:
    - Processed barcode string
    """
    try:
        user_input = input(prompt)
        return process_barcode_input(user_input)
    except KeyboardInterrupt:
        print("\nInput cancelled")
        return None

def batch_scan_mode():
    """
    Enter batch scanning mode to process multiple barcodes
    
    Returns:
    - List of (barcode, quantity) tuples
    """
    print("\n=== Batch Scanning Mode ===")
    print("Enter barcodes followed by quantities.")
    print("Leave barcode empty to finish.")
    
    barcodes = []
    
    while True:
        barcode = read_barcode_from_scanner("Scan barcode (or press Enter to finish): ")
        
        if not barcode:
            break
            
        valid, error = validate_barcode(barcode)
        if not valid:
            print(f"Invalid barcode: {error}")
            continue
            
        try:
            quantity = float(input("Quantity: "))
            if quantity <= 0:
                print("Quantity must be greater than zero")
                continue
                
            barcodes.append((barcode, quantity))
            print(f"Added: {barcode}, Qty: {quantity}")
            
        except ValueError:
            print("Invalid quantity, must be a number")
            continue
    
    print(f"\nBatch complete. {len(barcodes)} items processed.")
    return barcodes