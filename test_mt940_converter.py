import os
import pandas as pd
from datetime import datetime
import re

def parse_amount(amount_str):
    """Parse amount from MT940 transaction line"""
    try:
        # First, find the debit/credit indicator and amount
        debit = 'D' in amount_str
        credit = 'C' in amount_str
        
        if not (debit or credit):
            return 0.0
            
        # Extract the numeric part using regex
        # Look for amount after D or C indicator, followed by N or F
        amount_match = re.search(r'[DC]N?(\d+,\d*|\d*\.\d*|\d+)', amount_str)
        if not amount_match:
            # Try alternative format where amount comes after reference
            amount_match = re.search(r'NONREF//.*?(\d+,\d*|\d*\.\d*|\d+)', amount_str)
        
        if amount_match:
            amount_str = amount_match.group(1)
            # Convert to float, handling both comma and dot as decimal separator
            amount = float(amount_str.replace(',', '.'))
            # Apply sign based on debit/credit
            if debit:
                amount = -amount  # Debit (outgoing) is negative
            else:
                amount = amount  # Credit (incoming) is positive
            return amount
            
        return 0.0
        
    except Exception as e:
        print(f"Warning: Error parsing amount from '{amount_str}': {str(e)}")
        return 0.0

def extract_currency(line):
    """Extract currency from balance field"""
    try:
        # Find the currency code using regex
        # Currency codes are always 3 uppercase letters
        match = re.search(r'[DC](\d{6})([A-Z]{3})', line)
        if match:
            return match.group(2)
    except Exception as e:
        print(f"Warning: Error extracting currency from '{line}': {str(e)}")
    return None

def parse_mt940(file_path):
    """Optimized MT940 parsing"""
    transactions = []
    current_transaction = None
    description = []
    currency = None
    
    # Pre-compile transaction markers
    transaction_start = ':61:'
    currency_markers = [':60F:', ':60M:', ':62F:', ':62M:']  # Various balance fields that contain currency
    description_start = ':86:'
    desc_markers = {'<00', '<20', '<21', '<22', '<23', '<27', '<28', '<29'}
    
    try:
        with open(file_path, 'r', encoding='iso-8859-1') as file:
            lines = file.readlines()
            
        print(f"\nTesting file: {os.path.basename(file_path)}")
        print("-" * 50)
        print("Parsing MT940 file...")
        print(f"Processing {len(lines)} lines...")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract currency from balance fields
            if not currency:  # Only try to find currency if we haven't found it yet
                for marker in currency_markers:
                    if line.startswith(marker):
                        found_currency = extract_currency(line)
                        if found_currency:
                            currency = found_currency
                            print(f"\nFound currency: {currency} in line: {line}")
                            break
            
            if line.startswith(transaction_start):
                if current_transaction:
                    current_transaction['Description'] = ' '.join(description)
                    transactions.append(current_transaction)
                    description = []
                
                # Parse transaction header
                try:
                    print(f"\nParsed transaction: {line}")
                    
                    # Extract date and reference
                    date_str = line[4:10]  # Date is always 6 characters after :61:
                    
                    # Parse amount and type (D/C)
                    amount_str = line[10:]  # Skip date part
                    amount = parse_amount(amount_str)
                    
                    # Get reference - handle both formats
                    ref = ''
                    if 'NTRFNONREF//' in line:
                        # PLN format - reference is after the second amount
                        parts = line.split('//')
                        if len(parts) > 1:
                            ref = parts[-1].strip()
                    elif 'NERRNONREF//' in line:
                        # USD format - reference is between // and next space
                        parts = line.split('//')
                        if len(parts) > 1:
                            ref = parts[1].split()[0].strip()
                    elif '//' in line:
                        # Generic format
                        ref = line.split('//')[-1].strip()
                    
                    current_transaction = {
                        'Date': datetime.strptime(date_str, '%y%m%d'),
                        'Amount': amount,
                        'Currency': currency or 'Unknown',
                        'Bank Reference': ref
                    }
                    
                    print(f"Amount: {amount}, Currency: {currency}")
                    
                except Exception as e:
                    print(f"Warning: Error parsing transaction line: {line}")
                    print(f"Error details: {str(e)}")
                    continue
            
            elif line.startswith(description_start):
                continue
            
            elif current_transaction:
                # Process description lines more efficiently
                if line.startswith('<'):
                    marker = line[:3]
                    if marker in desc_markers:
                        description.append(line[3:].strip())
                else:
                    description.append(line.strip())
        
        # Add the last transaction
        if current_transaction:
            current_transaction['Description'] = ' '.join(description)
            transactions.append(current_transaction)
        
        if not transactions:
            raise Exception("No transactions found in the file")
        
        print(f"\nFound {len(transactions)} transactions\n")
        
        # Print first few transactions for verification
        print("First few transactions:\n")
        for i, t in enumerate(transactions[:3], 1):
            print(f"Transaction {i}:")
            print(f"Date: {t['Date']}")
            print(f"Amount: {t['Amount']}")
            print(f"Currency: {t['Currency']}")
            print(f"Reference: {t['Bank Reference']}")
            print(f"Description: {t['Description'][:100]}...\n")
        
        print("Converting to CSV...")
        
        # Convert to DataFrame and save
        output_path = os.path.splitext(file_path)[0] + '_test.csv'
        df = pd.DataFrame(transactions)
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        df['Amount'] = pd.to_numeric(df['Amount']).round(2)
        df.to_csv(output_path, index=False)
        
        print(f"\nSaved to: {os.path.basename(output_path)}\n")
        
        # Print DataFrame summary
        print("DataFrame Summary:")
        print("-" * 50 + "\n")
        print(f"Shape: {df.shape}\n")
        print(f"Columns: {list(df.columns)}\n")
        print("Currency value counts:")
        print(df['Currency'].value_counts())
        print("\nAmount statistics:")
        print(df['Amount'].describe())
        print("\n")
        
        return transactions
        
    except Exception as e:
        raise Exception(f"Error parsing MT940 file: {str(e)}")

def test_mt940_file(file_path):
    """Test function to process an MT940 file"""
    try:
        transactions = parse_mt940(file_path)
        return transactions
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Find the first .sta file in the current directory
    sta_files = [f for f in os.listdir('.') if f.endswith('.sta')]
    if sta_files:
        test_mt940_file(sta_files[0])
    else:
        print("No .sta files found in current directory") 