"""
Verify that all 'hemisphere' references have been removed (except in comments)
"""
import os
import re
from pathlib import Path

root_dir = Path(r"e:\Projects\HDRI_editor\hdri_light_studio")

# Search for any remaining hemisphere references
py_files = list(root_dir.rglob("*.py"))

print("🔍 Checking for remaining 'hemisphere' references...\n")

issues_found = []

for py_file in py_files:
    with open(py_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        # Skip comments and docstrings
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        
        # Check for hemisphere (case-insensitive)
        if re.search(r'\bhemisphere\b', line, re.IGNORECASE):
            # Exclude if it's in a comment on the same line
            if '#' in line:
                code_part = line.split('#')[0]
                if not re.search(r'\bhemisphere\b', code_part, re.IGNORECASE):
                    continue
            
            issues_found.append({
                'file': py_file.relative_to(root_dir),
                'line': i,
                'content': line.strip()
            })

if issues_found:
    print(f"❌ Found {len(issues_found)} remaining 'hemisphere' references:\n")
    for issue in issues_found:
        print(f"  {issue['file']}:{issue['line']}")
        print(f"    → {issue['content'][:80]}")
        print()
else:
    print("✅ SUCCESS! No 'hemisphere' references found in code!")
    print("   (Only in comments/docstrings for documentation)")

# Check for correct sphere references
print("\n🔍 Verifying correct 'sphere' usage...\n")

required_patterns = [
    ("sphere_props", "Scene property name"),
    ("sphere_name", "Property: sphere name"),
    ("sphere_scale", "Property: sphere scale"),
    ("sphere_type", "Property: sphere type"),
    ("SphereProperties", "Class name"),
    ("HDRI_Preview_Sphere", "Object name"),
]

found_patterns = []
for pattern, description in required_patterns:
    count = 0
    for py_file in py_files:
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            count += content.count(pattern)
    
    if count > 0:
        found_patterns.append((pattern, count, description))
        print(f"✅ {pattern:30} → {count:3} occurrences ({description})")
    else:
        print(f"❌ {pattern:30} → NOT FOUND!")

print("\n" + "="*70)
if not issues_found and len(found_patterns) == len(required_patterns):
    print("🎉 VERIFICATION COMPLETE - ALL CHECKS PASSED!")
else:
    print("⚠️  Some issues found - please review above")
print("="*70)
