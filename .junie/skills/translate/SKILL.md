---
name: translate
description: Translate web user interface strings from English to another language.
---

# Translate Skill

Use this skill when asked to translate.

## Key Principles

- The source language is always English.
- Identify the target language. If the target language is not specified, ask the user.
- Preserve the original formatting, structure, and markup.
- Keep placeholders unchanged — only translate human-readable text.
- Maintain the tone and style of the original (formal, informal, technical).

## Guidelines

### Translating .po files:
- The `.po` files are located in the `src/nsupdate/locale` directory.
- Follow the standard gettext format and only fill in `msgstr` entries.
- Never change the `msgid` entries.
- When asked to translate missing strings, only process the strings with currently empty `msgstr` entries.
- **After any edits to a `.po` file**, always validate and compile it:
  1. Validate: `msgfmt --check-format -o /dev/null <path/to/file.po>`
  2. Compile: `msgfmt -o <path/to/file.mo> <path/to/file.po>` (output `.mo` in the same directory as the `.po` file)
  3. Validate the compiled `.mo` file: `msgunfmt <path/to/file.mo> | msgfmt --check-format -o /dev/null -`

### Quality:
- Prefer natural, fluent translations over literal word-for-word translations.
- For ambiguous terms, add a brief translator's note as a comment if appropriate.
- Always check the `glossaries/<TARGET_LANGUAGE>.md` file to produce a consistent translation.
- If the text contains domain-specific jargon (e.g., DNS, networking), use the accepted terminology in the target language.

### Scripts:
- `scripts/find_missing.py <language_code>` — finds all entries with empty `msgstr` in a `.po` file for the given language.
  Use it to identify which strings still need translation.
