"""
LINKSHIELD AI - Official Dataset Importer (R4C / Cyber Crime Reports)
Usage:
    python backend/import_r4c.py <path_to_csv_or_json>
"""
import sys
import os
import csv
import json
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import SessionLocal
from app.analyzers.message import analyze_message
from app.analyzers.url import analyze_url
from app.analyzers.website import analyze_website_content
from app.models import Case

def import_r4c_file(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)

    print(f"[*] Importing records from {filepath} into LINKSHIELD database...")
    db = SessionLocal()
    imported = 0
    skipped = 0

    try:
        if path.suffix.lower() == '.csv':
            with open(path, mode='r', encoding='utf-8', errors='replace') as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    content = (
                        row.get("content") or row.get("text") or row.get("message") or
                        row.get("url") or row.get("complaint_text") or ""
                    ).strip()
                    if not content:
                        skipped += 1
                        continue

                    itype = (row.get("input_type") or ("url" if content.startswith("http") else "message")).lower()
                    subject = row.get("subject") or row.get("title") or f"R4C Dataset Record #{idx + 1}"

                    if itype == "url":
                        analyze_url(content, db=db, is_demo=False, subject=subject)
                    elif itype == "website":
                        analyze_website_content(url=content if content.startswith("http") else None, raw_html=content if not content.startswith("http") else None, db=db, is_demo=False, subject=subject)
                    else:
                        analyze_message(content, db=db, is_demo=False, subject=subject)

                    imported += 1
                    if imported % 10 == 0:
                        print(f"    Processed {imported} cases...")
        elif path.suffix.lower() == '.json':
            with open(path, mode='r', encoding='utf-8', errors='replace') as f:
                records = json.load(f)
                if not isinstance(records, list):
                    records = [records]
                for idx, item in enumerate(records):
                    content = (item.get("content") or item.get("text") or item.get("message") or item.get("url") or "").strip()
                    if not content:
                        skipped += 1
                        continue
                    itype = item.get("input_type", "message").lower()
                    subject = item.get("subject") or f"Imported Case #{idx + 1}"

                    if itype == "url":
                        analyze_url(content, db=db, is_demo=False, subject=subject)
                    else:
                        analyze_message(content, db=db, is_demo=False, subject=subject)
                    imported += 1
        else:
            print("[ERROR] Unsupported format. Please provide a .csv or .json file.")
            sys.exit(1)

        print(f"[SUCCESS] Import completed successfully! Total imported: {imported}, Skipped: {skipped}")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backend/import_r4c.py <path_to_csv_or_json>")
        sys.exit(1)
    import_r4c_file(sys.argv[1])
