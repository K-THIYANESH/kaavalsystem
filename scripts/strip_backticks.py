from pathlib import Path


def strip_backticks_from_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines:
        return False

    # Find the first and last lines that look like a triple-backtick fence.
    first_idx = None
    last_idx = None
    for i, l in enumerate(lines[:10]):
        if l.strip().startswith("```"):
            first_idx = i
            break

    for i in range(len(lines) - 1, max(-1, len(lines) - 11), -1):
        if lines[i].strip().startswith("```"):
            last_idx = i
            break

    # Only treat as a fence block if a starting fence is near the top
    if first_idx is None or last_idx is None or last_idx <= first_idx:
        return False

    new_lines = lines[first_idx + 1 : last_idx]
    # write back with trailing newline
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return True


def main():
    root = Path(".")
    # Avoid traversing virtualenvs and external third-party code
    exclude_parts = {".venv", "venv", "external", "site-packages", "__pycache__"}

    def is_excluded(p: Path) -> bool:
        return any(part in exclude_parts for part in p.parts)

    py_files = [p for p in root.rglob("*.py") if not is_excluded(p)]
    fixed = 0
    for p in py_files:
        try:
            if strip_backticks_from_file(p):
                print(f"Fixed: {p}")
                fixed += 1
        except Exception as e:
            print(f"Error processing {p}: {e}")

    print(f"Completed. Files fixed: {fixed}")


if __name__ == "__main__":
    main()
