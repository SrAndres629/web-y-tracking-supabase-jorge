from typing import Dict, Any, Callable

class GetSignalAuditQuery:
    def __init__(self, get_cursor: Callable[[], Any]):
        self._get_cursor = get_cursor

    async def execute(self) -> Dict[str, Any]:
        """
        Executes the query to perform a signal audit.
        Compares Leads (DB) vs Eventos Enviados (Flag 'sent_to_meta' o proxy).
        """
        try:
            with self._get_cursor() as cur:
                # 1. Total Contactos Únicos
                cur.execute("SELECT COUNT(*) FROM crm_leads")
                total_leads = cur.fetchone()[0]

                # 2. Total con fb_click_id (Proxy de calidad/señal)
                cur.execute("SELECT COUNT(*) FROM crm_leads WHERE fb_click_id IS NOT NULL")
                leads_with_signal = cur.fetchone()[0]
                
                # 3. Discrepancy
                match_rate = 0
                if total_leads > 0:
                    match_rate = round((leads_with_signal / total_leads) * 100, 2)
                    
                return {
                    "status": "active",
                    "audit": {
                        "total_leads_db": total_leads,
                        "quality_leads_with_fbclid": leads_with_signal,
                        "signal_match_rate": f"{match_rate}%",
                        "alert": "LOW SIGNAL" if match_rate < 50 else "HEALTHY"
                    },
                    "recommendation": "Check 'tracking.js' if Match Rate < 80%"
                }
        except Exception as e:
            return {"error": str(e)}
