import math
import re
from app.tools.base_tool import BaseTool, ToolResult

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Safely evaluate mathematical expressions (e.g. '2 + 2', 'sqrt(144) * 3')."
    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The math expression to evaluate."
            }
        },
        "required": ["expression"]
    }

    _ALLOWED_NAMES = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
        "exp": math.exp, "pow": pow, "abs": abs,
        "floor": math.floor, "ceil": math.ceil, "round": round,
        "pi": math.pi, "e": math.e
    }

    async def execute(self, expression: str = "", **kwargs) -> ToolResult:
        expr = expression.strip()
        if not expr:
            return ToolResult(success=False, output=None, error="Empty expression provided")

        if not re.match(r'^[0-9+\-*/()., %^eEa-z_]+$', expr):
            return ToolResult(success=False, output=None, error="Expression contains invalid characters")

        expr = expr.replace('^', '**')
        try:
            code = compile(expr, "<string>", "eval")
            for name in code.co_names:
                if name not in self._ALLOWED_NAMES:
                    return ToolResult(success=False, output=None, error=f"Use of forbidden function: {name}")

            result = eval(code, {"__builtins__": {}}, self._ALLOWED_NAMES)
            return ToolResult(success=True, output=result)
        except Exception as e:
            return ToolResult(success=False, output=None, error=f"Calculation error: {e}")
