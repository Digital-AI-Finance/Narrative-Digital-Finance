"""
Push wiki content to GitHub Wiki.
Run this AFTER manually creating the first wiki page on GitHub.

Instructions:
1. Go to: https://github.com/Digital-AI-Finance/Narrative-Digital-Finance/wiki
2. Click "Create the first page"
3. Add title "Home" and any content
4. Click "Save Page"
5. Run this script: python push_wiki.py
"""

import os
import shutil
import subprocess
from pathlib import Path

REPO = "Digital-AI-Finance/Narrative-Digital-Finance"
BASE_DIR = Path(__file__).parent
WIKI_CONTENT_DIR = BASE_DIR / "wiki_content"
WIKI_CLONE_DIR = BASE_DIR / "wiki_clone"


def main():
    print("=" * 60)
    print("Push Wiki Content to GitHub")
    print("=" * 60)
    print(f"\nRepository: {REPO}")

    # Remove existing clone if exists
    if WIKI_CLONE_DIR.exists():
        print(f"\nRemoving existing clone: {WIKI_CLONE_DIR}")
        shutil.rmtree(WIKI_CLONE_DIR)

    # Clone wiki repo
    print(f"\nCloning wiki repository...")
    wiki_url = f"https://github.com/{REPO}.wiki.git"

    try:
        result = subprocess.run(
            ["git", "clone", wiki_url, str(WIKI_CLONE_DIR)],
            capture_output=True,
            text=True,
            check=True
        )
        print("Wiki cloned successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\nError: Could not clone wiki: {e.stderr}")
        print("\nPlease ensure you have:")
        print("1. Created the first wiki page at:")
        print(f"   https://github.com/{REPO}/wiki")
        print("2. Saved the page")
        print("\nThen run this script again.")
        return

    # Copy wiki content
    print(f"\nCopying wiki content...")
    for md_file in WIKI_CONTENT_DIR.glob("*.md"):
        dest = WIKI_CLONE_DIR / md_file.name
        shutil.copy(md_file, dest)
        print(f"  Copied: {md_file.name}")

    # Also copy from docs/ folder if applicable
    docs_dir = BASE_DIR / "repo" / "docs"
    if docs_dir.exists():
        mapping = {
            "objectives.md": "Research-Objectives.md",
            "team.md": "Team.md",
            "funding.md": "Funding.md"
        }
        for src_name, dest_name in mapping.items():
            src = docs_dir / src_name
            if src.exists():
                dest = WIKI_CLONE_DIR / dest_name
                shutil.copy(src, dest)
                print(f"  Copied: {src_name} -> {dest_name}")

    # Git add, commit, and push
    print(f"\nCommitting and pushing...")
    os.chdir(WIKI_CLONE_DIR)

    subprocess.run(["git", "add", "-A"], check=True)

    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True
    )

    if result.stdout.strip():
        subprocess.run(
            ["git", "commit", "-m", "Update wiki with full project documentation"],
            check=True
        )
        subprocess.run(["git", "push"], check=True)
        print("\nWiki updated successfully!")
    else:
        print("\nNo changes to commit.")

    print(f"\nView wiki at: https://github.com/{REPO}/wiki")


if __name__ == "__main__":
    main()
