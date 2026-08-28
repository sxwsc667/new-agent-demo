# streamlit_app.py - Streamlit 聊天界面
# 作用：在浏览器中驱动底层 ReAct 智能体（核心复用 demo.web_demo.run_agent，不依赖 gradio）

import sys
from pathlib import Path

# 将项目根目录加入 Python 路径（保证能 import 到顶层模块）
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

# 导入核心智能体运行函数
from demo.web_demo import run_agent

# ========== Streamlit 页面配置 ==========
st.set_page_config(page_title="new-agent 智能体", page_icon="🧠", layout="centered")
st.title("🧠 new-agent 智能体")
st.caption("基于 ReAct 架构的多工具智能体 | 推理 + 工具调用")

# ========== 初始化聊天历史（用于界面展示） ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

# ========== 显示历史消息 ==========
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ========== 处理用户输入 ==========
if prompt := st.chat_input("请输入您的问题（例如：你好、查天气）"):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用智能体（历史由 box 自动维护，session_state 仅作界面展示）
    with st.chat_message("assistant"):
        with st.spinner("🤔 智能体思考中..."):
            response = run_agent(prompt, st.session_state.messages)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})