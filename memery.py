# 上下文工程模块：负责把每一轮对话需要的材料组装成发给模型的完整消息列表

import os
from box import box
from search_llm import get_llm_name

# 摘要文件的存放位置（单文件覆盖，不追加、不带时间戳，保持轻量）
摘要文件路径 = "memory/对话摘要.txt"


def 按轮次切分(消息):
    """
    把消息列表（不含开头的 system）切分成"轮次"列表。
    一轮 = 一条 user 消息 + 其后到下一 user 为止的所有消息（含 assistant、tool）。
    """
    轮列表 = []
    当前轮 = []
    for 条 in 消息:
        # 遇到新的 user 消息，且当前已在积累内容，就把上一轮收尾存起来
        if 条.get("role") == "user" and 当前轮:
            轮列表.append(当前轮)
            当前轮 = [条]
        else:
            当前轮.append(条)
    if 当前轮:
        轮列表.append(当前轮)
    return 轮列表


def 生成摘要(轮列表):
    """
    调用模型，把被压缩的若干轮对话压成一段简洁的中文摘要。
    """
    系统提示 = [{"role": "system", "content": "请把下面这段对话压缩成一段简洁的中文摘要，保留关键信息，语气客观。"}]
    临时消息 = 系统提示 + [条 for 轮 in 轮列表 for 条 in 轮]
    name = get_llm_name(box["主模型"])
    回复 = name(临时消息, None)  # 生成摘要不需要工具，可用工具传 None
    return 回复["content"]


def 写入摘要文件(摘要):
    """
    把生成的摘要写进单独的摘要文件（单文件覆盖，不追加、不带时间戳）。
    """
    os.makedirs("memory", exist_ok=True)
    with open(摘要文件路径, "w", encoding="utf-8") as 文件:
        文件.write(摘要)


def 上下文压缩():
    """
    当 box["消息"] 里的对话达到 10 轮（一轮 = 一条 user + 一条 assistant）时，
    把最老的 5 轮压缩成一段摘要，写进单独的摘要文件，
    并用这条摘要消息替换掉那 5 轮在消息里的位置，
    最终保留：system 头部 + 摘要 + 最近保留的若干轮。
    """
    消息 = box["消息"]

    # 用 user 消息的数量来统计轮数
    轮数 = sum(1 for 条 in 消息 if 条.get("role") == "user")
    if 轮数 < 10:
        return

    # 找到第一条 user 的位置，前面的 system 等头部消息原样保留
    首个user索引 = next(i for i, 条 in enumerate(消息) if 条.get("role") == "user")
    头部 = 消息[:首个user索引]              # 含 system 在内的固定头部
    轮列表 = 按轮次切分(消息[首个user索引:])

    最老5轮 = 轮列表[:5]
    保留轮 = 轮列表[5:]

    # 生成摘要并写入文件
    摘要 = 生成摘要(最老5轮)
    写入摘要文件(摘要)

    # 用一条摘要消息替换被压缩的那 5 轮位置
    摘要消息 = [{"role": "assistant", "content": "以下是此前被压缩的对话摘要：" + 摘要}]

    # 重新组装：头部 + 摘要 + 保留的轮次（展平为消息列表）
    box["消息"] = 头部 + 摘要消息 + [条 for 轮 in 保留轮 for 条 in 轮]