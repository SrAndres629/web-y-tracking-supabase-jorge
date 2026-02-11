from typing import List, Dict, Any
from app.database import get_all_visitors

class GetAllVisitorsQuery:
    async def execute(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Executes the query to retrieve all visitors.
        """
        return await get_all_visitors(limit=limit)
