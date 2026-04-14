with open('tests/test_api.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "test_extract_pdf_path_not_exists(" in line or "test_extract_pdf_path_pdf_processing_error(" in line:
        pass
new_lines = lines # just fixing by hand below
