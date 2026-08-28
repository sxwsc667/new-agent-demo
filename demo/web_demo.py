# demo/web_demo.py - 智能体演示外壳
# 作用：提供核心 run_agent 运行函数；可选附带 Gradio 演示界面（已改为可选依赖，不装 gradio 也能正常 import）

import sys
import importlib.util
from pathlib import Path

# 将项目根目录加入 Python 路径（保证能 import 到顶层模块）
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# gradio 为可选依赖：仅用于内置浏览器演示；核心 run_agent 不依赖它
HAS_GRADIO = importlib.util.find_spec("gradio") is not None
if HAS_GRADIO:
    import gradio as gr

# ========== 导入核心模块 ==========
from box import box
from hooks import (
    会话开始, 模型调用前, use_model, 模型调用后,
    工具调用前, use_tool, 工具调用后, 工具循环结束,
)

# ========== 智能体运行函数 ==========
def run_agent(user_message, history):
    """
    运行一轮 ReAct 循环，返回最终回复文本。

    设计说明：历史与系统提示都不在这里手写。
    - 系统提示：首次调用时由 会话开始 一次性初始化（对应终端 chat.py 的对话起点）；
    - 历史累积：由钩子的 输入消息拼接 + 返回消息处理 自动维护（box 跨轮常驻，同终端逻辑）；
    - 这里只需要注入当前用户消息，再跑一遍内层工具循环即可。
    """
    # 首次调用：初始化系统提示（box["消息"] 为空时执行，只做一次）
    if not box["消息"]:
        会话开始()
        # ★★★ 主模型必须是 search_llm.py 中"模型映射表"里的一个 key ★★★
        box["主模型"] = "deepseek"  # 千问 4B，价格更便宜

    # 写入当前用户消息（钩子的 用户输入 依赖终端 input()，Gradio 场景改为手动追加）
    box["消息"].append({"role": "user", "content": user_message})

    # ReAct 内层循环：模型可能连续多次请求工具，直到给出最终答案
    max_tool_rounds = 10
    tool_round = 0
    try:
        while tool_round < max_tool_rounds and not box["结束会话"]:
            模型调用前()
            use_model()
            模型调用后()

            if box["是否调用工具"]:
                工具调用前()
                use_tool()
                工具调用后()
                tool_round += 1
            else:
                break

        工具循环结束()

        # 从 box 中取出最终回复文本
        最终回复 = box.get("最终回复") or box.get("回复消息") or {}
        if isinstance(最终回复, dict):
            return 最终回复.get("content") or "（模型未返回有效内容）"
        return "（未返回有效回复）"

    except Exception as e:
        return f"❌ 错误：{str(e)}"


# ========== Gradio 演示界面（可选：仅当安装了 gradio 才提供） ==========
if HAS_GRADIO:

    def chat_with_agent(message, history):
        """Gradio 回调：过滤空消息与退出指令后交给 run_agent。"""
        if not message or not message.strip():
            return "请输入有效消息"
        if message.strip() in ["退出", "111"]:
            return "👋 会话结束"
        return run_agent(message, history)

    demo = gr.ChatInterface(
        fn=chat_with_agent,
        title="🧠 智能体演示",
        description="基于 ReAct 架构的多工具智能体 | 支持 DeepSeek 推理 + 工具调用",
        examples=[
            ["你好，请介绍一下你自己"],
            ["帮我查一下杭州的天气"],
            ["你支持哪些工具？"],
        ],
    )

    if __name__ == "__main__":
        demo.launch(share=True, server_name="0.0.0.0", server_port=7860)