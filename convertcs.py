def read_txt_file_as_string(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

# Usage:
txt_file = "anomalies.txt"
full_text = read_txt_file_as_string(txt_file)
