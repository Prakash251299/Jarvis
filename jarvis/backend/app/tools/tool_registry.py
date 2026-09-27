from typing import Dict, List, Optional, Type
from loguru import logger
from app.tools.base_tool import BaseTool, ToolResult

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool
        logger.info("Registered tool: {}", tool.name)

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[BaseTool]:
        return list(self._tools.values())

    async def execute_tool(self, name: str, **kwargs) -> ToolResult:
        tool = self.get(name)
        if not tool:
            return ToolResult(success=False, output=None, error=f"Tool '{name}' not found")
        try:
            return await tool.execute(**kwargs)
        except Exception as e:
            logger.error("Error executing tool '{}': {}", name, e)
            return ToolResult(success=False, output=None, error=str(e))

    def auto_discover(self):
        from app.tools.builtin.calculator import CalculatorTool
        from app.tools.builtin.datetime_tool import DateTimeTool
        self.register(CalculatorTool())
        self.register(DateTimeTool())

registry = ToolRegistry()
