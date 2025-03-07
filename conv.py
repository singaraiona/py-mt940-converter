import pandas as pd
from datetime import datetime

def clean_description(desc):
    # Remove special characters and clean up the description
    desc = desc.replace('<', ' ').replace('>', ' ')
    # Remove multiple spaces
    desc = ' '.join(desc.split())
    return desc

def parse_amount(amount_str):
    try:
        # The amount format is like "2502280228DN20,00" where:
        # - First 6 digits are the date
        # - Next 4 digits are the transaction code
        # - D/C indicates debit/credit
        # - N is a separator
        # - The actual amount follows
        # Extract the amount part after the N
        parts = amount_str.split('N')
        if len(parts) < 2:
            return 0.0
        amount_part = parts[1].split('N')[0]  # Get the amount part before the next N
        # Convert comma to decimal point
        amount_part = amount_part.replace(',', '.')
        return float(amount_part)
    except (ValueError, IndexError):
        print(f"Error parsing amount: {amount_str}")  # Debug print
        return 0.0

def parse_mt940(file_path):
    transactions = []
    
    with open(file_path, 'r', encoding='iso-8859-1') as file:
        lines = file.readlines()
        
    current_transaction = None
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith(':61:'):
            # Parse transaction details
            parts = line[4:].split('N')
            date_str = parts[0][:6]  # Format: YYMMDD
            
            # Handle both debit (D) and credit (C) transactions
            amount_str = line[4:]  # Get the full string including the amount
            print(f"Processing amount string: {amount_str}")  # Debug print
            
            if 'D' in amount_str:
                amount = parse_amount(amount_str)
            elif 'C' in amount_str:
                amount = -parse_amount(amount_str)
            else:
                continue
            
            # Convert date
            date = datetime.strptime(date_str, '%y%m%d')
            
            # Get description from next lines
            description = []
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if not next_line or next_line.startswith(':61:'):
                    break
                if next_line.startswith(':86:'):
                    j += 1
                    while j < len(lines):
                        desc_line = lines[j].strip()
                        if not desc_line or desc_line.startswith(':61:'):
                            break
                        if desc_line.startswith('<'):
                            # Extract the actual description part
                            if desc_line.startswith('<00'):
                                description.append(desc_line[3:])  # Transaction type
                            elif desc_line.startswith('<20'):
                                description.append(desc_line[3:])
                            elif desc_line.startswith('<21'):
                                description.append(desc_line[3:])
                            elif desc_line.startswith('<22'):
                                description.append(desc_line[3:])
                            elif desc_line.startswith('<23'):
                                description.append(desc_line[3:])
                            elif desc_line.startswith('<27'):
                                description.append(desc_line[3:])  # Counterparty name
                            elif desc_line.startswith('<28'):
                                description.append(desc_line[3:])  # Additional details
                            elif desc_line.startswith('<29'):
                                description.append(desc_line[3:])  # Additional details
                        j += 1
                    break  # Exit after processing the :86: section
                else:
                    # Add the transaction type from the line after :61:
                    description.append(next_line)
                j += 1
            
            current_transaction = {
                'Date': date,
                'Amount': amount,
                'Currency': 'PLN',  # Based on the file content
                'Bank Reference': parts[0].split('//')[-1] if '//' in parts[0] else '',
                'Description': clean_description(' '.join(description))
            }
            transactions.append(current_transaction)
    
    return transactions

# Parse the MT940 file
transactions = parse_mt940('f.mt940')

# Convert to DataFrame
df = pd.DataFrame(transactions)

# Format the date column
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

# Format the amount column with 2 decimal places
df['Amount'] = df['Amount'].round(2)

# Save as CSV
df.to_csv("output.csv", index=False)

print(f"CSV file created successfully with {len(transactions)} transactions!")
