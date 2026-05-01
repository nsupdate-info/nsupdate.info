#!/usr/bin/env python3
"""Find missing translations (empty msgstr) in a .po file.

Usage: python find_missing.py <language_code>
Example: python find_missing.py fr
"""
import sys
import os

try:
    import polib
except ImportError:
    print("Error: polib is required. Install it with: pip install polib")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python find_missing.py <language_code>")
    print("Example: python find_missing.py fr")
    sys.exit(1)

lang = sys.argv[1]
project_root = os.path.dirname(os.path.abspath(os.path.join(__file__, '..', '..', '..', '..')))

po_path = os.path.join(project_root, 'src', 'nsupdate', 'locale', lang, 'LC_MESSAGES', 'django.po')

if not os.path.exists(po_path):
    print(f"File not found: {po_path}")
    sys.exit(1)

po = polib.pofile(po_path)
missing = [e for e in po if not e.msgstr and not e.obsolete and e.msgid]

if missing:
    print(f"Found {len(missing)} missing translation(s) for '{lang}':")
    for i, entry in enumerate(missing):
        print(f"  {i}: {repr(entry.msgid)}")
else:
    print(f"No missing translations for '{lang}'.")
