"""Sync files under `docs/` into the `nav:` section of mkdocs.yml.

Usage:
	python syncDocs.py [--docs docs] [--mkdocs mkdocs.yml]

This script:
 - scans the `docs` directory for files (recursively)
 - builds a nested nav structure representing folders and files
 - replaces the `nav:` block in `mkdocs.yml` (makes a .bak first)
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from typing import Dict, List, Tuple


def find_all_files(docs_dir: str) -> List[str]:
    out: List[str] = []
    for root, _, files in os.walk(docs_dir):
        rel = os.path.relpath(root, docs_dir)
        for f in files:
            # include all files
            if rel == ".":
                p = f
            else:
                p = os.path.join(rel, f)
            out.append(p.replace("\\", "/"))
    return sorted(out)


def add_to_tree(tree: Dict, parts: List[str], path: str) -> None:
	node = tree
	for part in parts[:-1]:
		node = node.setdefault(part, {})
	files = node.setdefault("__files__", [])
	name = os.path.splitext(parts[-1])[0]
	files.append((name, path))


def build_tree(paths: List[str]) -> Dict:
	tree: Dict = {}
	for p in paths:
		parts = p.split("/")
		add_to_tree(tree, parts, p)
	return tree


def emit_nav_lines(node: Dict, indent: int = 1) -> List[str]:
	lines: List[str] = []
	spaces = "  " * indent

	# files at this node
	files: List[Tuple[str, str]] = sorted(node.get("__files__", []), key=lambda x: x[0].lower())
	for name, path in files:
		lines.append(f"{spaces}- {name}: {path}")

	# subdirectories
	subdirs = sorted([k for k in node.keys() if k != "__files__"], key=lambda x: x.lower())
	for sub in subdirs:
		subnode = node[sub]
		sub_files = subnode.get("__files__", [])
		sub_subdirs = [k for k in subnode.keys() if k != "__files__"]

		# if single file and no subdirs, emit as mapping to the file
		if len(sub_subdirs) == 0 and len(sub_files) == 1:
			name, path = sorted(sub_files, key=lambda x: x[0])[0]
			lines.append(f"{spaces}- {sub}: {path}")
		else:
			lines.append(f"{spaces}- {sub}:")
			lines.extend(emit_nav_lines(subnode, indent + 1))

	return lines


def update_mkdocs(mkdocs_path: str, nav_block_lines: List[str]) -> None:
	with open(mkdocs_path, "r", encoding="utf-8") as f:
		content = f.readlines()

	# find nav: line
	nav_idx = None
	for i, line in enumerate(content):
		if line.strip().startswith("nav:"):
			nav_idx = i
			break

	if nav_idx is None:
		# append nav at end
		before = content
		after = []
	else:
		before = content[:nav_idx]
		# find end: next top-level key (line starting at column 0 and not blank)
		end_idx = None
		for j in range(nav_idx + 1, len(content)):
			if content[j].strip() == "":
				continue
			if content[j][0] not in (" ", "\t"):
				end_idx = j
				break
		if end_idx is None:
			after = []
		else:
			after = content[end_idx:]

	new_nav = ["nav:\n"] + [l + "\n" for l in nav_block_lines]

	backup = mkdocs_path + ".bak"
	shutil.copyfile(mkdocs_path, backup)

	with open(mkdocs_path, "w", encoding="utf-8") as f:
		f.writelines(before)
		f.writelines(new_nav)
		f.writelines(after)


def main(argv: List[str]) -> int:
	p = argparse.ArgumentParser(description="Sync docs/ into mkdocs.yml nav")
	p.add_argument("--docs", default="docs", help="Path to docs directory")
	p.add_argument("--mkdocs", default="mkdocs.yml", help="Path to mkdocs.yml")
	args = p.parse_args(argv)

	docs_dir = args.docs
	mkdocs_path = args.mkdocs

	if not os.path.isdir(docs_dir):
		print(f"docs directory not found: {docs_dir}")
		return 2
	if not os.path.isfile(mkdocs_path):
		print(f"mkdocs.yml not found: {mkdocs_path}")
		return 2

	files = find_all_files(docs_dir)
	tree = build_tree(files)
	nav_lines = emit_nav_lines(tree, indent=1)
	update_mkdocs(mkdocs_path, nav_lines)

	print(f"Updated {mkdocs_path} (backup at {mkdocs_path}.bak)")
	return 0


if __name__ == "__main__":
	raise SystemExit(main(sys.argv[1:]))
