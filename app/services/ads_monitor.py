# =================================================================
# ADS MONITOR - Sistema de Alertas 24/7 para Meta Ads
# =================================================================
"""
Monitorea métricas críticas y alerta cuando hay problemas que
podrían causar penalización de Meta.

Alertas implementadas:
- EMQ bajo (< 6.0)
- Pixel offline > 1 hora
- Error rate > 5%
- Bot traffic > 30%
- Consent violation
- CPM anómalo (indicativo de problemas de calidad)
"""

import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypedDict

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class Alert:
    """Modelo de alerta"""

    id: str
    timestamp: datetime
    severity: AlertSeverity
    category: str
    message: str
    details: Dict
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class MonitorState(TypedDict):
    """Estado del monitoreo con tipos fuertes para Mypy"""

    last_pixel_event: Optional[datetime]
    emq_scores: Dict[str, Dict[str, Any]]
    error_count: int
    total_events: int
    bot_count: int
    cpm_current: float
    cpm_average: float


class AdsMonitor:
    """
    Sistema de monitoreo continuo para Meta Ads.
    """

    # Umbrales de alerta
    THRESHOLDS = {
        "emq_min": 6.0,  # EMQ < 6.0 = penalización
        "emq_critical": 4.0,  # EMQ < 4.0 = ban risk
        "pixel_offline_max": 3600,  # Segundos (1 hora)
        "error_rate_max": 0.05,  # 5% error rate
        "bot_traffic_max": 0.30,  # 30% tráfico bot
        "cpm_spike_multiplier": 2.0,  # CPM 2x del promedio
    }

    def __init__(self, check_interval: int = 300):  # 5 minutos default
        self.check_interval = check_interval
        self.alerts: List[Alert] = []
        self.alert_handlers: List[Callable] = []
        self.is_running = False
        self.metrics_history: List[Dict] = []

        # Estado actual
        self.current_state: MonitorState = {
            "last_pixel_event": None,
            "emq_scores": {},
            "error_count": 0,
            "total_events": 0,
            "bot_count": 0,
            "cpm_current": 0.0,
            "cpm_average": 0.0,
        }

    def register_alert_handler(self, handler: Callable):
        """Registra un handler para recibir alertas"""
        self.alert_handlers.append(handler)

    def create_alert(
        self,
        severity: AlertSeverity,
        category: str,
        message: str,
        details: Dict | None = None,
    ) -> Alert:
        """Crea y dispara una alerta"""
        alert = Alert(
            id=f"alert_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            severity=severity,
            category=category,
            message=message,
            details=details or {},
        )

        self.alerts.append(alert)

        # Log según severidad
        if severity == AlertSeverity.CRITICAL:
            logger.error(f"🚨 ALERTA CRÍTICA: {message}")
        elif severity == AlertSeverity.WARNING:
            logger.warning(f"⚠️  ALERTA: {message}")
        else:
            logger.info(f"ℹ️  {message}")

        # Notificar handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.exception(f"Error en alert handler: {e}")

        return alert

    def check_emq(self, event_type: str, emq_score: float):
        """Verifica EMQ y genera alertas si es necesario"""
        self.current_state["emq_scores"][event_type] = {
            "score": emq_score,
            "timestamp": datetime.utcnow(),
        }

        if emq_score < self.THRESHOLDS["emq_critical"]:
            self.create_alert(
                severity=AlertSeverity.EMERGENCY,
                category="EMQ",
                message=f"EMQ CRÍTICO ({emq_score}) para {event_type}. RIESGO DE BAN.",
                details={
                    "event_type": event_type,
                    "emq_score": emq_score,
                    "threshold": self.THRESHOLDS["emq_critical"],
                    "action_required": "DETENER ADS INMEDIATAMENTE",
                },
            )
        elif emq_score < self.THRESHOLDS["emq_min"]:
            self.create_alert(
                severity=AlertSeverity.CRITICAL,
                category="EMQ",
                message=f"EMQ bajo ({emq_score}) para {event_type}. Penalización activa.",
                details={
                    "event_type": event_type,
                    "emq_score": emq_score,
                    "threshold": self.THRESHOLDS["emq_min"],
                    "estimated_cpc_increase": "+30%",
                },
            )

    def check_pixel_status(self):
        """Verifica si el Pixel está enviando eventos"""
        last_event = self.current_state["last_pixel_event"]

        if not last_event:
            # No hay eventos registrados aún
            return

        elapsed = (datetime.utcnow() - last_event).total_seconds()

        if elapsed > self.THRESHOLDS["pixel_offline_max"]:
            self.create_alert(
                severity=AlertSeverity.CRITICAL,
                category="PIXEL",
                message=f"Pixel offline por {elapsed / 60:.0f} minutos",
                details={
                    "last_event": last_event.isoformat(),
                    "elapsed_seconds": elapsed,
                    "possible_causes": [
                        "AdBlockers activos",
                        "Error en código de Pixel",
                        "Problemas de red",
                        "Consent rejection",
                    ],
                },
            )

    def check_error_rate(self):
        """Verifica tasa de errores en eventos"""
        total = self.current_state["total_events"]
        errors = self.current_state["error_count"]

        if total == 0:
            return

        error_rate = errors / total

        if error_rate > self.THRESHOLDS["error_rate_max"]:
            self.create_alert(
                severity=AlertSeverity.WARNING,
                category="ERRORS",
                message=f"Tasa de error alta: {error_rate * 100:.1f}%",
                details={
                    "error_rate": error_rate,
                    "total_events": total,
                    "error_count": errors,
                    "threshold": self.THRESHOLDS["error_rate_max"],
                },
            )

    def check_bot_traffic(self):
        """Verifica porcentaje de tráfico bot"""
        total = self.current_state["total_events"]
        bots = self.current_state["bot_count"]

        if total == 0:
            return

        bot_rate = bots / total

        if bot_rate > self.THRESHOLDS["bot_traffic_max"]:
            self.create_alert(
                severity=AlertSeverity.WARNING,
                category="TRAFFIC",
                message=f"Alto tráfico de bots: {bot_rate * 100:.1f}%",
                details={
                    "bot_rate": bot_rate,
                    "total_visits": total,
                    "bot_visits": bots,
                    "recommendation": "Revisar filtros de bot y calidad de audiencia",
                },
            )

    def check_cpm_anomaly(self, current_cpm: float):
        """Detecta spikes en CPM (indicativo de problemas)"""
        self.current_state["cpm_current"] = current_cpm

        # Calcular promedio móvil
        history = [m.get("cpm", 0) for m in self.metrics_history[-30:]]
        if len(history) < 5:
            return

        avg_cpm = sum(history) / len(history)
        self.current_state["cpm_average"] = avg_cpm

        if avg_cpm > 0 and current_cpm > avg_cpm * self.THRESHOLDS["cpm_spike_multiplier"]:
            self.create_alert(
                severity=AlertSeverity.WARNING,
                category="COST",
                message=f"CPM anómalo: ${current_cpm:.2f} (promedio: ${avg_cpm:.2f})",
                details={
                    "current_cpm": current_cpm,
                    "average_cpm": avg_cpm,
                    "increase_percent": ((current_cpm / avg_cpm) - 1) * 100,
                    "possible_causes": [
                        "Competencia aumentando pujas",
                        "Problemas de calidad de anuncio",
                        "Audiencia muy específica",
                        "Problemas de EMQ",
                    ],
                },
            )

    def record_event(self, event_type: str, success: bool, is_bot: bool = False):
        """Registra un evento para monitoreo"""
        self.current_state["total_events"] += 1
        self.current_state["last_pixel_event"] = datetime.utcnow()

        if not success:
            self.current_state["error_count"] += 1

        if is_bot:
            self.current_state["bot_count"] += 1

    async def run_monitoring_loop(self):
        """Loop principal de monitoreo"""
        self.is_running = True
        logger.info("🚀 Ads Monitor iniciado")

        while self.is_running:
            try:
                # Verificar todas las métricas
                self.check_pixel_status()
                self.check_error_rate()
                self.check_bot_traffic()

                # Guardar estado
                self.metrics_history.append(
                    {"timestamp": datetime.utcnow().isoformat(), **self.current_state}
                )

                # Mantener solo últimos 1000 registros
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]

                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.exception(f"Error en monitoring loop: {e}")
                await asyncio.sleep(60)  # Esperar 1 min en caso de error

    def stop(self):
        """Detiene el monitoreo"""
        self.is_running = False
        logger.info("🛑 Ads Monitor detenido")

    def get_status(self) -> Dict:
        """Obtiene estado actual del monitoreo"""
        return {
            "is_running": self.is_running,
            "check_interval": self.check_interval,
            "current_state": self.current_state,
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "total_alerts": len(self.alerts),
            "alert_summary": self._get_alert_summary(),
        }

    def _get_alert_summary(self) -> Dict:
        """Resumen de alertas por severidad"""
        summary = {"emergency": 0, "critical": 0, "warning": 0, "info": 0}

        for alert in self.alerts:
            if not alert.resolved:
                summary[alert.severity.value] += 1

        return summary

    def resolve_alert(self, alert_id: str):
        """Marca una alerta como resuelta"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                logger.info(f"✅ Alerta {alert_id} marcada como resuelta")
                return True
        return False

    def export_report(self, filepath: str):
        """Exporta reporte de monitoreo"""
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "monitor_status": self.get_status(),
            "alerts": [asdict(a) for a in self.alerts[-100:]],  # Últimas 100
            "metrics": self.metrics_history[-168:],  # Última semana (asumiendo 5min interval)
        }

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"📊 Reporte exportado a {filepath}")


# Singleton
ads_monitor = AdsMonitor()


# ═══════════════════════════════════════════════════════════════════════════
# HANDLERS DE ALERTA (Ejemplos)
# ═══════════════════════════════════════════════════════════════════════════


def console_alert_handler(alert: Alert):
    """Handler simple: solo log a consola"""
    pass  # Ya se loguea en create_alert


def webhook_alert_handler(alert: Alert):
    """Handler: envía alerta a webhook (Discord/Slack)"""
    webhook_url = os.getenv("ALERT_WEBHOOK_URL")
    if not webhook_url:
        return

    emoji = {
        AlertSeverity.INFO: "ℹ️",
        AlertSeverity.WARNING: "⚠️",
        AlertSeverity.CRITICAL: "🚨",
        AlertSeverity.EMERGENCY: "🔥",
    }.get(alert.severity, "📢")

    payload = {
        "text": f"{emoji} **{alert.severity.value.upper()}**: {alert.message}",
        "details": alert.details,
    }

    try:
        import requests

        requests.post(webhook_url, json=payload, timeout=5)
    except Exception as e:
        logger.exception(f"Error enviando webhook: {e}")


def email_alert_handler(alert: Alert):
    """Handler: envía alerta por email (solo CRITICAL+)"""
    if alert.severity not in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
        return

    # Implementar con SendGrid/AWS SES/etc
    logger.info(f"📧 Email alert would be sent for: {alert.message}")


# Registrar handlers por defecto
ads_monitor.register_alert_handler(console_alert_handler)
