"""Concatenate project files into a single text file.

Usage examples:
  python scripts/extract_all.py --root . --output all_code.txt
  python scripts/extract_all.py --root . --output ALL_CODE.txt --ext .py,.js,.html --skip-dirs venv,node_modules --max-size 5242880

Features:
- Skips common ignored directories by default (.git, venv, __pycache__, node_modules, etc.)
- Skips binary files and files larger than --max-size (default 5MB)
- Allows specifying extensions (comma-separated) or use --all to include every file (text-only)
- Adds headers with relative path, size and mtime for each file
"""

from __future__ import annotations
import argparse
import os
from pathlib import Path
from datetime import datetime

DEFAULT_EXTS = [
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".md", ".txt",
    ".json", ".yml", ".yaml", ".sql", ".ini", ".cfg", ".bat", ".sh", ".ps1",
    ".java", ".c", ".cpp", ".h", ".hpp", ".rb", ".go", ".rs", ".php"
]

DEFAULT_SKIP_DIRS = {".git", "venv", "env", "__pycache__", "node_modules", ".venv", ".idea", ".vscode", ".pytest_cache", ".mypy_cache", "qdrant_data", "qdrant_data_test"}

def is_binary_file(p: Path) -> bool:
    try:
        with p.open("rb") as f:
            chunk = f.read(1024)
            if b"\0" in chunk:
                return True
            # heuristic: check for large proportion of non-text bytes
            textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)))
            return bool(chunk) and sum(c not in textchars for c in chunk) / len(chunk) > 0.30
    except Exception:
        return True


def gather_files(root: Path, include_exts: set[str] | None, skip_dirs: set[str], include_all: bool, max_size: int, output_path: Path) -> list[Path]:
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Filter out skip dirs in-place for os.walk
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in filenames:
            file_path = Path(dirpath) / fn
            # skip the output file itself
            if output_path and file_path.resolve() == output_path.resolve():
                continue
            # skip hidden system files like .DS_Store
            if fn in {".DS_Store"}:
                continue
            try:
                if file_path.is_dir():
                    continue
            except Exception:
                continue
            # size limit
            try:
                size = file_path.stat().st_size
            except Exception:
                continue
            if size > max_size:
                continue
            if not include_all:
                if include_exts and file_path.suffix.lower() not in include_exts:
                    continue
            # skip binary
            if is_binary_file(file_path):
                continue
            files.append(file_path)
    files.sort()
    return files


def write_output(files: list[Path], root: Path, out_file: Path):
    written = 0
    with out_file.open("w", encoding="utf-8", errors="replace") as out:
        for p in files:
            try:
                rel = p.relative_to(root)
            except Exception:
                rel = p
            stat = p.stat()
            header = f"\n----- FILE: {rel} -----\nsize: {stat.st_size} bytes | mtime: {datetime.fromtimestamp(stat.st_mtime).isoformat()}\n\n"
            out.write(header)
            with p.open("r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    out.write(line)
            out.write("\n----- END FILE -----\n")
            written += 1
    return written


def parse_args():
    p = argparse.ArgumentParser(description="Concatenate project files into a single file.")
    p.add_argument("--root", default='.', help="Root directory to scan (default: .)")
    p.add_argument("--output", default='ALL_CODE.txt', help="Output filename (default: ALL_CODE.txt)")
    p.add_argument("--ext", default=','.join(DEFAULT_EXTS), help="Comma-separated extensions to include (default: common code/text extensions). Use e.g. '.py,.js' or empty for none")
    p.add_argument("--all", action='store_true', help="Include all text files regardless of extension (skips binary)")
    p.add_argument("--skip-dirs", default=','.join(sorted(DEFAULT_SKIP_DIRS)), help="Comma-separated directories to skip (default: common dirs)")
    p.add_argument("--max-size", type=int, default=5*1024*1024, help="Maximum file size in bytes to include (default: 5MB)")
    return p.parse_args()


def main():
    args = parse_args()
    root = Path(args.root).resolve()
    out = Path(args.output).resolve()
    include_all = args.all
    include_exts = None if include_all else {ext.strip().lower() for ext in args.ext.split(',') if ext.strip()}
    skip_dirs = {d.strip() for d in args.skip_dirs.split(',') if d.strip()}

    print(f"Scanning {root} (include_all={include_all})...")
    files = gather_files(root, include_exts, skip_dirs, include_all, args.max_size, out)
    print(f"Found {len(files)} files to include.")
    if not files:
        print("No files to write. Exiting.")
        return 1
    print(f"Writing to {out} ...")
    written = write_output(files, root, out)
    print(f"Done. Wrote {written} files into {out}.")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())