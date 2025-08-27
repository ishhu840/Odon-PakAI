#!/usr/bin/env python3
"""
Find “Table 1” … “Table 5” → export the table below → 1 Excel / PDF
"""

import os, re, glob, pdfplumber, pandas as pd
from tqdm import tqdm

PDF_DIR = "pdfs"
OUT_DIR = "excel_out"
os.makedirs(OUT_DIR, exist_ok=True)

SHEETS = ["T1 Province", "T2 Sindh", "T3 Baloch", "T4 KP", "T5 Lab"]

def clean(txt):
    return re.sub(r"\s+", " ", str(txt)).strip()

def find_table_after_label(pdf, label):
    """
    Returns the **first** table whose top-left cell **starts with** `label`
    (case-insensitive).  label = "Table 1", "Table 2", …
    """
    for page in pdf.pages:
        for tbl in page.extract_tables():
            if tbl and tbl[0] and tbl[0][0]:
                first = clean(tbl[0][0])
                if first.lower().startswith(label.lower()):
                    # Build DataFrame
                    df = pd.DataFrame(tbl[1:], columns=[clean(c) for c in tbl[0]])
                    # commas → numeric, NR → NaN
                    df = df.replace({r",": "", "NR": pd.NA}, regex=True)
                    # force numeric columns (skip non-numeric ones)
                    for col in df.columns[1:]:
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                    return df
    return pd.DataFrame()

for pdf_path in tqdm(glob.glob(os.path.join(PDF_DIR, "*.pdf"))):
    basename = os.path.splitext(os.path.basename(pdf_path))[0]
    out_xlsx = os.path.join(OUT_DIR, f"{basename}.xlsx")

    with pdfplumber.open(pdf_path) as pdf:
        dfs = [find_table_after_label(pdf, f"Table {i+1}") for i in range(5)]

    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        for df, sheet in zip(dfs, SHEETS):
            if not df.empty:
                df.to_excel(writer, sheet_name=sheet, index=False)

print("✅ All PDFs processed — Excel files in", OUT_DIR)