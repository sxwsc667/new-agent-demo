box = {
    "主模型": "CC_switch",
    "消息": [], 
    "调用工具": None,
    "结束会话": False,
    "工具调用结果": [],
    "可用工具": [],
    "是否调用工具": False,
    "最终回复": None,
    "回复消息": {        
        "role": "assistant",   # 角色标识,用它来区分用户（"user"）、助手（"assistant"）和工具（"tool"）
        "content": None,#最终回复内容
        "refusal": None,       # 如果模型因为安全策略等原因拒绝回答用户的问题，这里会给出拒绝理由
        # 工具调用列表,当模型决定调用工具时，会包含调用指令，
        # 包括：id：唯一调用 ID（后面执行完工具回传时需要带上）
        # type：固定为 "function(功能OpenAI提前预留的，实际上并没有别的选择)"
        # function：包含 name和 arguments（JSON 格式的参数）        
        "tool_calls": None,   
        "function_call": None, # 旧版函数调用字段，现在已被 tool_calls 取代。保留以兼容
        "audio": None,         # 音频数据,如果模型支持并返回音频，这里会包含音频数据。文本模型不会返回这个
        "annotations": None,   # 某些服务会在答案中附上引文来源或注释，DeepSeek不用
        "reasoning_content":None# 推理内容
        }
 }
        
