# =================================================================
# EMQ VALIDATOR - Event Match Quality Monitor
# =================================================================
"""
Monitorea y valida la calidad de matching de eventos para Meta CAPI.

Meta penaliza (cobra más) cuando EMQ < 6.0:
- EMQ 9-10: Costo óptimo
- EMQ 6-8: Costo normal
- EMQ < 6: +30% CPC (penalización)
- EMQ < 4: +50% CPC (severa)
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class EMQScore(Enum):
    """Niveles de EMQ y sus implicaciones"""

    EXCELLENT = (9.0, 10.0, "Costo óptimo", "green")
    GOOD = (7.0, 8.9, "Costo normal", "yellow")
    FAIR = (6.0, 6.9, "Ligera penalización", "orange")
    POOR = (4.0, 5.9, "Alta penalización (+30% CPC)", "red")
    CRITICAL = (0.0, 3.9, "Severa penalización (+50% CPC)", "dark_red")

    def __init__(self, min_score, max_score, description, color):
        self.min_score = min_score
        self.max_score = max_score
        self.description = description
        self.color = color

    @classmethod
    def from_score(cls, score: float) -> "EMQScore":
        for level in cls:
            if level.min_score <= score <= level.max_score:
                return level
        return cls.CRITICAL


@dataclass
class EMQEvent:
    """Registro de evento para análisis EMQ"""

    event_name: str
    event_id: str
    timestamp: datetime
    emq_score: float
    match_keys: Dict[str, bool]  # Qué campos tenían match
    user_data: Dict[str, Any]


class EMQValidator:
    """
    Valida y monitorea Event Match Quality para Meta CAPI.
    """

    # Campos requeridos para EMQ óptimo (9-10)
    OPTIMAL_FIELDS = [
        "em",  # Email (hash)
        "ph",  # Phone (hash)
        "fn",  # First Name
        "ln",  # Last Name
        "ct",  # City
        "st",  # State
        "country",  # Country
        "zp",  # Zip
        "external_id",  # ID único
        "fbc",  # FB Click ID
        "fbp",  # FB Browser ID
    ]

    # Ponderaciones de campos (estimado basado en docs de Meta)
    FIELD_WEIGHTS = {
        "em": 2.0,  # Email es el más importante
        "ph": 1.8,  # Phone muy importante
        "external_id": 1.5,
        "fbc": 1.5,  # FB Click ID (atribución directa)
        "fbp": 1.3,  # FB Pixel ID
        "fn": 0.8,
        "ln": 0.8,
        "ct": 0.5,
        "st": 0.5,
        "country": 0.4,
        "zp": 0.4,
        "client_ip_address": 0.3,
        "client_user_agent": 0.3,
    }

    EMQ_THRESHOLD_WARNING = 6.0  # Alerta si baja de aquí
    EMQ_THRESHOLD_CRITICAL = 4.0  # Bloquear ads si baja de aquí

    def __init__(self, storage_path: str = ".logs/emq_history.json"):
        self.storage_path = storage_path
        self.events: List[EMQEvent] = []
        self.daily_scores: Dict[str, Dict[str, float]] = {}
        self._load_history()

    def calculate_emq(self, user_data: Dict[str, Any]) -> Dict:
        """
        Calcula EMQ score estimado basado en campos presentes.

        Returns:
            {
                "score": float (0-10),
                "level": EMQScore,
                "matched_fields": List[str],
                "missing_fields": List[str],
                "recommendations": List[str]
            }
        """
        score = 0.0
        matched = []
        missing = []
        recommendations = []

        # Verificar cada campo ponderado
        for field, weight in self.FIELD_WEIGHTS.items():
            if self._has_valid_field(user_data, field):
                score += weight
                matched.append(field)
            else:
                missing.append(field)

        # Normalizar a escala 0-10
        max_possible = sum(self.FIELD_WEIGHTS.values())
        normalized_score = min(10.0, (score / max_possible) * 10)

        # Generar recomendaciones
        if "em" not in matched:
            recommendations.append("Agregar email hashing para mejorar EMQ")
        if "ph" not in matched:
            recommendations.append("Agregar phone hashing para mejorar EMQ")
        if "external_id" not in matched:
            recommendations.append("Generar external_id consistente server-side")
        if "fbc" not in matched and "fbp" not in matched:
            recommendations.append("Capturar fbclid de URL para atribución")

        level = EMQScore.from_score(normalized_score)

        return {
            "score": round(normalized_score, 2),
            "level": level,
            "matched_fields": matched,
            "missing_fields": missing,
            "recommendations": recommendations,
            "max_possible": max_possible,
            "raw_score": score,
        }

    def _has_valid_field(self, user_data: Dict, field: str) -> bool:
        """Verifica si un campo existe y es válido"""
        value = user_data.get(field)
        if not value:
            return False

        # Validaciones específicas
        if field in ["em", "ph"]:
            # Debe ser hash SHA256
            return isinstance(value, str) and len(value) == 64

        if field in ["fbc", "fbp"]:
            # Formato específico de FB
            return isinstance(value, str) and value.startswith("fb.")

        return True

    def validate_event(self, event_name: str, event_id: str, user_data: Dict) -> Dict:
        """
        Valida un evento antes de enviarlo a Meta.

        Returns:
            {
                "valid": bool,
                "emq": dict,
                "warnings": List[str],
                "can_send": bool  # Si EMQ >= 4.0
            }
        """
        emq_result = self.calculate_emq(user_data)
        warnings = []

        # Validaciones específicas por tipo de evento
        if event_name == "Purchase":
            if "value" not in user_data.get("custom_data", {}):
                warnings.append("Evento Purchase sin 'value'")
            if "currency" not in user_data.get("custom_data", {}):
                warnings.append("Evento Purchase sin 'currency'")

        # Guardar en historial
        event = EMQEvent(
            event_name=event_name,
            event_id=event_id,
            timestamp=datetime.utcnow(),
            emq_score=emq_result["score"],
            match_keys={k: k in emq_result["matched_fields"] for k in self.FIELD_WEIGHTS.keys()},
            user_data=user_data,
        )
        self.events.append(event)
        self._save_history()

        # Alertas
        if emq_result["score"] < self.EMQ_THRESHOLD_CRITICAL:
            logger.error(f"🔴 EMQ CRÍTICO: {emq_result['score']} para {event_name}")
            warnings.append(f"EMQ muy bajo ({emq_result['score']}) - Evento no debería enviarse")
        elif emq_result["score"] < self.EMQ_THRESHOLD_WARNING:
            logger.warning(f"🟡 EMQ BAJO: {emq_result['score']} para {event_name}")
            warnings.append(f"EMQ bajo ({emq_result['score']}) - Considerar mejorar matching")

        return {
            "valid": len(warnings) == 0,
            "emq": emq_result,
            "warnings": warnings,
            "can_send": emq_result["score"] >= self.EMQ_THRESHOLD_CRITICAL,
            "penalty": emq_result["level"].description if emq_result["score"] < 6 else None,
        }

    def get_daily_report(self, date: Optional[datetime] = None) -> Dict:
        """
        Genera reporte diario de EMQ para monitoreo.
        """
        if date is None:
            date = datetime.utcnow()

        date_str = date.strftime("%Y-%m-%d")

        # Filtrar eventos del día
        day_events = [e for e in self.events if e.timestamp.strftime("%Y-%m-%d") == date_str]

        if not day_events:
            return {"error": "No events for date", "date": date_str}

        # Calcular métricas
        scores = [e.emq_score for e in day_events]
        avg_score = sum(scores) / len(scores)

        events_by_type = {}
        for e in day_events:
            events_by_type[e.event_name] = events_by_type.get(e.event_name, 0) + 1

        # Eventos por nivel de EMQ
        level_counts = {"excellent": 0, "good": 0, "fair": 0, "poor": 0, "critical": 0}
        for score in scores:
            level = EMQScore.from_score(score)
            if level == EMQScore.EXCELLENT:
                level_counts["excellent"] += 1
            elif level == EMQScore.GOOD:
                level_counts["good"] += 1
            elif level == EMQScore.FAIR:
                level_counts["fair"] += 1
            elif level == EMQScore.POOR:
                level_counts["poor"] += 1
            else:
                level_counts["critical"] += 1

        report = {
            "date": date_str,
            "total_events": len(day_events),
            "avg_emq": round(avg_score, 2),
            "min_emq": round(min(scores), 2),
            "max_emq": round(max(scores), 2),
            "level": EMQScore.from_score(avg_score).name,
            "penalty_risk": avg_score < 6.0,
            "events_by_type": events_by_type,
            "level_distribution": level_counts,
            "recommendation": self._get_recommendation(avg_score),
        }

        return report

    def _get_recommendation(self, avg_score: float) -> str:
        """Genera recomendación basada en score promedio"""
        if avg_score >= 9:
            return "EMQ óptimo. Mantener configuración actual."
        elif avg_score >= 7:
            return "Buen EMQ. Considerar agregar email/phone hashing."
        elif avg_score >= 6:
            return "EMQ aceptable. Mejorar captura de external_id y fbc."
        elif avg_score >= 4:
            return "⚠️ EMQ bajo. Revisar implementación de CAPI inmediatamente."
        else:
            return "🚨 EMQ crítico. NO INICIAR ADS hasta resolver."

    def _load_history(self):
        """Carga historial de eventos desde disco"""
        try:
            import os

            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    # Reconstruir objetos EMQEvent
                    for e in data.get("events", [])[-1000:]:  # Mantener últimos 1000
                        self.events.append(
                            EMQEvent(
                                event_name=e["event_name"],
                                event_id=e["event_id"],
                                timestamp=datetime.fromisoformat(e["timestamp"]),
                                emq_score=e["emq_score"],
                                match_keys=e["match_keys"],
                                user_data=e["user_data"],
                            )
                        )
        except Exception as e:
            logger.warning(f"Could not load EMQ history: {e}")

    def _save_history(self):
        """Guarda historial de eventos a disco"""
        try:
            import os

            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

            # Mantener solo últimos 1000 eventos
            recent_events = self.events[-1000:]

            data = {
                "events": [
                    {
                        "event_name": e.event_name,
                        "event_id": e.event_id,
                        "timestamp": e.timestamp.isoformat(),
                        "emq_score": e.emq_score,
                        "match_keys": e.match_keys,
                        "user_data": e.user_data,
                    }
                    for e in recent_events
                ]
            }

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.warning(f"Could not save EMQ history: {e}")


# Singleton
emq_validator = EMQValidator()
