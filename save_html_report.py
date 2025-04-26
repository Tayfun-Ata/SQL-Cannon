import os
import re
import time

def save_html_report(results, output_file):
    """Generate an enhanced HTML report from the scan results."""
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Ensure directory exists
        
        # Parse results to categorize findings
        vulnerabilities = []
        info_logs = []
        errors = []
        
        for line in results:
            line = line.strip()
            if "SQL Injection detected" in line:
                vulnerabilities.append(line)
            elif "[INFO]" in line:
                info_logs.append(line)
            elif "[ERROR]" in line or "[-]" in line:
                errors.append(line)
        
        # Create HTML report with modern styling
        with open(output_file, 'w') as html_file:
            html_file.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Injection Scan Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        h1 {{
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .summary {{
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }}
        .summary-item {{
            background: #fff;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            width: 30%;
            min-width: 250px;
            margin-bottom: 15px;
        }}
        .vulnerabilities {{
            background-color: #fadbd8;
            border-left: 4px solid #e74c3c;
        }}
        .safe {{
            background-color: #d5f5e3;
            border-left: 4px solid #2ecc71;
        }}
        .warnings {{
            background-color: #fcf3cf;
            border-left: 4px solid #f1c40f;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        th {{
            background-color: #2c3e50;
            color: white;
            text-align: left;
            padding: 12px 15px;
        }}
        td {{
            padding: 10px 15px;
            border-bottom: 1px solid #ddd;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #e9f7fe;
        }}
        .vulnerability-item {{
            background-color: #fdedec;
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
        }}
        .error-item {{
            background-color: #fcf3cf;
            border-left: 4px solid #f39c12;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
        }}
        .info-item {{
            background-color: #ebf5fb;
            border-left: 4px solid #3498db;
            padding: 10px;
            margin-bottom: 8px;
            border-radius: 4px;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: right;
        }}
        pre {{
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>SQL Injection Scan Report</h1>
        <div class="timestamp">Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}</div>
        
        <div class="summary">
            <div class="summary-item {('vulnerabilities' if vulnerabilities else 'safe')}">
                <h3>Vulnerabilities</h3>
                <p>{len(vulnerabilities)} found</p>
            </div>
            <div class="summary-item">
                <h3>Tests Run</h3>
                <p>{sum(1 for line in info_logs if 'Total payloads' in line)}</p>
            </div>
            <div class="summary-item {('warnings' if errors else 'safe')}">
                <h3>Errors</h3>
                <p>{len(errors)}</p>
            </div>
        </div>""")
            
            # Vulnerabilities section
            if vulnerabilities:
                html_file.write("""
        <h2>Vulnerabilities Detected</h2>
        <div class="vulnerabilities-list">""")
                
                for vuln in vulnerabilities:
                    # Extract URL from the vulnerability line if possible
                    url_match = re.search(r'at: (https?://[^\s]+)', vuln)
                    url = url_match.group(1) if url_match else "Unknown URL"
                    
                    # Extract detection method if available
                    method_match = re.search(r'Detection method: ([^\n]+)', vuln)
                    method = method_match.group(1) if method_match else "Unknown method"
                    
                    html_file.write(f"""
            <div class="vulnerability-item">
                <h3>SQL Injection Vulnerability</h3>
                <p><strong>URL:</strong> {url}</p>
                <p><strong>Method:</strong> {method}</p>
                <p><strong>Details:</strong> {vuln}</p>
            </div>""")
                
                html_file.write("\n        </div>")
            else:
                html_file.write("""
        <h2>No Vulnerabilities Detected</h2>
        <p>The scan did not detect any SQL injection vulnerabilities on the target.</p>""")
            
            # Error section
            if errors:
                html_file.write("""
        <h2>Errors</h2>
        <div class="errors-list">""")
                
                for error in errors:
                    html_file.write(f"""
            <div class="error-item">
                <p>{error}</p>
            </div>""")
                
                html_file.write("\n        </div>")
            
            # Complete logs section
            html_file.write("""
        <h2>Complete Scan Log</h2>
        <div class="logs">
            <pre>""")
            
            for line in results:
                html_file.write(f"{line}")
            
            html_file.write("""</pre>
        </div>
    </div>
</body>
</html>""")
        
        print(f"[+] Enhanced HTML report saved to {output_file}")
    except Exception as e:
        print(f"[-] Error generating HTML report: {e}")
