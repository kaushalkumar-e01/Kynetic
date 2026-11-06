"""
Question Catalog Aggregator
"""
from typing import List, Dict, Any
from app.services.catalog.dsa_catalog import get_dsa_questions
from app.services.catalog.lang_catalog import get_lang_questions
from app.services.catalog.sql_catalog import get_sql_questions
from app.services.catalog.web_catalog import get_web_questions
from app.services.catalog.cs_catalog import get_cs_questions


def get_all_expanded_questions() -> List[Dict[str, Any]]:
    all_qs: List[Dict[str, Any]] = []
    all_qs.extend(get_dsa_questions())
    all_qs.extend(get_lang_questions())
    all_qs.extend(get_sql_questions())
    all_qs.extend(get_web_questions())
    all_qs.extend(get_cs_questions())
    return all_qs

