"""
Mini Writer Agent - Agent 大脑逻辑
"""
import os
from openai import OpenAI
from tools import search_materials, save_article


class WriterAgent:
    """写作 Agent 核心类"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """你是一个专业的微信公众号写作助手。你的任务是：
1. 根据用户提供的主题，搜索相关背景资料
2. 整合资料，生成高质量的文章
3. 确保文章符合微信公众号的写作风格

写作风格要求：
- 标题吸引人，有阅读欲望
- 开头引人入胜，抓住读者注意力
- 内容有深度，提供真正有价值的信息
- 结尾有力，给读者留下思考空间
- 适当使用小标题分段，便于阅读
"""

    def run(self, topic: str) -> str:
        """执行写作任务"""
        # Step 1: 搜索背景资料
        print("[Agent] 正在搜索背景资料...")
        materials = search_materials(topic)
        
        # Step 2: 生成文章
        print("[Agent] 正在生成文章...")
        article = self._generate_article(topic, materials)
        
        # Step 3: 保存文章
        print("[Agent] 正在保存文章...")
        filepath = save_article(topic, article)
        print(f"[Agent] 文章已保存至: {filepath}")
        
        return article
    
    def _generate_article(self, topic: str, materials: str) -> str:
        """调用 LLM 生成文章"""
        user_prompt = f"""请根据以下主题和背景资料，生成一篇微信公众号文章。

主题：{topic}

背景资料：
{materials}

请生成文章："""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
