import sqlite3

conn = sqlite3.connect('backend/kynetic_dev.db')
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM questions WHERE is_active = 1 AND validation_status = 'validated'")
print(f"Total Active Validated: {c.fetchone()[0]}")

print("\n--- By Category ---")
c.execute("SELECT category, count(*) FROM questions WHERE is_active = 1 AND validation_status = 'validated' GROUP BY category")
for cat, cnt in c.fetchall():
    print(f"  {cat}: {cnt}")

print("\n--- By Question Type ---")
c.execute("SELECT question_type, count(*) FROM questions WHERE is_active = 1 AND validation_status = 'validated' GROUP BY question_type")
for qt, cnt in c.fetchall():
    print(f"  {qt}: {cnt}")

print("\n--- By Difficulty Level ---")
c.execute("SELECT difficulty_level, count(*) FROM questions WHERE is_active = 1 AND validation_status = 'validated' GROUP BY difficulty_level ORDER BY difficulty_level")
for lvl, cnt in c.fetchall():
    print(f"  Level {lvl}: {cnt}")

print("\n--- By Programming Language ---")
c.execute("SELECT programming_language, count(*) FROM questions WHERE is_active = 1 AND validation_status = 'validated' GROUP BY programming_language")
for lang, cnt in c.fetchall():
    print(f"  {lang}: {cnt}")

