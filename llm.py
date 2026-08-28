from search_llm import get_llm_name
from box import box
import api 
import memery
from tools.tool_list import tool_list
# 调用模型,传入消息和工具列表

def 输入消息拼接():
    # 先做上下文压缩：达到 10 轮时，把最老的 5 轮压成摘要、替换其位置，避免历史无限膨胀
    memery.上下文压缩()
    # 把人话历史拼接好，供本轮发送给模型：
    # 1) 上轮整理好的 assistant 回复（含 content 和 tool_calls 字段）
    # 2) 上轮工具执行结果（tool 消息）
    if box["最终回复"]:
        box["消息"].append(box["最终回复"])
    if box["工具调用结果"]:
        box["消息"].extend(box["工具调用结果"])
    box["可用工具"] = tool_list

def use_llm():
    
    message = box["消息"]
    tools = box["可用工具"]
    name = get_llm_name(box["主模型"])
    # 位置传参：函数签名已是 (消息历史, 可用工具, 流式=True)，message→消息历史、tools→可用工具 正好对应
    box["回复消息"] = name(message, tools)

def 返回消息处理():
    # 从模型回复中剪出 content，若有工具调用再带上 tool_calls，组装成完整 assistant 消息放进最终回复，
    # 供下一次 输入消息拼接() 追加进消息历史
    最终回复 = {
        "role": "assistant",
        "content": box["回复消息"]["content"]
    }
    # 仅当模型本轮发起了工具调用时，才携带 tool_calls 字段；不调工具则不写该字段
    if box["回复消息"]["tool_calls"]:
        最终回复["tool_calls"] = box["回复消息"]["tool_calls"]
    # DeepSeek thinking 模式要求：继续对话时，assistant 消息须连同本轮 reasoning_content 一并回传，否则 400
    if box["回复消息"]["reasoning_content"]:
        最终回复["reasoning_content"] = box["回复消息"]["reasoning_content"]
    box["最终回复"] = 最终回复   

def 工具调用写入():
    box["调用工具"]=box["回复消息"]["tool_calls"]
    print(box["调用工具"])










if __name__ == "__main__":
    use_llm()
