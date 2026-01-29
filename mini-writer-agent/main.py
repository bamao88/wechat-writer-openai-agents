"""
Mini Writer Agent - 业务执行入口
"""
import os
from dotenv import load_dotenv
from agent import WriterAgent

# 加载环境变量
load_dotenv()


def main():
    """主执行函数"""
    print("=" * 50)
    print("Mini Writer Agent 启动")
    print("=" * 50)
    
    # 初始化 Agent
    agent = WriterAgent()
    
    # 示例：执行写作任务
    topic = input("请输入写作主题: ").strip()
    if not topic:
        topic = "AI 技术趋势"
    
    print(f"\n开始生成关于「{topic}」的文章...\n")
    
    # 执行 Agent 任务
    result = agent.run(topic=topic)
    
    print("\n" + "=" * 50)
    print("生成完成!")
    print("=" * 50)
    print(result)


if __name__ == "__main__":
    main()
