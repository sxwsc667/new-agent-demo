import json
import tools.tool_box as tool_box

工具调用映射表 = {
    "查天气": tool_box.查天气,
    "query_weather": tool_box.查天气,  # 英文别名：DeepSeek 要求工具名只能为英文字母/数字/_/-
}

# 工具列表：OpenAI function calling 格式，每个元素是一个工具定义
# 后续新增工具就把新工具定义追加进这个列表即可
tool_list = [
    {
        "type": "function",
        "function": {
            "name": "query_weather",
            "description": "查询指定城市的当前天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "城市": {
                        "type": "string",
                        "description": "要查询天气的城市名称，例如：北京",
                    },
                },
                "required": ["城市"],
            },
        },
    },
]

if __name__ == "__main__":
    print(f"映射表取出的对象是: {工具调用映射表.get('查天气')}")
