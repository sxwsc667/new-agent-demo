from openai import OpenAI
import os
import sys
import json
import httpx
from box import box

'''
将标准输出设为 UTF-8，避免 Windows 控制台 GBK 编码打印 emoji 时报错
不建议装进某个业务函数（比如 流式输出显示 ） 。
原因是它改的是「进程级全局」的 stdout 编码，
是"启动时设一次、全程生效"的配置
它的正确归属是 入口 ：
现在 api.py 本身就是入口，放模块顶层没问题。
以后不在这个文件运行时，应该挪到入口文件。
'''
sys.stdout.reconfigure(encoding="utf-8")



# 显示流式输出，实时打印，返回数据块列表
def _流式输出显示(response):
    # ---------- 临时控制台打印,后续换成前端的方法 ----------
    reasoning_content = "" # 存储思考过程
    content = ""           # 存储回答内容
    tool_calls = []
    数据块列表 = []  # 收集数据块，返回给解析函数复用，避免流被读两遍
    
    is_reasoning = True  
    print("\n\n" + "="*30 + " 思考开始 " + "="*30 + "\n\n", end="", flush=True)
    for i in response:
        if not i.choices:
            continue
        chunk = i.choices[0].delta
        数据块列表.append(i)  # 顺手收集本次数据块
        

        if  hasattr(chunk, 'reasoning_content') and chunk.reasoning_content:
            
            reasoning_content += chunk.reasoning_content
            print(chunk.reasoning_content, end="", flush=True)

        if hasattr(chunk, 'content') and chunk.content:
            # 2. 如果正在思考中，且现在开始输出 content，说明思考刚结束
            if is_reasoning:
                # 在这里插入你想要的任何分隔符（这里用空行 + 分割线）
                print("\n\n" + "="*30 + " 思考结束 " + "="*30 + "\n\n", end="", flush=True)
                is_reasoning = False  # 标记已经切换过了，防止多次插入

            content += chunk.content
            print(chunk.content, end="", flush=True)

    return 数据块列表  # 返回收集的数据块，供解析函数复用 


# 把流式输出内容拼装成完整字典，数据列表会消失，只能解析一次
def _流式输出解析(response):
    # ---------- 流式累积和词典拼装 ----------
    # 用于存放回答内容
    content_parts = []
    # 用于存放思维链
    reasoning_parts = []
    # 用于按索引合并工具调用
    #范例:
    #  {
    #     "id": "call_9c8a7b6d5e4f3g2h1i0j",
    #     "type": "function",
    #     "function": {
    #         "name": "get_weather",
    #         "arguments": '{"city": "北京", "unit": "celsius"}'
    #     }
    # }
    tool_calls_dict = {}

    # ---------- 遍历流式数据块 ----------
    for chunk in response:
        # 某些数据块可能没有 choices（如空包），直接跳过
        if not chunk.choices:
            continue
    
        # 提取当前数据块中的增量对象（delta）
        # delta 包含本次新增的内容（可能是普通文本、推理内容或工具调用片段）
        delta = chunk.choices[0].delta

        # ----- 1. 累积回答内容 -----
        # 检查 delta 是否有 content 字段，并且不为 None
        if hasattr(delta, 'content') and delta.content is not None:
            # 将本次新增的文本片段追加到列表中
            content_parts.append(delta.content)
            
        # ----- 2. 累积推理内容 -----
        if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
            # 将本次新增的推理片段追加到列表中
            reasoning_parts.append(delta.reasoning_content)
        
        # ----- 3. 累积工具调用 -----
        # 按索引（index）合并各个部分
        if hasattr(delta, 'tool_calls') and delta.tool_calls:
            # 遍历当前数据块中的所有工具调用增量（可能多个）
            for tool_call_delta in delta.tool_calls:
                # 获取该工具调用的索引（用于区分不同工具调用）
                idx = tool_call_delta.index
                
                # 如果该索引尚未在字典中初始化，则创建一个空结构
                if idx not in tool_calls_dict:
                    tool_calls_dict[idx] = {
                        "id": "",                     # 工具调用 ID（在第一个分块中出现）
                        "type": "function",           # 固定为 "function"
                        "function": {
                            "name": "",               # 工具名称
                            "arguments": ""           # 工具参数（JSON 字符串，可能分块拼接）
                        }
                    }
                    
                # 更新 id（通常只有第一个包含 tool_calls 的数据块会携带 id）
                if tool_call_delta.id:
                    tool_calls_dict[idx]["id"] = tool_call_delta.id
                    
                # 更新 function 子对象
                if tool_call_delta.function:
                    # 如果本次有工具名称，则直接覆盖（通常只有第一个分块携带）
                    if tool_call_delta.function.name:
                        tool_calls_dict[idx]["function"]["name"] = tool_call_delta.function.name
                    # 如果本次有参数片段，则拼接到已有的参数字符串后面（因为参数可能分多次传输）
                    if tool_call_delta.function.arguments:
                        tool_calls_dict[idx]["function"]["arguments"] += tool_call_delta.function.arguments
                    
    # ---------- 后处理：工具调用列表排序 ----------
    # 如果确实有工具调用，则按索引升序排列，保证顺序
    if tool_calls_dict:
        # 使用 sorted() 对字典的键排序，然后按顺序提取值，生成列表
        tool_calls_list = [tool_calls_dict[i] for i in sorted(tool_calls_dict.keys())]
    else:
        # 没有工具调用时，设为 None（保持与非流式结构一致）
        tool_calls_list = None
    
    # ---------- 构造最终返回的字典 ----------
    result = {
        "role": "assistant",   # 角色标识,用它来区分用户（"user"）、助手（"assistant"）和工具（"tool"）
        "content": "".join(content_parts) if content_parts else None,#最终回复内容
        "refusal": None,       # 如果模型因为安全策略等原因拒绝回答用户的问题，这里会给出拒绝理由
        # 工具调用列表,当模型决定调用工具时，会包含调用指令，
        # 包括：id：唯一调用 ID（后面执行完工具回传时需要带上）
        # type：固定为 "function(功能OpenAI提前预留的，实际上并没有别的选择)"
        # function：包含 name和 arguments（JSON 格式的参数）        
        "tool_calls": tool_calls_list,   
        "function_call": None, # 旧版函数调用字段，现在已被 tool_calls 取代。保留以兼容
        "audio": None,         # 音频数据,如果模型支持并返回音频，这里会包含音频数据。文本模型不会返回这个
        "annotations": None,   # 某些服务会在答案中附上引文来源或注释，DeepSeek不用
        "reasoning_content": "".join(reasoning_parts) if reasoning_parts else None# 推理内容
        
    }
    return result



# 调用deepseek api,不使用流式输出不打印
# 消息历史：外部传入完整对话（含system），用于多轮对话；不传则用默认单轮示例
def deepseek_chat(消息历史=None, 可用工具=None, 流式=True):
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    if not api_key:
        # 环境变量没有，从 config/api_key.json 读取
        with open("config/api_key.json", "r", encoding="utf-8") as file:
            config = json.load(file)["deepseek"]
            api_key = config.get("DEEPSEEK_API_KEY") or config.get("api_key")
            base_url = config.get("url", "https://api.deepseek.com")

    client = OpenAI(
        api_key=config["DEEPSEEK_API_KEY"],
        base_url=config["url"])

    # 未传入消息历史时，用默认单轮示例（保持原有行为不变）
    messages = 消息历史 if 消息历史 is not None else [
        {"role": "system", "content": "你是大鲸鱼"},
        {"role": "user", "content": "你好"},
    ]

    # reply: 模型回复
    reply = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=messages,
        tools=可用工具,  # 传递工具列表到模型
        stream=流式,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
        
    )

    if 流式:
        数据块列表 = _流式输出显示(reply)  # 流式模式：实时显示并收集数据块
        result = _流式输出解析(数据块列表)  # 流式模式：用收集的数据块解析
    else:
        i = reply.choices[0].message
        result = i.model_dump()  # 非流式模式：直接返回字典
        
    return result


# 调用字节的千问4b模型,不使用流式输出不打印
# 消息历史：外部传入完整对话（含system），用于多轮对话；不传则用默认单轮示例
def SiliconFlow_chat(消息历史=None, 可用工具=None, 流式=True):
    # 从配置文件读取密钥与地址(Load API key and URL from config file)
    with open("config/api_key.json", "r", encoding="utf-8") as file:
        config = json.load(file)["siliconFlow"]  # 键名须与 config/api_key.json 一致（小写 s）

    client = OpenAI(
        api_key=config["SILICONFLOW_API_KEY"],
        base_url=config["url"])

    # 未传入消息历史时，用默认单轮示例（保持原有行为不变）
    messages = 消息历史 if 消息历史 is not None else [
        {"role": "system", "content": """你是一个极速助手，必须要在一秒内给出回答
        以下是你的内部推理流程（仅用于指导思考，绝对不要输出到最终回答中）：
        1. 分析请求：（快速归类）
        2. 确定回应方式：（直接回复）
        3. 草拟回应：（使用最简模板）
        4. 选择最佳选项：（直接采用）
        5. 最终检查：（默认通过）"""},
        {"role": "user", "content": "你好"},
    ]

    # reply: 模型回复
    reply = client.chat.completions.create(
        model="Qwen/Qwen3.5-4B",
        messages=messages,
        tools=可用工具,
        stream=流式,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    if 流式:
        数据块列表 = _流式输出显示(reply)  # 流式模式：实时显示并收集数据块
        result = _流式输出解析(数据块列表)  # 流式模式：用收集的数据块解析
    else:
        i = reply.choices[0].message
        result = i.model_dump()  # 非流式模式：直接返回字典
        
    return result

# 调用露米娅的4.6模型,不使用流式输出不打印,没有推理内容
# 消息历史：外部传入完整对话（含system），用于多轮对话；不传则用默认单轮示例
def lumiya_chat(消息历史=None, 可用工具=None, 流式=True):
    # 从配置文件读取密钥与地址(Load API key and URL from config file)
    with open("config/api_key.json", "r", encoding="utf-8") as file:
        config = json.load(file)["lumiya"]

    client = OpenAI(
        api_key=config["LUMIYA_API_KEY"],
        base_url=config["url"])

    # 未传入消息历史时，用默认单轮示例（保持原有行为不变）
    messages = 消息历史 if 消息历史 is not None else [
        {"role": "system", "content": "你是露米娅"},
        {"role": "user", "content": "你好"},
    ]

    # reply: 模型回复
    reply = client.chat.completions.create(
        model="grok-4.6-high",
        messages=messages,
        tools=可用工具,  # 传递工具列表到模型
        stream=流式,
        #reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    if 流式:
        数据块列表 = _流式输出显示(reply)  # 流式模式：实时显示并收集数据块
        result = _流式输出解析(数据块列表)  # 流式模式：用收集的数据块解析
    else:
        i = reply.choices[0].message
        result = i.model_dump()  # 非流式模式：直接返回字典
        
    return result


# 消息历史：外部传入完整对话（含system），用于多轮对话；不传则用默认单轮示例
def CC_switch_chat(消息历史=None, 可用工具=None, 流式=True):
    # 从配置文件读取密钥与地址(Load API key and URL from config file)
    with open("config/api_key.json", "r", encoding="utf-8") as file:
        config = json.load(file)["agnes"]
     
    client = OpenAI(
        api_key="dummy",  # CC Switch 会忽略，但必须传
        base_url="http://127.0.0.1:15721/v1",  # codex 路由地址
    )

    # 未传入消息历史时，用默认单轮示例（保持原有行为不变）
    messages = 消息历史 if 消息历史 is not None else [
        {"role": "system", "content": "你是agnes"},
        {"role": "user", "content": "你好"},
    ]

    # reply: 模型回复
    reply = client.chat.completions.create(
        model="agnes-2.5-flash",
        messages=messages,
        tools= 可用工具,  # 传递工具列表到模型
        stream=流式,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    if 流式:
        数据块列表 = _流式输出显示(reply)  # 流式模式：实时显示并收集数据块
        result = _流式输出解析(数据块列表)  # 流式模式：用收集的数据块解析
    else:
        i = reply.choices[0].message
        result = i.model_dump()  # 非流式模式：直接返回字典
        
    return result


if __name__ == "__main__":
    #lumiya_chat()
    print(CC_switch_chat(流式=False))

