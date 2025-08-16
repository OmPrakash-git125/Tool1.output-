import os
import re
import json

def extract_metadata(content):
    proc_match = re.search(r"CREATE\s+PROC(?:EDURE)?\s+([\[\]\w\.]+)", content, re.IGNORECASE)
    if not proc_match:
        return None
    proc_name = proc_match.group(1).replace('[', '').replace(']', '').strip()

    # Extract params more flexibly (handles newlines before AS)
    param_block_match = re.search(
        r"CREATE\s+PROC(?:EDURE)?\s+[\[\]\w\.]+\s*(.*?)\bAS\b",
        content, re.IGNORECASE | re.DOTALL
    )
    params = []
    if param_block_match:
        param_text = param_block_match.group(1).strip()
        if param_text:
            param_lines = re.split(r',\s*(?![^(]*\))', param_text)
            for line in param_lines:
                line = line.strip().rstrip(',;')
                if not line:
                    continue
                param_match = re.match(r'(@[\w]+)\s+([\w\(\),]+)', line)
                if param_match:
                    name = param_match.group(1)
                    type_raw = param_match.group(2).upper()
                    if type_raw.startswith(('DECIMAL', 'NUMERIC')):
                        type_ = 'NUMERIC'
                    elif type_raw in ('INT', 'INTEGER'):
                        type_ = 'INTEGER'
                    elif type_raw.startswith('CHAR'):
                        type_ = 'CHAR'
                    else:
                        type_ = type_raw.split('(')[0]
                    params.append({"name": name, "type": type_})

    # Extract procedure calls
    calls = list(set(re.findall(r"\b(?:EXEC|CALL)\s+([\[\]\w\.]+)", content, re.IGNORECASE)))
    calls = [c.replace('[', '').replace(']', '') for c in calls]

    # Extract tables (keep first appearance order)
    table_pattern = re.compile(
        r"\b(?:FROM|JOIN|INTO|UPDATE|DELETE\s+FROM)\s+([\[\]\w\.#]+)",
        re.IGNORECASE
    )
    raw_tables = table_pattern.findall(content)
    cleaned_tables, seen_tables = [], set()
    skip_words = {"log", "the", "select", "set", "values", "where", "if", "begin", "end"}

    for t in raw_tables:
        t = t.replace('[', '').replace(']', '').strip()
        if (
            t.lower() not in skip_words
            and not re.search(r'(cursor$|^cur_)', t, re.IGNORECASE)
            and t not in seen_tables
        ):
            cleaned_tables.append(t)
            seen_tables.add(t)

    return {
        proc_name: {
            "params": params,
            "calls": calls,
            "tables": cleaned_tables
        }
    }

def process_sql_file(file_path):
    index = {}
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by GO to handle multiple procedures
    proc_blocks = re.split(r"\bGO\b", content, flags=re.IGNORECASE)
    for block in proc_blocks:
        block = block.strip()
        if not block:
            continue
        metadata = extract_metadata(block)
        if metadata:
            index.update(metadata)

    return index

def process_sql_folder(folder_path):
    index = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".sql"):
            file_path = os.path.join(folder_path, filename)
            index.update(process_sql_file(file_path))
    return index

if __name__ == "__main__":
    # Change to your path — works for both file & folder
    path = r"C:\Users\OmPrakashJha\OneDrive - McLaren Strategic Solutions US Inc\Desktop\sybase_indexer_project\sybase-sp-indexer\sybase_indexer_project\test1_sql\test.sql"

    if os.path.isfile(path):
        index = process_sql_file(path)
    elif os.path.isdir(path):
        index = process_sql_folder(path)
    else:
        raise FileNotFoundError(f"❌ Path not found: {path}")

    with open("index.json", "w", encoding="utf-8") as out_file:
        json.dump(index, out_file, indent=2)

    print("✅ index.json generated successfully.")
