import ast
import operator
import math
from .tools import ToolExcuter

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

from hello_agents import HelloAgentsLLM
from dotenv import load_dotenv
load_dotenv()
if __name__ == "__main__":
    register = create_calculate_register()
    llm = HelloAgentsLLM()
    messages = [
        {'role'}:'system','content':'请注意，你是一个有能力调用外部工具的智能助手。对于用户问题，你先思考是否需要调用工具解决。如果需要则说明'
        {'role':'user','content':''}
    ]