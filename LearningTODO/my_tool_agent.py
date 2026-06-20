from dotenv import load_dotenv
from openai import OpenAI
import os
from typing import List,Dict,Tuple,Any
import json
import ast
import operator
import math

from tools import ToolExcuter

load_dotenv()

class ToolAgent:
    def __init__(self, api_key:str=None, base_url:str=None, model_name:str=None, time_out:int=None, tools:List[Dict[str,Any]]=[]):
        api_key = api_key or os.getenv("LLM_API_KEY")
        base_url = base_url or os.getenv("LLM_BASE_URL")
        time_out = time_out or int(os.getenv("LLM_TIME_OUT",60))
        self.model = model_name or os.getenv("LLM_MODEL_ID")
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=time_out)
        self.tools = tools

    def _excute_tool(self, tool_name:str, tool_args:Dict[str, Any]):
        if tool_name not in self.tools:
            return f"错误：不存在工具 {tool_name}"
        try:
            results = self.tools[tool_name]["func"](**tool_args)
            return results
        except Exception as e:
            return f"工具{tool_name}执行异常：{str(e)}"

    def run(self,message:List[Dict[str,str]], temperature:float=0)->str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=message,
            tools=self.tools,
            stream=True,
            temperature=temperature,
            tool_choice="auto" if self.tools else None
        )

        collect_content = []
        tool_calls = {}

        for chunk in response:
            if not chunk.choices:
                continue
            delta = chunk.choices.delta
            if delta["content"]:
                collect_content.append(delta["content"])
            if delta["tool_calls"]:
                for call in delta["tool_calls"]:
                    idx = call['index']
                    if idx not in tool_calls:
                        tool_calls[idx]={
                            "id":call["id"],
                            "name":call["function"]["name"] or "",
                            "arguments":call["function"]["arguments"] or "",
                        }
                    else:
                        if call['function']['name'] :
                            tool_calls[idx]["name"] += call["function"]["name"]
                        if call["function"]["arguments"]:
                            tool_calls[idx]["arguments"] += call["function"]["arguments"]

        content_txt = "".join(collect_content)
        if tool_calls:
            for _,call_info in tool_calls.items():
                tool_name = call_info['name']
                try:
                    tool_args = call_info['arguments']
                except Exception as e:
                    tool_args = {}
                tool_results = str(self._excute_tool(tool_name,tool_args))
                tool_call_msg = {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": call_info["id"],
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(tool_args)
                            }
                        }
                    ]
                }
                tool_res_msg = {
                    "role": "tool",
                    "tool_call_id": call_info["id"],
                    "name": tool_name,
                    "content": tool_results
                }
                message = message + [tool_call_msg, tool_res_msg]
                final_answer = self.run(message,temperature)
                return final_answer
        return content_txt

def my_calculate(expression: str) -> str:
    """简单的数学计算函数"""
    if not expression.strip():
        return "计算表达式不能为空"

    # 支持的基本运算
    operators = {
        ast.Add: operator.add,      # +
        ast.Sub: operator.sub,      # -
        ast.Mult: operator.mul,     # *
        ast.Div: operator.truediv,  # /
    }

    # 支持的基本函数
    functions = {
        'sqrt': math.sqrt,
        'pi': math.pi,
    }

    try:
        node = ast.parse(expression, mode='eval')
        result = _eval_node(node.body, operators, functions)
        return str(result)
    except:
        return "计算失败，请检查表达式格式"

def _eval_node(node, operators, functions):
    """简化的表达式求值"""
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        left = _eval_node(node.left, operators, functions)
        right = _eval_node(node.right, operators, functions)
        op = operators.get(type(node.op))
        return op(left, right)
    elif isinstance(node, ast.Call):
        func_name = node.func.id
        if func_name in functions:
            args = [_eval_node(arg, operators, functions) for arg in node.args]
            return functions[func_name](*args)
    elif isinstance(node, ast.Name):
        if node.id in functions:
            return functions[node.id]

def create_calculate_register():
    register = ToolExcuter()
    register.registerTool(
        name='my calculator',
        description='简单的数学计算工具，支持基本运算(+,-,*,/)和sqrt函数',
        func=my_calculate
    )
    return register

if __name__ == "__main__":
    tools = create_calculate_register().tools
    agent = ToolAgent(tools=tools)
    user_msg = [
        {"role": "user", "content": "现在几点？再帮我算一下 123 乘以 456"}
        ]
    ans = agent.run(message=user_msg)
    print("最终回答：", ans)
   