import json
import sys

def parse_json_and_create_html_table(json_file_path, output_html_path):
    # Load the JSON data from the file
    with open(json_file_path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            sys.exit(1)

    # Extract the "features" list from the JSON data
    features = data.get("features", [])
    if not isinstance(features, list):
        print("Error: 'features' key is missing or not a list in the JSON file.")
        sys.exit(1)

    # Initialize a dictionary to store Score/Coverage/Match data by gene name
    score_coverage_match_by_gene = {}

    # Counters for summary table
    summary_counts = {
        "gene": 0,
        "CDS": 0,
        "rRNA": 0,
        "tRNA": 0
    }

    # First pass: Extract Score/Coverage/Match data for all genes and count entries
    for entry in features:
        if not isinstance(entry, dict):
            continue

        entry_type = entry.get("type", "")
        gene_name = entry.get("gene", "")
        info = entry.get("info", "")

        # Update summary counts
        if entry_type in summary_counts:
            summary_counts[entry_type] += 1

        # Check if the info field contains Score/Coverage/Match data
        if gene_name and "psl score" in info and "coverage" in info and "match" in info:
            try:
                score_start = info.find("psl score") + len("psl score")
                score_end = info.find(",", score_start)
                score = info[score_start:score_end].strip()

                coverage_start = info.find("coverage") + len("coverage")
                coverage_end = info.find("%", coverage_start)
                coverage = info[coverage_start:coverage_end].strip() + "%"

                match_start = info.find("match") + len("match")
                match_end = info.find("%", match_start)
                match = info[match_start:match_end].strip() + "%"

                score_coverage_match = f"psl score {score}, coverage {coverage}, match {match}"
                score_coverage_match_by_gene[gene_name] = score_coverage_match
            except Exception as e:
                print(f"Error parsing 'info' field for gene {gene_name}: {e}")

    # Second pass: Build the table data for CDS, rRNA, and tRNA entries
    table_data = []
    for entry in features:
        if not isinstance(entry, dict):
            continue

        entry_type = entry.get("type", "")
        if entry_type not in ["CDS", "tRNA", "rRNA"]:
            continue  # Skip entries that are not CDS, tRNA, or rRNA

        gene_name = entry.get("gene", "") or entry.get("product", "")
        annotator = entry.get("annotator", "")
        score_coverage_match = score_coverage_match_by_gene.get(gene_name, "")
        function = entry.get("product", "") or "No function description available"

        # Append the extracted data to the table_data list
        table_data.append([
            entry_type,
            gene_name,
            annotator,
            score_coverage_match,
            function  # New column for function
        ])

    # Generate the HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Genomic Data Table</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 20px;
            }
            .tab {
                overflow: hidden;
                border: 1px solid #ccc;
                background-color: #f1f1f1;
            }
            .tab button {
                background-color: inherit;
                float: left;
                border: none;
                outline: none;
                cursor: pointer;
                padding: 14px 16px;
                transition: 0.3s;
            }
            .tab button:hover {
                background-color: #ddd;
            }
            .tab button.active {
                background-color: #ccc;
            }
            .tabcontent {
                display: none;
                padding: 20px;
                border: 1px solid #ccc;
                border-top: none;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-size: 1em;
                font-family: Arial, sans-serif;
                min-width: 400px;
            }
            thead tr {
                background-color: #009879;
                color: #ffffff;
                text-align: left;
            }
            th, td {
                padding: 12px 15px;
            }
            tbody tr {
                border-bottom: 1px solid #dddddd;
            }
            tbody tr:nth-of-type(even) {
                background-color: #f3f3f3;
            }
            tbody tr:last-of-type {
                border-bottom: 2px solid #009879;
            }
        </style>
    </head>
    <body>
        <h1>Genomic Data</h1>

        <!-- Tab Buttons -->
        <div class="tab">
            <button class="tablinks" onclick="openTab(event, 'MainTable')">Main Table</button>
            <button class="tablinks" onclick="openTab(event, 'Summary')">Summary</button>
        </div>

        <!-- Main Table -->
        <div id="MainTable" class="tabcontent">
            <h2>Main Table</h2>
            <table>
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Gene/Product Name</th>
                        <th>Annotator</th>
                        <th>Score/Coverage/Match</th>
                        <th>Function</th>
                    </tr>
                </thead>
                <tbody>
    """

    # Add table rows
    for row in table_data:
        html_content += f"""
                    <tr>
                        <td>{row[0]}</td>
                        <td>{row[1]}</td>
                        <td>{row[2]}</td>
                        <td>{row[3]}</td>
                        <td>{row[4]}</td>
                    </tr>
        """

    html_content += """
                </tbody>
            </table>
        </div>

        <!-- Summary Table -->
        <div id="Summary" class="tabcontent">
            <h2>Summary Table</h2>
            <table>
                <thead>
                    <tr>
                        <th>Entry Type</th>
                        <th>Count</th>
                    </tr>
                </thead>
                <tbody>
    """

    # Add summary rows
    for entry_type, count in summary_counts.items():
        html_content += f"""
                    <tr>
                        <td>{entry_type}</td>
                        <td>{count}</td>
                    </tr>
        """

    html_content += """
                </tbody>
            </table>
        </div>

        <!-- JavaScript for Tabs -->
        <script>
            function openTab(evt, tabName) {
                var i, tabcontent, tablinks;
                tabcontent = document.getElementsByClassName("tabcontent");
                for (i = 0; i < tabcontent.length; i++) {
                    tabcontent[i].style.display = "none";
                }
                tablinks = document.getElementsByClassName("tablinks");
                for (i = 0; i < tablinks.length; i++) {
                    tablinks[i].className = tablinks[i].className.replace(" active", "");
                }
                document.getElementById(tabName).style.display = "block";
                evt.currentTarget.className += " active";
            }
            // Open the first tab by default
            document.getElementsByClassName("tablinks")[0].click();
        </script>
    </body>
    </html>
    """

    # Write the HTML content to the output file
    with open(output_html_path, 'w') as html_file:
        html_file.write(html_content)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parse_json_to_html.py <input_json_file> <output_html_file>")
        sys.exit(1)

    input_json_file = sys.argv[1]
    output_html_file = sys.argv[2]

    parse_json_and_create_html_table(input_json_file, output_html_file)
    print(f"HTML file has been created successfully at {output_html_file}")
