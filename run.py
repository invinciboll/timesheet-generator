from datetime import datetime
import os
import platform
import tkinter as tk
from tkinter import messagebox
import csv
import pdfkit
from functools import partial

class Logic():
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Name List")
        self.window.geometry("400x400")
        self.window.bind('<Return>', self.add_name)

        self.left_frame = tk.Frame(self.window)
        self.left_frame.pack(side='left', padx=20, pady=20, fill='y')
        self.right_frame = tk.Frame(self.window)
        self.right_frame.pack(side='right', padx=20, pady=20, fill='y')

        # Load names from CSV file
        names = []
        try:
            with open('names.csv', 'r') as csvfile:
                csvreader = csv.reader(csvfile)
                names = [row[0] for row in csvreader]
        except FileNotFoundError:
            pass
        
        self.names_and_vars = []
        for name in names:
            name_frame = tk.Frame(self.left_frame)
            name_frame.pack(anchor='w', pady=5)

            var = tk.IntVar(value=1)
            checkbox = tk.Checkbutton(name_frame, text=name, variable=var)
            checkbox.pack(side='left')

            delete_button = tk.Button(name_frame, text="X", command=partial(self.delete_name, name_frame, name))
            delete_button.pack(side='left', padx=5)

            self.names_and_vars.append((name, var))

        self.entry = tk.Entry(self.right_frame, width=25)
        self.entry.pack(anchor='n')
        add_button = tk.Button(self.right_frame, text="Hinzufügen", command=self.add_name, width=20)
        add_button.pack(anchor='n')

        print_button = tk.Button(self.right_frame, text="Drucken", command=self.print_pdf, width=20)
        print_button.pack()

        export_button = tk.Button(self.right_frame, text="PDF exportieren", command=self.export_pdf, width=20)
        export_button.pack()

    def run(self):
        self.window.mainloop()

    def add_name(self, event=None):
        new_name = self.entry.get()
        if new_name:
            name_frame = tk.Frame(self.left_frame)
            name_frame.pack(anchor='w', pady=5)

            var = tk.IntVar(value=1)
            checkbox = tk.Checkbutton(name_frame, text=new_name, variable=var)
            checkbox.pack(side='left')

            delete_button = tk.Button(name_frame, text="x", command=partial(self.delete_name, name_frame, new_name))
            delete_button.pack(side='left', padx=5)

            self.names_and_vars.append((new_name, var))

            with open('names.csv', 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow([new_name])

            self.entry.delete(0, tk.END)

    def delete_name(self, frame, name):
        frame.destroy()
        self.names_and_vars = [nv for nv in self.names_and_vars if nv[0] != name]
        self.update_csv()

    def update_csv(self):
        with open('names.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            for child in self.left_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    name = child.winfo_children()[0].cget("text")
                    csvwriter.writerow([name])
    
    def generate_table(self, name):
        kw = datetime.now().strftime("%V")
        with open('template.html') as f:
            table_content =  f.read()
        return table_content
    
    def generate_pdf(self, file_path):
        html_content = "<html><body>"
        for name, var in self.names_and_vars:
            if var.get() == 1:
                table = self.generate_table(name)
                html_content += table
        html_content += "</body></html>"

        # Determine the platform and set the wkhtmltopdf path accordingly
        if platform.system() == 'Windows':
            wkhtmltopdf_path = os.path.join('tooling', 'wkhtmltopdf', 'bin', 'wkhtmltopdf.exe')
        else:  # Assuming Fedora or other Linux distributions
            wkhtmltopdf_path = '/usr/bin/wkhtmltopdf'  # Default installation path for Fedora

        # Configure pdfkit with the correct path
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

        # Generate the PDF
        return pdfkit.from_string(html_content, file_path, configuration=config)
    
    def print_pdf(self):
        file_path = 'output.pdf'
        if self.generate_pdf(file_path):
            try:
                os.startfile(file_path, 'print')
                print(f"Opening print menu for {file_path}...")
            except OSError:
                print("Error opening print menu.")
        else:
            print("Error generating PDF.")

    def export_pdf(self):
        pdf = self.generate_pdf('output.pdf')

if __name__ == "__main__":
    logic = Logic()
    logic.run()
