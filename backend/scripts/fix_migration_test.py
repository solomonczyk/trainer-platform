"""Fix test_migration_007_execution.py for new head (008)."""
import re

path = "tests/certification_core/test_migration_007_execution.py"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix initial state check: handle 008 being head
old_start = r'def test_cycle_upgrade_downgrade_upgrade.*?Step 1: verify we start at 007\n\s+rev = _current_revision\(\)\n\s+assert rev == "007" or rev\.startswith\("007"\), f"Expected 007, got {rev}"'
new_start = '''def test_cycle_upgrade_downgrade_upgrade(self, pg_available):
        """Full cycle: ensure at 007 -> downgrade 006 -> upgrade 007."""
        # Step 1: ensure we are at 007 (downgrade from head if needed)
        rev = _current_revision()
        major = rev[:3]
        assert major in ("007", "008"), f"Expected 007 or 008, got {rev}"
        if major == "008":
            _alembic("downgrade", "007")
            rev = _current_revision()
        assert rev == "007" or rev.startswith("007"), f"Expected 007, got {rev}"'''

content = re.sub(old_start, new_start, content, count=1, flags=re.DOTALL)

# Fix upgrade step: "upgrade head" -> "upgrade 007"
content = content.replace(
    '# Step 3: upgrade back to head (007)\n        _alembic("upgrade", "head")',
    '# Step 3: upgrade back to 007\n        _alembic("upgrade", "007")'
)

# Fix final assert to check version 007 not head
content = content.replace(
    'assert rows[0] == "007",',
    'assert rows[0] == "007",  # 007 target, not head'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed {path}")
