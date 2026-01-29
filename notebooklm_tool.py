"""NotebookLM search tool using PleasePrompto/notebooklm-skill.

This module integrates the notebooklm-skill to query NotebookLM notebooks
for source-grounded answers.

Requires:
    - notebooklm_skill/ directory (cloned from GitHub)
    - Google authentication (one-time setup)
"""

import os
import sys
import subprocess
from pathlib import Path

# Path to notebooklm_skill
NOTEBOOKLM_SKILL_PATH = Path(__file__).parent / "notebooklm_skill" / "scripts"
NOTEBOOKLM_SKILL_ROOT = Path(__file__).parent / "notebooklm_skill"

# Use notebooklm_skill's own virtual environment Python
NOTEBOOKLM_PYTHON = NOTEBOOKLM_SKILL_ROOT / ".venv" / "bin" / "python"

if str(NOTEBOOKLM_SKILL_PATH) not in sys.path:
    sys.path.insert(0, str(NOTEBOOKLM_SKILL_PATH))


def _get_notebook_url() -> str:
    """Get NotebookLM notebook URL from environment.

    Returns:
        Notebook URL string.
    """
    # Try to get from environment
    url = os.getenv("NOTEBOOK_URL")
    if url:
        return url

    # Try to construct from NOTEBOOK_ID
    notebook_id = os.getenv("NOTEBOOK_ID")
    if notebook_id:
        return f"https://notebooklm.google.com/notebook/{notebook_id}"

    # Default fallback
    return "https://notebooklm.google.com"


def _check_authenticated() -> bool:
    """Check if NotebookLM authentication is set up.

    Returns:
        True if authenticated, False otherwise.
    """
    try:
        result = subprocess.run(
            [str(NOTEBOOKLM_PYTHON), str(NOTEBOOKLM_SKILL_PATH / "run.py"), "auth_manager.py", "status"],
            capture_output=True,
            text=True,
            cwd=NOTEBOOKLM_SKILL_PATH.parent,
        )
        # Check for "Authenticated: Yes" pattern, not just "authenticated"
        # Output format: "Authenticated: Yes" or "Authenticated: No"
        stdout_lower = result.stdout.lower()
        return result.returncode == 0 and "authenticated: yes" in stdout_lower
    except Exception:
        return False


async def run_search(query: str) -> str:
    """Search for information using NotebookLM skill.

    Args:
        query: The search query string.

    Returns:
        Search results as a string from NotebookLM.
        Returns error message if not authenticated or request fails.
    """
    if not query:
        return "No results found for empty query."

    # Check if notebooklm_skill exists
    if not NOTEBOOKLM_SKILL_PATH.exists():
        return (
            "Error: notebooklm_skill not found. "
            "Please clone https://github.com/PleasePrompto/notebooklm-skill to notebooklm_skill/"
        )

    # Check authentication
    if not _check_authenticated():
        return (
            "Error: NotebookLM not authenticated. "
            f"Please run: cd {NOTEBOOKLM_SKILL_PATH.parent} && python scripts/run.py auth_manager.py setup"
        )

    notebook_url = _get_notebook_url()

    try:
        # Run the ask_question.py script via run.py wrapper
        # Use notebooklm_skill's own venv Python to ensure correct dependencies
        result = subprocess.run(
            [
                str(NOTEBOOKLM_PYTHON),
                str(NOTEBOOKLM_SKILL_PATH / "run.py"),
                "ask_question.py",
                "--question", query,
                "--notebook-url", notebook_url,
            ],
            capture_output=True,
            text=True,
            cwd=NOTEBOOKLM_SKILL_PATH.parent,
            timeout=300,  # 5 minutes timeout
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return f"Search failed for '{query}': {error_msg}"

        # Return stdout which contains the answer
        output = result.stdout.strip()
        if output:
            return f"Search results for '{query}':\n{output}"
        else:
            return f"No results found for '{query}'"

    except subprocess.TimeoutExpired:
        return f"Search timeout for '{query}' - took too long to respond"
    except Exception as e:
        return f"Error searching for '{query}': {str(e)}"


def setup_authentication():
    """Run NotebookLM authentication setup.

    This is a one-time setup that opens a browser for Google login.
    """
    if not NOTEBOOKLM_SKILL_PATH.exists():
        print("Error: notebooklm_skill not found.")
        print("Please clone: git clone https://github.com/PleasePrompto/notebooklm-skill.git notebooklm_skill")
        return False

    print("Setting up NotebookLM authentication...")
    print("A browser window will open for Google login.")
    print("")

    try:
        result = subprocess.run(
            [str(NOTEBOOKLM_PYTHON), str(NOTEBOOKLM_SKILL_PATH / "run.py"), "auth_manager.py", "setup"],
            cwd=NOTEBOOKLM_SKILL_PATH.parent,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Setup failed: {e}")
        return False


def list_notebooks():
    """List all notebooks in the library."""
    try:
        result = subprocess.run(
            [str(NOTEBOOKLM_PYTHON), str(NOTEBOOKLM_SKILL_PATH / "run.py"), "notebook_manager.py", "list"],
            capture_output=True,
            text=True,
            cwd=NOTEBOOKLM_SKILL_PATH.parent,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except Exception as e:
        print(f"Error listing notebooks: {e}")


if __name__ == "__main__":
    # Quick test
    import asyncio

    # Check auth first
    if not _check_authenticated():
        print("Not authenticated. Running setup...")
        setup_authentication()
    else:
        # Test search
        test_query = "What is the main topic of this notebook?"
        print(f"Testing search: {test_query}")
        result = asyncio.run(run_search(test_query))
        print(result)
