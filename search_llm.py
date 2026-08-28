# LLM 工具模块
# 功能：统一管理所有 LLM 调用，支持灵活模型切换

from typing import Dict, Callable
import json
import sys
from api import (
    deepseek_chat,
    SiliconFlow_chat,
    lumiya_chat,
    CC_switch_chat
)

# ==================== 模型映射 ====================
模型映射表 = {
    "deepseek": deepseek_chat,
    "Qwen4b": SiliconFlow_chat,
    "lumiya": lumiya_chat,
    "CC_switch": CC_switch_chat,
}

def get_llm_name(model_name: str) -> Callable:
    """
    根据模型名称返回对应 LLM 函数
    model_name 示例：deepseek, Qwen4b, lumiya
    """
    model = model_name.strip()
    return 模型映射表[model]


# ==================== 统一调用函数 ====================
def call_llm(model_name="Qwen4b", **kwargs) -> dict:
    """
    通用 LLM 调用函数
    model_name: 模型名称（small english）
    stream: 是否流式输出
    kwargs: 传递给具体函数的参数
    """
    llm_name = get_llm_name(model_name)
    result = llm_name(**kwargs)
    return result

# ==================== 示例使用 ====================
if __name__ == "__main__":
    # 测试调用
    result = call_llm("lumiya", 流式=False)
    print(result)
