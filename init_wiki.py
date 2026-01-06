"""
Initialize GitHub Wiki by creating the first page via API.
GitHub wikis must be initialized before they can be cloned/pushed to.
"""

import subprocess
import json
import os

def get_github_token():
    """Get GitHub token from gh CLI config."""
    try:
        result = subprocess.run(
            ['gh', 'auth', 'token'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def create_initial_wiki_page():
    """Create initial wiki page using gh CLI."""
    # The GitHub API doesn't support direct wiki creation
    # We need to use gh to open the wiki creation page
    print("GitHub Wiki needs to be initialized via web interface.")
    print("\nOpening wiki creation page...")

    subprocess.run([
        'gh', 'browse', '-n',
        'https://github.com/Digital-AI-Finance/Narrative-Digital-Finance/wiki/_new'
    ])

    print("\nPlease create the first wiki page manually in your browser.")
    print("After creating the first page, run the following command to push all wiki content:")
    print("\n  cd wiki && git push -u origin master")

def main():
    print("=" * 60)
    print("GitHub Wiki Initialization")
    print("=" * 60)
    print("\nRepository: Digital-AI-Finance/Narrative-Digital-Finance")
    print("\nThe GitHub Wiki needs to be initialized through the web interface.")
    print("\nOptions:")
    print("1. Go to: https://github.com/Digital-AI-Finance/Narrative-Digital-Finance/wiki")
    print("2. Click 'Create the first page'")
    print("3. Add any content and save")
    print("4. Then run: cd wiki && git push -f origin master")
    print("\n" + "=" * 60)

    # Try to open in browser
    try:
        subprocess.run([
            'gh', 'browse',
            'https://github.com/Digital-AI-Finance/Narrative-Digital-Finance/wiki'
        ], check=False)
    except:
        pass

if __name__ == "__main__":
    main()
