import pdfplumber
with pdfplumber.open("samplePDFs\DCS1101 updated230621.pdf") as f:
    print(f.pages[0].extract_table())