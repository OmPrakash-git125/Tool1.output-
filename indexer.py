import os
import re
import json

def extract_metadata(content):
    proc_match = re.search(r"CREATE\s+PROC(?:EDURE)?\s+(\w+)", content, re.IGNORECASE)
    if not proc_match:
        return None
    proc_name = proc_match.group(1)

    param_block_match = re.search(r"\bCREATE\s+PROC(?:EDURE)?\s+\w+\s*\((.*?)\)", content, re.IGNORECASE | re.DOTALL)
    params = []
    if param_block_match:
        param_block = param_block_match.group(1)
        param_lines = [line.strip() for line in param_block.split(",")]
        for line in param_lines:
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0].rstrip(',')
                type_ = parts[1].upper()
                params.append({"name": name, "type": type_})
    else:
        param_matches = re.findall(r"(@\w+)\s+(\w+)", content)
        for name, type_ in param_matches:
            params.append({"name": name, "type": type_.upper()})

    calls = list(set(re.findall(r"\b(?:EXEC|CALL)\s+(\w+)", content, re.IGNORECASE)))
    tables = list(set(re.findall(r"\b(?:FROM|JOIN|INTO|UPDATE|DELETE\s+FROM)\s+(\w+)", content, re.IGNORECASE)))

    return {
        proc_name: {
            "params": params,
            "calls": calls,
            "tables": tables
        }
    }

def index_stored_procedures(folder_path):
    index = {}
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
    folder_path = r"C:\Users\OmPrakashJha\OneDrive - McLaren Strategic Solutions US Inc\Desktop\sybase_indexer_project\test"
    index_stored_procedures(folder_path)
