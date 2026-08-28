from box import box
from System_Prompt.system_prompt import system_prompt
import System_Prompt.skill_list as skill_list



def 预设初始消息():
    system = system_prompt  + skill_list.skill_list
    box["消息"]= [{"role": "system", "content": system}]
 





def 用户输入():
    用户输入 = input("请输入：")
    if 用户输入 == "退出" or 用户输入 == "111":
        box["结束会话"] = True
        用户输入 = "结束会话"
    box["消息"].append({"role": "user", "content": 用户输入})





















if __name__ == "__main__":
    print(box["消息"])
