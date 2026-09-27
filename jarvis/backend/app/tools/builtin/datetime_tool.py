from datetime import datetime, timezone
from app.tools.base_tool import BaseTool, ToolResult

class DateTimeTool(BaseTool):
    name = "get_current_datetime"
    description = "Get current date, time, and day of week in ISO or readable format."
    parameters = {
        "type": "object",
        "properties": {
            "format": {
                "type": "string",
                "enum": ["readable", "iso", "date_only", "time_only"],
                "description": "Output format style."
            }
        },
        "required": []
    }

    async def execute(self, format: str = "readable", **kwargs) -> ToolResult:
        now = datetime.now(timezone.utc)
        if format == "iso":
            res = now.isoformat()
        elif format == "date_only":
            res = now.strftime("%Y-%m-%d")
        elif format == "time_only":
            res = now.strftime("%H:%M:%S UTC")
        else:
            res = now.strftime("%A, %B %d, %Y at %I:%M:%S %p UTC")

        return ToolResult(success=True, output=res)
