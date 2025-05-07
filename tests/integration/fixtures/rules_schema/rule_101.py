from typing import Any


class Rule:
    id = "101"
    description = "Verify schema passed"
    severity = "HIGH"

    @classmethod
    def match(cls, data: dict[Any, Any], schema: Any) -> list[str]:
        results = []
        if not schema:
            results.append("No schema")
        return results
