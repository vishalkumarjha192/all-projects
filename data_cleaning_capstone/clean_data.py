"""
Data Cleaning Capstone Project
Dataset: synthetic student records for demonstration.
Run: python clean_data.py
Requires: pandas
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "students_raw.csv"
OUTPUT = ROOT / "students_cleaned.csv"
REPORT = ROOT / "cleaning_report.txt"

df = pd.read_csv(INPUT)
initial_rows = len(df)
initial_missing = int(df.isna().sum().sum())

# 1. Remove exact duplicate rows.
df = df.drop_duplicates()

# 2. Standardize whitespace and text fields.
for col in ["Student_ID", "Name", "Gender", "Course", "Email"]:
    df[col] = df[col].astype("string").str.strip()

df["Name"] = df["Name"].str.title()
df["Email"] = df["Email"].str.lower()
df["Course"] = df["Course"].str.title()

# 3. Normalize categories.
gender_map = {
    "m": "Male", "male": "Male",
    "f": "Female", "female": "Female",
    "other": "Other"
}
df["Gender"] = df["Gender"].str.lower().map(gender_map).fillna("Unknown")

course_map = {
    "Data Analytics": "Data Analytics",
    "Business": "Business",
    "It": "IT"
}
df["Course"] = df["Course"].map(course_map).fillna("Unknown")

# 4. Convert numeric columns and clean percent signs.
df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
df["Attendance"] = (
    df["Attendance"].astype("string").str.replace("%", "", regex=False)
)
df["Attendance"] = pd.to_numeric(df["Attendance"], errors="coerce")

# 5. Apply basic business rules. Invalid values become missing.
df.loc[~df["Age"].between(16, 100), "Age"] = pd.NA
df.loc[~df["Score"].between(0, 100), "Score"] = pd.NA
df.loc[~df["Attendance"].between(0, 100), "Attendance"] = pd.NA

# 6. Fill missing numeric values with the median (rounded where appropriate).
for col in ["Age", "Score", "Attendance"]:
    df[col] = df[col].fillna(df[col].median())
df["Age"] = df["Age"].round().astype("Int64")
df["Score"] = df["Score"].round(1)
df["Attendance"] = df["Attendance"].round(1)

# 7. Validate key fields and flag duplicate IDs.
df["Email_Valid"] = df["Email"].str.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", na=False)
df["Student_ID_Duplicate"] = df["Student_ID"].duplicated(keep=False)

df.to_csv(OUTPUT, index=False)

final_rows = len(df)
final_missing = int(df.isna().sum().sum())
report = f"""DATA CLEANING REPORT
====================
Input file: {INPUT.name}
Output file: {OUTPUT.name}

Initial rows: {initial_rows}
Rows after removing exact duplicates: {final_rows}
Exact duplicate rows removed: {initial_rows - final_rows}
Missing cells before cleaning: {initial_missing}
Missing cells after cleaning: {final_missing}

Cleaning steps:
- Removed exact duplicate rows
- Trimmed whitespace and standardized names, email addresses, and categories
- Converted age, score, and attendance to numeric values
- Removed percent signs from attendance
- Set out-of-range age, score, and attendance values to missing
- Imputed missing numeric values using each column's median
- Added email-format and duplicate-student-ID validation flags

Note: This is a learning example using synthetic data. Review imputation and
business rules with a project supervisor before using them on real data.
"""
REPORT.write_text(report, encoding="utf-8")
print(report)
