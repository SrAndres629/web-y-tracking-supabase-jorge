from typing import Any, Callable, Dict, List


class GetAllVisitorsQuery:
    def __init__(self, list_visitors: Callable[..., List[Dict[str, Any]]]):
        self._list_visitors = list_visitors

    async def execute(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Executes the query to retrieve all visitors.
        """
        return self._list_visitors(limit=limit)
