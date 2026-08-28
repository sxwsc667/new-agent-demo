
import json
import random
from datetime import datetime, timedelta

def 查天气(城市):
    return f"{城市}的天气是晴朗的"





def decompose_development_task(task_description: str):
    """
    研发效能核心工具：将重复性开发任务抽象为可自动执行的智能体工作流。
    模拟 Codex 的意图识别 → 任务拆分 → 编排执行的闭环。
    """
    # 预置几类常见研发场景的“工作流模板”
    templates = {
        "发版": {
            "workflow_name": "版本发布自动化流水线",
            "steps": [
                {"step": 1, "action": "代码冻结 & 分支创建 (release/v{version})", "estimated_time": "10min"},
                {"step": 2, "action": "执行全量自动化测试 (Unit + E2E)", "estimated_time": "15min"},
                {"step": 3, "action": "LLM-as-Judge 代码质量评分 (三维度)", "estimated_time": "5min"},
                {"step": 4, "action": "生成 CHANGELOG 与发版说明 (Release Notes)", "estimated_time": "3min"},
                {"step": 5, "action": "构建 Docker 镜像并推送至仓库", "estimated_time": "8min"},
                {"step": 6, "action": "触发灰度发布 (Canary Deployment)", "estimated_time": "20min"}
            ]
        },
        "重构": {
            "workflow_name": "代码重构与优化工作流",
            "steps": [
                {"step": 1, "action": "识别重复代码块 & 设计模式分析", "estimated_time": "30min"},
                {"step": 2, "action": "拆分大函数，单一职责改造", "estimated_time": "45min"},
                {"step": 3, "action": "更新单元测试，确保覆盖率 ≥ 85%", "estimated_time": "20min"},
                {"step": 4, "action": "执行回归测试，验证业务逻辑无退化", "estimated_time": "15min"},
                {"step": 5, "action": "提交 PR，触发 Code Review Agent 自动审查", "estimated_time": "10min"}
            ]
        },
        "debug": {
            "workflow_name": "线上 Bug 修复应急流程",
            "steps": [
                {"step": 1, "action": "通过 RAG 检索相似历史工单与解决方案", "estimated_time": "3min"},
                {"step": 2, "action": "定位异常日志，分析堆栈调用链", "estimated_time": "8min"},
                {"step": 3, "action": "生成修复代码补丁 (Patch)", "estimated_time": "12min"},
                {"step": 4, "action": "执行影响面评估 (Impact Analysis)", "estimated_time": "5min"},
                {"step": 5, "action": "创建工单并自动指派给负责人", "estimated_time": "2min"}
            ]
        }
    }
    
    # 智能匹配（演示版：关键词匹配）
    matched_template = None
    for keyword, template in templates.items():
        if keyword in task_description:
            matched_template = template
            break
    
    # 默认回退：通用工作流
    if not matched_template:
        matched_template = {
            "workflow_name": "通用研发任务自动化编排",
            "steps": [
                {"step": 1, "action": "意图识别与需求解析 (Intent Classification)", "estimated_time": "2min"},
                {"step": 2, "action": "工具调用编排 (Function Calling Orchestration)", "estimated_time": "3min"},
                {"step": 3, "action": "执行结果聚合与自检 (Self-Correction)", "estimated_time": "5min"},
                {"step": 4, "action": "生成结构化报告并交付", "estimated_time": "2min"}
            ]
        }
    
    return json.dumps({
        "status": "success",
        "original_task": task_description,
        "workflow": matched_template,
        "message": f"已自动拆解为 {len(matched_template['steps'])} 个可执行步骤，预计总耗时 {sum(s['estimated_time'].replace('min','') for s in matched_template['steps'])} 分钟"
    }, ensure_ascii=False)




_ticket_db = []
_ticket_counter = 0

def create_smart_ticket(title: str, description: str, auto_assign: bool = True):
    """
    自动化办公工具：创建一个智能工单，并自动触发后续编排动作（模拟）。
    对应简历中“工具调用与编排 → 多步任务编排与失败重试”。
    """
    global _ticket_counter
    _ticket_counter += 1
    
    # 模拟根据描述自动生成“编排计划”（这就是简历里的“把重复性工作抽象为工作流”）
    orchestration_plan = [
        "步骤 1: 意图识别 → 判定为研发类任务",
        f"步骤 2: 匹配责任人 → {'自动分配至后端组 (模拟)' if auto_assign else '等待人工指派'}",
        "步骤 3: 创建工单并同步至演示仪表板",
        "步骤 4: 触发异步通知 (模拟邮件/飞书消息)",
        "步骤 5: 设置 SLA 时效监控 (24h内闭环)"
    ]
    
    new_ticket = {
        "ticket_id": f"TICKET-{_ticket_counter:04d}",
        "title": title,
        "description": description,
        "status": "已创建 (编排中)",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "orchestration_status": "执行中",
        "auto_assign": auto_assign,
        "estimated_completion": (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    }
    _ticket_db.append(new_ticket)
    
    return json.dumps({
        "status": "created",
        "ticket": new_ticket,
        "orchestration_plan": orchestration_plan,
        "message": f"✅ 工单已创建，智能编排引擎已自动生成 {len(orchestration_plan)} 步执行计划"
    }, ensure_ascii=False)





