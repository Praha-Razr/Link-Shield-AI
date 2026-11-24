"""
LINKSHIELD AI - Demo Dataset Loader
Loads synthetic cases into the SQLite database.
Usage:
    python load_demo.py
"""
import sys
import json
from pathlib import Path

# Setup paths
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir / "backend"))

from app.database import SessionLocal
from app.models import Case, Indicator, Identifier, SimilarityLink
from app.analyzers.message import analyze_message
from app.analyzers.url import analyze_url
from app.analyzers.website import analyze_website_content

def load_demo_data():
    dataset_file = root_dir / "data" / "demo_dataset.json"
    if not dataset_file.exists():
        print(f"[ERROR] Dataset file not found at {dataset_file}")
        sys.exit(1)

    print(f"[*] Reading demo dataset from {dataset_file}...")
    with open(dataset_file, "r", encoding="utf-8") as f:
        cases_data = json.load(f)

    db = SessionLocal()
    try:
        # Clear previous demo cases
        demo_cases = db.query(Case).filter(Case.is_demo == True).all()
        demo_ids = [c.id for c in demo_cases]
        if demo_ids:
            print(f"[*] Clearing {len(demo_ids)} existing demo cases...")
            db.query(Indicator).filter(Indicator.case_id.in_(demo_ids)).delete(synchronize_session=False)
            db.query(Identifier).filter(Identifier.case_id.in_(demo_ids)).delete(synchronize_session=False)
            db.query(SimilarityLink).filter(
                (SimilarityLink.source_case_id.in_(demo_ids)) | (SimilarityLink.target_case_id.in_(demo_ids))
            ).delete(synchronize_session=False)
            db.query(Case).filter(Case.id.in_(demo_ids)).delete(synchronize_session=False)
            db.commit()

        print(f"[*] Seeding {len(cases_data)} synthetic demo cases...")
        loaded = 0
        for item in cases_data:
            c_type = item.get("input_type", "message")
            content = item.get("submitted_content", "")
            cid = item.get("case_id")
            subj = f"DEMO: {item.get('category', 'Case').replace('_', ' ').title()}"

            if c_type == "url":
                res = analyze_url(content, db=db, is_demo=True, subject=subj)
            elif c_type == "website":
                res = analyze_website_content(url=content if content.startswith("http") else None, raw_html=content if not content.startswith("http") else None, db=db, is_demo=True, subject=subj)
            else:
                res = analyze_message(content, db=db, is_demo=True, subject=subj)

            if cid and res:
                # Update case_id if specified in demo dataset
                case_obj = db.query(Case).filter(Case.id == res.id).first()
                if case_obj:
                    # Keep auto-assigned or update
                    pass
            loaded += 1
            if loaded % 10 == 0:
                print(f"    Loaded {loaded}/{len(cases_data)} cases...")

        db.commit()
        print(f"[SUCCESS] Successfully seeded {loaded} demo cases into linkshield.db!")
    except Exception as e:
        print(f"[ERROR] Failed to seed demo data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_demo_data()
