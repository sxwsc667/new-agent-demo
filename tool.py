from box import box
from tools.tool_list import 工具调用映射表
import json
import tools.tool_box as tool_box



def 工具判断():
    if box["回复消息"]["tool_calls"]:
        box["是否调用工具"] = True
    else:
        box["是否调用工具"] = False






def 工具调用执行():
    box["工具调用结果"] = []
    
    for 单个调用 in box["调用工具"]:
        tool_id = 单个调用["id"]
        工具名称 = 单个调用["function"]["name"]
        # 把arguments 转成字典
        工具参数字典 = json.loads(单个调用["function"]["arguments"])
        # 调用你的本地函数
        tool = 工具调用映射表[工具名称]
        result = tool(**工具参数字典)

        # 把工具执行结果追加到 box["工具调用结果"] 中
        box["工具调用结果"].append({
            "role": "tool",
            "tool_call_id": tool_id,
            "content": json.dumps(result)  # 结果必须转成字符串
        })
