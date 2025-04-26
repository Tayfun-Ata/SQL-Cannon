import os
import sys
import asyncio

# Use absolute import paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Add type annotation comments to silence Pylance warnings
from path_manager import PathManager  # type: ignore
from save_html_report import save_html_report  # type: ignore
from vulnerability_scanner import test_sql_injection  # type: ignore
from config import load_config  # type: ignore

from tkinter import Tk, Label, Button, Entry, Text, filedialog, StringVar, END
print(f"Current working directory: {os.getcwd()}")  # Debugging line

def ensure_directory_exists(file_path):
    """Ensure the directory for the given file path exists."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

class SQLCannonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Cannon - SQL Injection Scanner")
        self.root.geometry("600x400")

        # Configuration
        self.config = load_config("config.json")

        # Target URL
        Label(root, text="Target URL:").pack()
        self.target_url = Entry(root, width=50)
        self.target_url.pack()

        # Parameter to Test
        Label(root, text="Parameter to Test:").pack()
        self.parameter = Entry(root, width=50)
        self.parameter.pack()

        # HTTP Method
        Label(root, text="HTTP Method (GET/POST):").pack()
        self.http_method = StringVar(value="GET")
        self.method_entry = Entry(root, textvariable=self.http_method, width=50)
        self.method_entry.pack()

        # Custom Payloads
        Label(root, text="Custom Payloads (comma-separated):").pack()
        self.payloads = Text(root, height=5, width=50)
        self.payloads.pack()

        # Output Folder Selection
        Label(root, text="Output Folder:").pack()
        self.output_folder = StringVar()
        self.output_folder_entry = Entry(root, textvariable=self.output_folder, width=50)
        self.output_folder_entry.pack()
        Button(root, text="Select Folder", command=self.select_output_folder).pack()

        # Run Button
        Button(root, text="Run Scanner", command=self.run_scanner).pack()  # Ensure the button is added here

        # Status
        self.status_label = Label(root, text="", fg="green")
        self.status_label.pack()

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)

    async def run_scanner_async(self):
        target_url = self.target_url.get()
        parameter = self.parameter.get()
        method = self.http_method.get().upper()
        custom_payloads = self.payloads.get("1.0", END).strip().split(",")
        payloads = [payload.strip() for payload in custom_payloads if payload.strip()]

        # Use default payloads if no custom payloads are provided
        if not payloads:
            payloads = [
                "' OR '1'='1--", "' AND '1'='2", "' UNION SELECT NULL--", "' UNION SELECT 1,2,3--",
                "' OR SLEEP(5)--", "' OR BENCHMARK(1000000,MD5(1))--", "' AND 1=2 UNION SELECT NULL,NULL,NULL--",
                "' AND 1=2 UNION SELECT table_name FROM information_schema.tables--",
                "' AND 1=2 UNION SELECT column_name FROM information_schema.columns WHERE table_name='users'--"
            ]

        # Set output log file
        output_folder = self.output_folder.get() or "C:\\Temp"  # Default to C:\Temp if no folder is selected
        path_manager = PathManager(base_directory=output_folder)
        self.config["output_log_file"] = path_manager.resolve_path("output.log")
        self.config["output_html_file"] = path_manager.resolve_path("output.html")
        self.config["resume_file"] = path_manager.resolve_path("resume.txt")
        self.config["vulnerabilities_file"] = path_manager.resolve_path("vulnerabilities.txt")

        # Ensure all files exist
        for key in ["output_log_file", "output_html_file", "resume_file", "vulnerabilities_file"]:
            try:
                resolved_path = self.config[key]
                path_manager.ensure_file_exists(resolved_path)
            except Exception as e:
                print(f"[ERROR] Failed to create file for {key}: {resolved_path}. Error: {e}")

        # Debugging: Print the output log file path
        print(f"Output log file path: {self.config['output_log_file']}")

        # Validate output folder
        if not os.path.isdir(output_folder) and output_folder:
            self.status_label.config(text="Invalid output folder selected.", fg="red")
            print("Error: Invalid output folder selected.")
            return

        # Load resume file if it exists
        resume_file = self.config.get("resume_file")
        if resume_file and os.path.exists(resume_file):
            with open(resume_file, "r") as file:
                completed_payloads = set(file.read().splitlines())
        else:
            completed_payloads = set()

        # Filter out completed payloads
        payloads = [p for p in payloads if p not in completed_payloads]

        # Run the scanner
        try:
            self.status_label.config(text="Running scanner...", fg="blue")
            
            # FIXED: Now pass all payloads at once instead of one by one
            found_vulnerabilities = await test_sql_injection(target_url, parameter, payloads, self.config, method=method)
            
            # Record completed payloads
            if resume_file:
                with open(resume_file, "a") as file:
                    for payload in payloads:
                        file.write(payload + "\n")
            
            # Check for vulnerabilities in the log
            vulnerabilities = []
            try:
                with open(self.config["output_log_file"], "r") as log_file:
                    log_content = log_file.read()
                    for payload in payloads:
                        if payload in log_content and "SQL Injection detected" in log_content:
                            vulnerabilities.append(payload)
            except Exception as e:
                print(f"Warning: Could not read log file: {e}")

            # Save vulnerabilities to a separate file
            if vulnerabilities:
                with open(self.config["vulnerabilities_file"], "w") as vuln_file:
                    vuln_file.write("\n".join(vulnerabilities))
                self.status_label.config(text=f"Vulnerabilities saved to {self.config['vulnerabilities_file']}", fg="green")
            else:
                self.status_label.config(text="No vulnerabilities found.", fg="orange")

            # Generate HTML report
            with open(self.config["output_log_file"], "r") as log_file:
                results = log_file.readlines()
            save_html_report(results, self.config["output_html_file"])
            self.status_label.config(text=f"HTML report saved to {self.config['output_html_file']}", fg="green")
        except Exception as e:
            # Handle and display any errors
            self.status_label.config(text=f"Error: {str(e)}", fg="red")
            print(f"Error during scan: {e}")

    def run_scanner(self):
        asyncio.run(self.run_scanner_async())

if __name__ == "__main__":
    root = Tk()
    app = SQLCannonGUI(root)
    root.mainloop()