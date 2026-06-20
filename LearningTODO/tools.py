import os
from typing import Dict,Any

class ToolExcuter:
    ""
    def __init__(self):
        self.tools:Dict[str, Dict[str, Any]] = {}
     
    def registerTool(self,name:str,description:str,func:callable):
        if name in self.tools:
            return "工具已存在!"
        self.tools[name]={'description':description,'func':func}
        print(f"工具{name}已注册！")

    def getAvailableTools(self) -> str:
        return '\n'.join(f"{name}:{info['discription']}" for name,info in self.tools.item())

    def getTool(self,name:str)-> callable:
        return self.tools[name]['func']