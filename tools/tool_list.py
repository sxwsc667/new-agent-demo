import json
import tools.tool_box as tool_box

工具调用映射表 = {
    "query_weather": tool_box.查天气, 
    "decompose_development_task":tool_box.decompose_development_task,
    "create_smart_ticket":tool_box.create_smart_ticket
    # 英文别名：DeepSeek 要求工具名只能为英文字母/数字/_/-
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
    {
        "type": "function",
        "function": {
            "name": "decompose_development_task",
            "description": "将用户提出的研发类需求（如发版、重构、Debug）自动拆解为可执行的智能体工作流，每个步骤包含具体动作和耗时预估。这是研发效能的核心能力。",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "用户提出的研发任务描述，例如：'下周要发版' 或 '帮我把登录模块重构一下'"
                    }
                },
                "required": ["task_description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_smart_ticket",
            "description": "创建自动化办公工单，并自动编排后续处理流程（包括意图识别、自动分派、SLA监控等）。适用于任务指派、Bug记录、审批流转等场景。",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "工单标题"
                    },
                    "description": {
                        "type": "string",
                        "description": "工单详细描述"
                    },
                    "auto_assign": {
                        "type": "boolean",
                        "description": "是否自动分配负责人，默认 true",
                        "default": true
                    }
                },
                "required": ["title", "description"]
            }
        }
    }
]


if __name__ == "__main__":
    print(f"映射表取出的对象是: {工具调用映射表.get('查天气')}")
