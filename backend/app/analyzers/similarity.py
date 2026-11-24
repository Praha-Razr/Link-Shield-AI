from typing import List, Dict, Any
from rapidfuzz import fuzz
from sqlalchemy.orm import Session
from app.models import Case

def find_similar_cases(content: str, db: Session, current_case_id: str = None, threshold: float = 0.85) -> List[Dict[str, Any]]:
    """
    Compares content with existing cases using RapidFuzz token_set_ratio.
    Returns matches with similarity >= threshold (0.85).
    """
    clean_content = content.strip().lower()
    if not clean_content or len(clean_content) < 10:
        return []

    query = db.query(Case)
    if current_case_id:
        query = query.filter(Case.id != current_case_id)
    
    # Check recent cases (limit to 500 for fast comparison)
    existing_cases = query.order_by(Case.created_at.desc()).limit(500).all()

    matches = []
    for other in existing_cases:
        other_text = (other.raw_content or "").strip().lower()
        if not other_text:
            continue
        
        ratio = fuzz.token_set_ratio(clean_content, other_text) / 100.0
        if ratio >= threshold:
            matches.append({
                "case_id": other.id,
                "similarity": round(ratio, 3),
                "subject": other.subject,
                "risk_level": other.risk_level
            })

    # Sort descending by similarity
    matches.sort(key=lambda x: x["similarity"], reverse=True)
    return matches[:5]
