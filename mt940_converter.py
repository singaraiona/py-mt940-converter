import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import pandas as pd
from datetime import datetime
import os

class MT940Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("MT940 to CSV Converter")
        self.root.geometry("600x400")
        
        # Initialize file path
        self.loaded_file_path = None
        
        # Configure style
        self.root.configure(bg='#f0f0f0')
        
        # Create main frame
        main_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="MT940 to CSV Converter",
            font=('Helvetica', 16, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = """
        This tool converts MT940 bank statement files (.sta) to CSV format.
        
        Steps:
        1. Click 'Load File' to choose your .sta file
        2. Click 'Convert' to create the CSV file
        3. The output CSV will be created in the same folder
        4. The CSV will contain: Date, Amount, Currency, Bank Reference, and Description
        """
        
        instructions_label = tk.Label(
            main_frame,
            text=instructions,
            font=('Helvetica', 10),
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
            font=('Helvetica', 12),
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=10
        )
        self.load_button.pack(side='left', padx=10)
        
        # Convert button (initially disabled)
        self.convert_button = tk.Button(
            button_frame,
            text="Convert to CSV",
            command=self.convert_file,
            font=('Helvetica', 12),
            bg='#2196F3',
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
            font=('Helvetica', 10),
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
        
        # Version info
        version_label = tk.Label(
            main_frame,
            text="Version 1.0",
            font=('Helvetica', 8),
            bg='#f0f0f0'
        )
        version_label.pack(side='bottom', pady=(20, 0))

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select MT940 File",
            filetypes=[("STA files", "*.sta"), ("All files", "*.*")]
        )
        
        if file_path:
            self.loaded_file_path = file_path
            self.status_label.config(text=f"File loaded: {file_path}")
            self.convert_button.config(state='normal')
            self.progress_var.set(50)

    def convert_file(self):
        if not self.loaded_file_path:
            messagebox.showerror("Error", "Please load a file first")
            return
            
        try:
            self.status_label.config(text="Converting file...")
            self.progress_var.set(75)
            self.root.update()
            
            # Convert the file
            transactions = self.parse_mt940(self.loaded_file_path)
            
            # Create output filename
            output_path = os.path.splitext(self.loaded_file_path)[0] + '.csv'
            
            # Convert to DataFrame and save
            df = pd.DataFrame(transactions)
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            df['Amount'] = df['Amount'].round(2)
            df.to_csv(output_path, index=False)
            
            self.progress_var.set(100)
            self.status_label.config(
                text=f"Success! Converted {len(transactions)} transactions.\nOutput saved to: {output_path}"
            )
            messagebox.showinfo("Success", "File converted successfully!")
            
            # Reset state
            self.loaded_file_path = None
            self.convert_button.config(state='disabled')
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to convert file: {str(e)}")
            self.progress_var.set(0)

    def clean_description(self, desc):
        desc = desc.replace('<', ' ').replace('>', ' ')
        desc = ' '.join(desc.split())
        return desc

    def parse_amount(self, amount_str):
        try:
            parts = amount_str.split('N')
            if len(parts) < 2:
                return 0.0
            amount_part = parts[1].split('N')[0]
            amount_part = amount_part.replace(',', '.')
            return float(amount_part)
        except (ValueError, IndexError):
            print(f"Error parsing amount: {amount_str}")
            return 0.0

    def parse_mt940(self, file_path):
        transactions = []
        
        with open(file_path, 'r', encoding='iso-8859-1') as file:
            lines = file.readlines()
            
        current_transaction = None
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith(':61:'):
                parts = line[4:].split('N')
                date_str = parts[0][:6]
                
                amount_str = line[4:]
                
                if 'D' in amount_str:
                    amount = self.parse_amount(amount_str)
                elif 'C' in amount_str:
                    amount = -self.parse_amount(amount_str)
                else:
                    continue
                
                date = datetime.strptime(date_str, '%y%m%d')
                
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
                                if desc_line.startswith('<00'):
                                    description.append(desc_line[3:])
                                elif desc_line.startswith('<20'):
                                    description.append(desc_line[3:])
                                elif desc_line.startswith('<21'):
                                    description.append(desc_line[3:])
                                elif desc_line.startswith('<22'):
                                    description.append(desc_line[3:])
                                elif desc_line.startswith('<23'):
                                    description.append(desc_line[3:])
                                elif desc_line.startswith('<27'):
                                    description.append(desc_line[3:])
                                elif desc_line.startswith('<28'):
                                    description.append(desc_line[3:])
                                elif desc_line.startswith('<29'):
                                    description.append(desc_line[3:])
                            j += 1
                        break
                    else:
                        description.append(next_line)
                    j += 1
                
                current_transaction = {
                    'Date': date,
                    'Amount': amount,
                    'Currency': 'PLN',
                    'Bank Reference': parts[0].split('//')[-1] if '//' in parts[0] else '',
                    'Description': self.clean_description(' '.join(description))
                }
                transactions.append(current_transaction)
        
        return transactions

def main():
    root = tk.Tk()
    app = MT940Converter(root)
    root.mainloop()

if __name__ == "__main__":
    main() 