"""
Mini Writer Agent - 工具单元测试
"""
import os
import sys
import pytest

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import search_materials, save_article, update_state
from notebooklm_tool import search_notebooklm, _mock_search


class TestNotebookLMTool:
    """NotebookLM 工具测试"""
    
    def test_mock_search_returns_string(self):
        """测试模拟搜索返回字符串"""
        result = _mock_search("测试主题")
        assert isinstance(result, str)
        assert "测试主题" in result
    
    def test_search_notebooklm_without_api_key(self):
        """测试无 API Key 时的搜索"""
        # 临时移除 API Key
        original_key = os.environ.pop("NOTEBOOKLM_API_KEY", None)
        
        try:
            result = search_notebooklm("AI 技术")
            assert isinstance(result, str)
            assert len(result) > 0
        finally:
            # 恢复 API Key
            if original_key:
                os.environ["NOTEBOOKLM_API_KEY"] = original_key


class TestTools:
    """工具函数测试"""
    
    def test_search_materials(self):
        """测试搜索资料"""
        result = search_materials("Python 编程")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_save_article(self, tmp_path):
        """测试保存文章"""
        # 设置临时输出目录
        os.environ["OUTPUT_DIR"] = str(tmp_path)
        
        topic = "测试文章"
        content = "这是测试内容"
        
        filepath = save_article(topic, content)
        
        assert os.path.exists(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            saved_content = f.read()
        assert topic in saved_content
        assert content in saved_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
