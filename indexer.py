import os
import re
import json

def extract_metadata(content):
    # Extract procedure name
    proc_match = re.search(r"CREATE\s+PROC(?:EDURE)?\s+(\w+)", content, re.IGNORECASE)
    if not proc_match:
        return None
    proc_name = proc_match.group(1)

    # Extract parameter block — with or without parentheses
    param_block_match = re.search(
        r"CREATE\s+PROC(?:EDURE)?\s+\w+\s*(?:\((.*?)\)|\s+((?:@\w+\s+\w+(?:\(\d+\))?,?\s*)+))",
        content, re.IGNORECASE | re.DOTALL
    )

    params = []
    if param_block_match:
        param_block = param_block_match.group(1) or param_block_match.group(2)
        if param_block:
            param_lines = [line.strip() for line in param_block.split(",")]
            for line in param_lines:
                parts = line.strip().split()
                if len(parts) >= 2:
                    name = parts[0].rstrip(',')
                    type_ = ' '.join(parts[1:]).rstrip(',').upper()
                    if type_ not in ['END', 'AS', 'BEGIN']:  # filter junk
                        params.append({"name": name, "type": type_})

    # Extract procedure calls
    calls = list(set(re.findall(r"\b(?:EXEC|CALL)\s+(\w+)", content, re.IGNORECASE)))

    # Extract table names
    table_pattern = re.compile(
    r"\b(?:FROM|JOIN|INTO|UPDATE|DELETE\s+FROM)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b",
    re.IGNORECASE
    )

    tables = list(set(table_pattern.findall(content)))
    tables = [t for t in tables if t.lower() != "log"]
    # Extract cursor declarations
    cursors = re.findall(r"DECLARE\s+(\w+)\s+CURSOR\s+FOR", content, re.IGNORECASE)

    return {
        proc_name: {
            "params": params,
            "calls": calls,
            "tables": tables,         
        }
    }

def index_stored_procedures(folder_path):
    index = {}
    if not os.path.isdir(folder_path):
        print(f"❌ The path is not a valid directory: {folder_path}")
        return

    for filename in os.listdir(folder_path):
        if filename.endswith(".sql"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                metadata = extract_metadata(content)
                if metadata:
                    index.update(metadata)

    with open("index.json", "w", encoding="utf-8") as out_file:
        json.dump(index, out_file, indent=2)
    print("✅ index.json generated successfully.")

if __name__ == "__main__":
    folder_path = r"C:\Users\OmPrakashJha\OneDrive - McLaren Strategic Solutions US Inc\Desktop\sybase_indexer_project\sybase-sp-indexer\test_sqls"
    index_stored_procedures(folder_path)