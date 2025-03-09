import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import pandas as pd
from datetime import datetime
import os
import re

class MT940Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("MT940 Statement Viewer")
        self.root.geometry("1000x600")
        
        # Initialize file path
        self.loaded_file_path = None
        
        # Configure style
        self.root.configure(bg='#f0f0f0')
        
        # Create main frame
        main_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Title - using system font
        title_label = tk.Label(
            main_frame,
            text="MT940 Statement Viewer",
            font=('system', 16, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = """
        This tool displays MT940 bank statement files (.sta) in a table format.
        
        Steps:
        1. Click 'Load File' to choose your .sta file
        2. Click 'Show' to display the transactions
        3. Use the table below to view and analyze your transactions
        """
        
        instructions_label = tk.Label(
            main_frame,
            text=instructions,
            font=('system', 10),
            bg='#f0f0f0',
            justify='left'
        )
        instructions_label.pack(pady=(0, 20))
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        # Load button
        self.load_button = tk.Button(
            button_frame,
            text="Load .sta File",
            command=self.load_file,
            font=('system', 12),
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=10
        )
        self.load_button.pack(side='left', padx=10)
        
        # Show button (initially disabled)
        self.show_button = tk.Button(
            button_frame,
            text="Show Transactions",
            command=self.show_transactions,
            font=('system', 12),
            bg='#2196F3',
            fg='white',
            padx=20,
            pady=10,
            state='disabled'
        )
        self.show_button.pack(side='left', padx=10)

        # Convert button (initially disabled)
        self.convert_button = tk.Button(
            button_frame,
            text="Convert to CSV",
            command=self.convert_file,
            font=('system', 12),
            bg='#FF9800',
            fg='white',
            padx=20,
            pady=10,
            state='disabled'
        )
        self.convert_button.pack(side='left', padx=10)
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="",
            font=('system', 10),
            bg='#f0f0f0',
            wraplength=500
        )
        self.status_label.pack(pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = tk.ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill='x', pady=10)
        
        # Create Treeview for transactions
        self.tree_frame = tk.Frame(main_frame)
        self.tree_frame.pack(expand=True, fill='both')
        
        # Create scrollbars
        y_scrollbar = ttk.Scrollbar(self.tree_frame)
        y_scrollbar.pack(side='right', fill='y')
        
        x_scrollbar = ttk.Scrollbar(self.tree_frame, orient='horizontal')
        x_scrollbar.pack(side='bottom', fill='x')
        
        # Create Treeview
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=('Date', 'Amount', 'Currency', 'Bank Reference', 'Description'),
            show='headings',
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        
        # Configure scrollbars
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        
        # Configure column headings
        self.tree.heading('Date', text='Date')
        self.tree.heading('Amount', text='Amount')
        self.tree.heading('Currency', text='Currency')
        self.tree.heading('Bank Reference', text='Bank Reference')
        self.tree.heading('Description', text='Description')
        
        # Configure column widths
        self.tree.column('Date', width=100)
        self.tree.column('Amount', width=100)
        self.tree.column('Currency', width=80)
        self.tree.column('Bank Reference', width=150)
        self.tree.column('Description', width=400)
        
        self.tree.pack(expand=True, fill='both')
        
        # Summary frame
        self.summary_frame = tk.Frame(main_frame, bg='#f0f0f0')
        self.summary_frame.pack(fill='x', pady=10)
        
        # Summary labels
        self.total_label = tk.Label(
            self.summary_frame,
            text="",
            font=('system', 10, 'bold'),
            bg='#f0f0f0'
        )
        self.total_label.pack(side='left', padx=10)
        
        # Version info
        version_label = tk.Label(
            main_frame,
            text="Version 2.0",
            font=('system', 8),
            bg='#f0f0f0'
        )
        version_label.pack(side='bottom', pady=(20, 0))

    def update_ui(self, message, progress):
        """Helper method to update UI and ensure updates are processed"""
        try:
            self.status_label.configure(text=message)
            self.progress_var.set(progress)
            self.root.update_idletasks()
            self.root.after(10)
            self.root.update()
        except Exception as e:
            print(f"Warning: Error updating UI: {str(e)}")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select MT940 File",
            filetypes=[("STA files", "*.sta"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Reset UI state
                self.update_ui("", 0)
                self.tree.delete(*self.tree.get_children())
                self.total_label.config(text="")
                
                # Verify file exists and is readable
                if not os.path.exists(file_path):
                    raise Exception("Selected file does not exist")
                    
                # Set new file and update UI
                self.loaded_file_path = file_path
                self.update_ui(f"File loaded: {os.path.basename(file_path)}", 25)
                
                # Enable both buttons
                self.show_button.configure(state='normal')
                self.convert_button.configure(state='normal')
                self.root.update_idletasks()
                
            except Exception as e:
                self.update_ui(f"Error loading file: {str(e)}", 0)
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                self.show_button.configure(state='disabled')
                self.convert_button.configure(state='disabled')
                self.loaded_file_path = None

    def show_transactions(self):
        if not self.loaded_file_path:
            messagebox.showerror("Error", "Please load a file first")
            return
            
        try:
            self.update_ui("Reading file...", 10)
            
            # Clear existing items
            self.tree.delete(*self.tree.get_children())
            
            # Parse the file
            transactions = self.parse_mt940(self.loaded_file_path)
            
            self.update_ui("Displaying transactions...", 75)
            
            # Add transactions to treeview
            total_amount = 0
            currency = None
            
            for trans in transactions:
                # Format date
                date_str = trans['Date'].strftime('%Y-%m-%d')
                
                # Format amount
                amount = round(trans['Amount'], 2)
                total_amount += amount
                
                # Get currency
                if not currency:
                    currency = trans['Currency']
                
                # Insert into treeview
                self.tree.insert('', 'end', values=(
                    date_str,
                    f"{amount:,.2f}",
                    trans['Currency'],
                    trans['Bank Reference'],
                    trans['Description']
                ))
            
            # Update summary
            self.total_label.config(
                text=f"Total Transactions: {len(transactions)} | Total Amount: {total_amount:,.2f} {currency}"
            )
            
            self.update_ui(
                f"Successfully displayed {len(transactions)} transactions.",
                100
            )
            
        except Exception as e:
            self.update_ui(f"Error: {str(e)}", 0)
            messagebox.showerror("Error", f"Failed to display transactions: {str(e)}")
            self.show_button.config(state='disabled')

    def convert_file(self):
        """Convert the loaded file to CSV"""
        if not self.loaded_file_path:
            messagebox.showerror("Error", "Please load a file first")
            return
            
        try:
            self.update_ui("Reading file...", 10)
            
            # Parse the file
            transactions = self.parse_mt940(self.loaded_file_path)
            
            self.update_ui("Creating CSV file...", 75)
            
            # Create output filename
            output_path = os.path.splitext(self.loaded_file_path)[0] + '.csv'
            
            # Convert to DataFrame and save
            df = pd.DataFrame(transactions)
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
            df['Amount'] = pd.to_numeric(df['Amount']).round(2)
            df.to_csv(output_path, index=False)
            
            self.update_ui(
                f"Success! Converted {len(transactions)} transactions.\nOutput saved to: {os.path.basename(output_path)}",
                100
            )
            messagebox.showinfo("Success", f"File converted successfully!\nSaved to: {os.path.basename(output_path)}")
            
        except Exception as e:
            self.update_ui(f"Error: {str(e)}", 0)
            messagebox.showerror("Error", f"Failed to convert file: {str(e)}")

    def extract_currency(self, line):
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

    def parse_amount(self, amount_str):
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

    def parse_mt940(self, file_path):
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
                
            total_lines = len(lines)
            for i, line in enumerate(lines):
                # Update progress every 100 lines
                if i % 100 == 0:
                    self.update_ui(f"Processing line {i}/{total_lines}...", 10 + (i/total_lines * 65))
                
                line = line.strip()
                if not line:
                    continue
                
                # Extract currency from balance fields
                if not currency:  # Only try to find currency if we haven't found it yet
                    for marker in currency_markers:
                        if line.startswith(marker):
                            found_currency = self.extract_currency(line)
                            if found_currency:
                                currency = found_currency
                                break
                
                if line.startswith(transaction_start):
                    if current_transaction:
                        current_transaction['Description'] = ' '.join(description)
                        transactions.append(current_transaction)
                        description = []
                    
                    # Parse transaction header
                    try:
                        # Extract date and reference
                        date_str = line[4:10]  # Date is always 6 characters after :61:
                        
                        # Parse amount and type (D/C)
                        amount_str = line[10:]  # Skip date part
                        amount = self.parse_amount(amount_str)
                        
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
            
            return transactions
        
        except Exception as e:
            raise Exception(f"Error parsing MT940 file: {str(e)}")

def main():
    root = tk.Tk()
    app = MT940Converter(root)
    root.mainloop()

if __name__ == "__main__":
    main() 