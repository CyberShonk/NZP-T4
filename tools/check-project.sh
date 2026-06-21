#!/usr/bin/env bash
set -euo pipefail

ROOT=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

printf 'Checking Python syntax...\n'
python3 -m compileall -q src tests

printf 'Checking JSON files...\n'
python3 - <<'PY'
import json
from pathlib import Path

skip_parts = {'.git', '__pycache__', 'reports-local', 'imports-local', '.upstream'}
for path in sorted(Path('.').rglob('*.json')):
    if any(part in skip_parts for part in path.parts):
        continue
    json.loads(path.read_text(encoding='utf-8'))
    print(path)
PY

printf 'Checking text formatting...\n'
python3 - <<'PY'
from pathlib import Path

skip_parts = {
    '.git',
    '.project-context-private',
    '__pycache__',
    'reports-local',
    'imports-local',
    '.upstream',
}
text_suffixes = {
    '.md', '.py', '.json', '.yml', '.yaml', '.toml', '.sh', '.txt', '.csv', '.gsc'
}
problems = []
for path in sorted(Path('.').rglob('*')):
    if not path.is_file() or any(part in skip_parts for part in path.parts):
        continue
    if path.name in {'.gitignore', '.gitattributes', '.editorconfig'} or path.suffix.lower() in text_suffixes:
        data = path.read_bytes()
        if b'\x00' in data:
            continue
        text = data.decode('utf-8')
        if text and not text.endswith('\n'):
            problems.append(f'{path}: missing final newline')
        for number, line in enumerate(text.splitlines(), start=1):
            if line.rstrip(' \t') != line:
                problems.append(f'{path}:{number}: trailing whitespace')
if problems:
    raise SystemExit('\n'.join(problems))
PY

printf 'Running unit tests...\n'
python3 -m unittest discover -s tests -v

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  printf 'Checking tracked paths for prohibited high-risk formats...\n'
  blocked_regex='\.(ff|iwd|d3dbsp|iwi|xmodel_bin|xanim_bin|xmodel_export|xanim_export|exe|dll|asi)$'
  blocked=$(git ls-files | grep -Ei "$blocked_regex" || true)
  if [[ -n "$blocked" ]]; then
    printf 'Blocked tracked paths:\n%s\n' "$blocked" >&2
    exit 1
  fi

  printf 'Checking whitespace in tracked/staged changes...\n'
  git diff --check
  git diff --cached --check
fi

printf 'All checks passed.\n'
