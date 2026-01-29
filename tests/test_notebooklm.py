"""Test NotebookLM search tool using PleasePrompto/notebooklm-skill."""

import pytest
from unittest.mock import patch, MagicMock
import subprocess


def test_run_search_exists():
    """Verify run_search function exists."""
    from notebooklm_tool import run_search
    assert callable(run_search)


@pytest.mark.asyncio
@patch('notebooklm_tool._check_authenticated')
@patch('notebooklm_tool.NOTEBOOKLM_SKILL_PATH')
async def test_run_search_returns_string(mock_path, mock_auth):
    """Verify run_search returns a string result."""
    from notebooklm_tool import run_search

    mock_auth.return_value = True
    mock_path.exists.return_value = True
    mock_path.__truediv__ = MagicMock(return_value=mock_path)
    mock_path.__str__ = MagicMock(return_value='/fake/path/run.py')
    mock_path.parent = '/fake'

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Test answer from NotebookLM"
    mock_result.stderr = ""

    with patch('subprocess.run', return_value=mock_result):
        result = await run_search("test query")
        assert isinstance(result, str)
        assert "test query" in result


@pytest.mark.asyncio
async def test_run_search_skill_not_found():
    """Verify run_search handles missing skill directory."""
    from notebooklm_tool import run_search

    with patch('notebooklm_tool.NOTEBOOKLM_SKILL_PATH') as mock_path:
        mock_path.exists.return_value = False
        mock_path.__str__ = MagicMock(return_value='/fake/path')

        result = await run_search("test query")
        assert isinstance(result, str)
        assert "not found" in result.lower()


@pytest.mark.asyncio
@patch('notebooklm_tool._check_authenticated')
async def test_run_search_not_authenticated(mock_auth):
    """Verify run_search handles unauthenticated state."""
    from notebooklm_tool import run_search

    mock_auth.return_value = False

    with patch('notebooklm_tool.NOTEBOOKLM_SKILL_PATH') as mock_path:
        mock_path.exists.return_value = True
        mock_path.__str__ = MagicMock(return_value='/fake/path')
        mock_path.parent = '/fake'

        result = await run_search("test query")
        assert isinstance(result, str)
        assert "not authenticated" in result.lower()


@pytest.mark.asyncio
@patch('notebooklm_tool._check_authenticated')
async def test_run_search_empty_query(mock_auth):
    """Verify run_search handles empty query."""
    from notebooklm_tool import run_search

    result = await run_search("")
    assert isinstance(result, str)
    assert "empty" in result.lower() or "no results" in result.lower()


@pytest.mark.asyncio
@patch('notebooklm_tool._check_authenticated')
@patch('notebooklm_tool.NOTEBOOKLM_SKILL_PATH')
async def test_run_search_command_fails(mock_path, mock_auth):
    """Verify run_search handles command failure."""
    from notebooklm_tool import run_search

    mock_auth.return_value = True
    mock_path.exists.return_value = True
    mock_path.__truediv__ = MagicMock(return_value=mock_path)
    mock_path.__str__ = MagicMock(return_value='/fake/path/run.py')
    mock_path.parent = '/fake'

    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Error: something went wrong"

    with patch('subprocess.run', return_value=mock_result):
        result = await run_search("test query")
        assert isinstance(result, str)
        assert "failed" in result.lower()


def test_check_authenticated_exists():
    """Verify _check_authenticated function exists."""
    from notebooklm_tool import _check_authenticated
    assert callable(_check_authenticated)


def test_get_notebook_url():
    """Verify _get_notebook_url reads from environment."""
    from notebooklm_tool import _get_notebook_url

    with patch.dict('os.environ', {'NOTEBOOK_URL': 'https://test.notebooklm.com'}):
        url = _get_notebook_url()
        assert url == 'https://test.notebooklm.com'

    with patch.dict('os.environ', {'NOTEBOOK_ID': 'abc123'}, clear=True):
        url = _get_notebook_url()
        assert 'abc123' in url


def test_setup_authentication_exists():
    """Verify setup_authentication function exists."""
    from notebooklm_tool import setup_authentication
    assert callable(setup_authentication)


def test_list_notebooks_exists():
    """Verify list_notebooks function exists."""
    from notebooklm_tool import list_notebooks
    assert callable(list_notebooks)
