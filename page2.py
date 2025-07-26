import re
import oracledb
from testquery import DB_HOST, DB_PORT, DB_SID, DB_USER, DB_PASSWORD
# Load ASP file content
with open("fois_carr_action.asp", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Find all table names (FROM or JOIN)
tables = set(re.findall(r'\b(?:FROM|JOIN)\s+([A-Z0-9_\.]+)', content, re.IGNORECASE))
tables = sorted(tables)

# Print table names for selection
print("Available tables:")
for i, t in enumerate(tables):
    print(f"{i+1}. {t}")
