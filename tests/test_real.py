"""
End-to-end real API integration tests.
Requires real API keys to run.
"""
import os
import sys
import pytest
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()


# Skip markers for tests requiring real APIs
requires_minimax = pytest.mark.skipif(
    not os.getenv("MINIMAX_API_KEY") or os.getenv("MINIMAX_API_KEY").startswith("your_"),
    reason="Requires real MINIMAX_API_KEY"
)

requires_notebooklm = pytest.mark.skipif(
    not os.getenv("NOTEBOOKLM_API_KEY") or os.getenv("NOTEBOOKLM_API_KEY").startswith("your_"),
    reason="Requires real NOTEBOOKLM_API_KEY"
)


class TestRealIntegration:
    """Real environment integration tests"""

    @requires_minimax
    @pytest.mark.asyncio
    async def test_minimax_connection(self):
        """Test MiniMax API connection through Agent"""
        from agent import create_agent, run_agent

        agent = create_agent(trace_id="test_real_minimax")
        result = await run_agent(agent, "Say 'Hello from MiniMax' and nothing else.")

        assert result is not None
        assert result.final_output is not None
        assert isinstance(result.final_output, str)
        assert len(result.final_output) > 0

    @requires_minimax
    @pytest.mark.asyncio
    async def test_agent_with_tools_real_api(self):
        """Test Agent with tools using real MiniMax API"""
        from agent import create_agent_with_tools, run_agent

        agent = create_agent_with_tools(trace_id="test_tools_real")

        # Prompt that should trigger tool use
        prompt = "Search for information about Python programming and summarize it"

        result = await run_agent(agent, prompt)

        assert result is not None
        assert result.final_output is not None
        assert isinstance(result.final_output, str)

    @pytest.mark.asyncio
    async def test_notebooklm_search_mock(self):
        """Test NotebookLM search (mock mode without real API)"""
        from notebooklm_tool import run_search

        # This will use the mock implementation
        result = await run_search("artificial intelligence")

        assert isinstance(result, str)
        # Should contain error message since no real API is configured
        assert "error" in result.lower() or "failed" in result.lower() or "search results" in result.lower()

    @requires_minimax
    @pytest.mark.asyncio
    async def test_full_workflow(self, tmp_path):
        """Test complete workflow with real APIs"""
        from main import run_workflow

        # Set temporary output directory
        os.environ["OUTPUT_DIR"] = str(tmp_path)

        result = await run_workflow("Python programming basics")

        assert result is not None
        assert "topic" in result
        assert "content" in result
        assert "trace_id" in result
        assert "output_path" in result

        # Verify file was created
        assert os.path.exists(result["output_path"])

        # Verify content was written
        with open(result["output_path"], "r", encoding="utf-8") as f:
            content = f.read()
            assert result["topic"] in content
            assert result["trace_id"] in content

    @requires_minimax
    @pytest.mark.asyncio
    async def test_trace_report_generation(self, tmp_path):
        """Test that trace report is generated with proper format"""
        from main import run_workflow

        os.environ["OUTPUT_DIR"] = str(tmp_path)

        result = await run_workflow("AI technology")

        # Verify trace_id format
        trace_id = result["trace_id"]
        assert trace_id.startswith("trace_")
        parts = trace_id.split("_")
        assert len(parts) == 4  # trace_YYYYMMDD_HHMMSS_uuid

        # Verify output file contains trace info
        with open(result["output_path"], "r", encoding="utf-8") as f:
            content = f.read()
            assert f"**Trace ID:** {trace_id}" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
