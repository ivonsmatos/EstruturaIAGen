"""
Alert Management System for EstruturaIAGen
Handles email notifications, Slack integration, and custom alert rules
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable, Any
import uuid
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    WEBHOOK = "webhook"


@dataclass
class AlertRule:
    """Defines conditions for triggering alerts"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    metric: str = ""  # e.g., "error_rate", "cost", "response_time"
    condition: str = ""  # e.g., "greater_than", "less_than", "equals"
    threshold: float = 0.0
    severity: AlertSeverity = AlertSeverity.MEDIUM
    enabled: bool = True
    check_interval: int = 300  # seconds
    created_at: datetime = field(default_factory=datetime.now)
    last_checked: Optional[datetime] = None
    consecutive_violations: int = 0
    max_consecutive_before_alert: int = 3  # consecutive threshold violations
    channels: List[AlertChannel] = field(default_factory=list)
    cooldown: int = 3600  # seconds before same alert can fire again

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['severity'] = self.severity.value
        data['channels'] = [ch.value for ch in self.channels]
        data['created_at'] = self.created_at.isoformat()
        data['last_checked'] = self.last_checked.isoformat() if self.last_checked else None
        return data


@dataclass
class Alert:
    """Represents a triggered alert"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str = ""
    rule_name: str = ""
    severity: AlertSeverity = AlertSeverity.MEDIUM
    message: str = ""
    current_value: Any = None
    threshold: Any = None
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['severity'] = self.severity.value
        data['triggered_at'] = self.triggered_at.isoformat()
        data['acknowledged_at'] = self.acknowledged_at.isoformat() if self.acknowledged_at else None
        return data


class NotificationChannel(ABC):
    """Abstract base class for notification channels"""

    @abstractmethod
    def send(self, alert: Alert, recipients: List[str]) -> bool:
        """Send alert notification"""
        pass


class EmailChannel(NotificationChannel):
    """Email notification channel"""

    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587,
                 sender_email: Optional[str] = None, sender_password: Optional[str] = None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email or os.getenv("ALERT_EMAIL_SENDER")
        self.sender_password = sender_password or os.getenv("ALERT_EMAIL_PASSWORD")

    def send(self, alert: Alert, recipients: List[str]) -> bool:
        """Send alert via email"""
        if not self.sender_email or not self.sender_password:
            logger.error("Email sender credentials not configured")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{alert.severity.value.upper()}] {alert.rule_name}"
            msg["From"] = self.sender_email
            msg["To"] = ", ".join(recipients)

            # Create plain text and HTML versions
            text = f"""
Alert triggered: {alert.rule_name}
Severity: {alert.severity.value}
Message: {alert.message}
Current Value: {alert.current_value}
Threshold: {alert.threshold}
Triggered At: {alert.triggered_at.isoformat()}
            """.strip()

            html = f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <div style="border-left: 4px solid #{self._severity_color(alert.severity)}; padding: 10px; background: #f5f5f5;">
      <h2 style="color: #{self._severity_color(alert.severity)};">{alert.rule_name}</h2>
      <p><strong>Severity:</strong> {alert.severity.value.upper()}</p>
      <p><strong>Message:</strong> {alert.message}</p>
      <p><strong>Current Value:</strong> {alert.current_value}</p>
      <p><strong>Threshold:</strong> {alert.threshold}</p>
      <p><strong>Triggered At:</strong> {alert.triggered_at.isoformat()}</p>
    </div>
  </body>
</html>
            """.strip()

            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            msg.attach(part1)
            msg.attach(part2)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipients, msg.as_string())

            logger.info(f"Email alert sent to {recipients}: {alert.rule_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
            return False

    @staticmethod
    def _severity_color(severity: AlertSeverity) -> str:
        """Get hex color for severity level"""
        colors = {
            AlertSeverity.LOW: "4CAF50",
            AlertSeverity.MEDIUM: "FF9800",
            AlertSeverity.HIGH: "F44336",
            AlertSeverity.CRITICAL: "9C27B0"
        }
        return colors.get(severity, "808080")


class SlackChannel(NotificationChannel):
    """Slack notification channel"""

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")

    def send(self, alert: Alert, recipients: List[str]) -> bool:
        """Send alert via Slack"""
        if not self.webhook_url:
            logger.error("Slack webhook URL not configured")
            return False

        try:
            import requests  # Optional dependency

            color_map = {
                AlertSeverity.LOW: "#4CAF50",
                AlertSeverity.MEDIUM: "#FF9800",
                AlertSeverity.HIGH: "#F44336",
                AlertSeverity.CRITICAL: "#9C27B0"
            }

            payload = {
                "text": f"{alert.severity.value.upper()}: {alert.rule_name}",
                "attachments": [
                    {
                        "color": color_map.get(alert.severity, "#808080"),
                        "fields": [
                            {"title": "Alert Rule", "value": alert.rule_name, "short": True},
                            {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                            {"title": "Message", "value": alert.message, "short": False},
                            {"title": "Current Value", "value": str(alert.current_value), "short": True},
                            {"title": "Threshold", "value": str(alert.threshold), "short": True},
                            {"title": "Triggered At", "value": alert.triggered_at.isoformat(), "short": False}
                        ]
                    }
                ]
            }

            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                logger.info(f"Slack alert sent: {alert.rule_name}")
                return True
            else:
                logger.error(f"Slack API error: {response.status_code}")
                return False
        except ImportError:
            logger.warning("requests library not installed for Slack integration")
            return False
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {str(e)}")
            return False


class WebhookChannel(NotificationChannel):
    """Custom webhook notification channel"""

    def __init__(self, webhook_url: str = ""):
        self.webhook_url = webhook_url

    def send(self, alert: Alert, recipients: List[str]) -> bool:
        """Send alert via webhook"""
        if not self.webhook_url:
            logger.error("Webhook URL not configured")
            return False

        try:
            import requests  # Optional dependency

            payload = alert.to_dict()
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code in (200, 201):
                logger.info(f"Webhook alert sent: {alert.rule_name}")
                return True
            else:
                logger.error(f"Webhook error: {response.status_code}")
                return False
        except ImportError:
            logger.warning("requests library not installed for webhook integration")
            return False
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {str(e)}")
            return False


class AlertManager:
    """Central alert management system"""

    def __init__(self, redis_client=None):
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.channels: Dict[AlertChannel, NotificationChannel] = {
            AlertChannel.EMAIL: EmailChannel(),
            AlertChannel.SLACK: SlackChannel(),
            AlertChannel.WEBHOOK: WebhookChannel()
        }
        self.redis_client = redis_client
        self.last_alert_times: Dict[str, datetime] = {}  # Track cooldowns
        self.listeners: List[Callable[[Alert], None]] = []

    def add_rule(self, name: str, metric: str, condition: str, threshold: float,
                 severity: AlertSeverity = AlertSeverity.MEDIUM,
                 channels: Optional[List[AlertChannel]] = None,
                 check_interval: int = 300,
                 max_consecutive: int = 3,
                 cooldown: int = 3600) -> AlertRule:
        """Create and add a new alert rule"""
        rule = AlertRule(
            name=name,
            metric=metric,
            condition=condition,
            threshold=threshold,
            severity=severity,
            channels=channels or [AlertChannel.EMAIL],
            check_interval=check_interval,
            max_consecutive_before_alert=max_consecutive,
            cooldown=cooldown
        )
        self.rules[rule.id] = rule
        logger.info(f"Alert rule added: {name} (ID: {rule.id})")
        return rule

    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get alert rule by ID"""
        return self.rules.get(rule_id)

    def list_rules(self) -> List[AlertRule]:
        """List all alert rules"""
        return list(self.rules.values())

    def enable_rule(self, rule_id: str) -> bool:
        """Enable an alert rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            logger.info(f"Rule enabled: {rule_id}")
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable an alert rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            logger.info(f"Rule disabled: {rule_id}")
            return True
        return False

    def delete_rule(self, rule_id: str) -> bool:
        """Delete an alert rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Rule deleted: {rule_id}")
            return True
        return False

    def check_condition(self, rule: AlertRule, current_value: Any) -> bool:
        """Evaluate if current value violates rule condition"""
        try:
            current = float(current_value)
            threshold = float(rule.threshold)

            conditions = {
                "greater_than": lambda v, t: v > t,
                "less_than": lambda v, t: v < t,
                "equals": lambda v, t: v == t,
                "greater_equal": lambda v, t: v >= t,
                "less_equal": lambda v, t: v <= t,
                "not_equal": lambda v, t: v != t,
                "between": lambda v, t: v > t - 10 and v < t + 10,  # Within 10% range
            }

            check_fn = conditions.get(rule.condition)
            if check_fn:
                return check_fn(current, threshold)
            else:
                logger.warning(f"Unknown condition: {rule.condition}")
                return False
        except (ValueError, TypeError) as e:
            logger.error(f"Error evaluating condition: {str(e)}")
            return False

    def evaluate_rule(self, rule_id: str, current_value: Any) -> Optional[Alert]:
        """Evaluate a rule and trigger alert if threshold is crossed"""
        rule = self.rules.get(rule_id)
        if not rule or not rule.enabled:
            return None

        rule.last_checked = datetime.now()
        violated = self.check_condition(rule, current_value)

        if violated:
            rule.consecutive_violations += 1
        else:
            rule.consecutive_violations = 0

        # Check if we should trigger alert
        if rule.consecutive_violations >= rule.max_consecutive_before_alert:
            # Check cooldown
            last_alert = self.last_alert_times.get(rule_id)
            if last_alert and (datetime.now() - last_alert).total_seconds() < rule.cooldown:
                logger.debug(f"Alert cooldown active for rule: {rule_id}")
                return None

            # Create and trigger alert
            alert = Alert(
                rule_id=rule_id,
                rule_name=rule.name,
                severity=rule.severity,
                message=f"{rule.name}: {rule.metric} {rule.condition} {rule.threshold}",
                current_value=current_value,
                threshold=rule.threshold,
                metadata={"rule": rule.to_dict()}
            )

            self.alerts[alert.id] = alert
            self.last_alert_times[rule_id] = datetime.now()

            # Send notifications
            self._send_notifications(rule, alert)

            # Notify listeners
            for listener in self.listeners:
                try:
                    listener(alert)
                except Exception as e:
                    logger.error(f"Error calling alert listener: {str(e)}")

            logger.warning(f"Alert triggered: {rule.name} (severity: {rule.severity.value})")
            return alert

        return None

    def _send_notifications(self, rule: AlertRule, alert: Alert):
        """Send alert through configured channels"""
        for channel in rule.channels:
            if channel in self.channels:
                # In production, would get actual recipient list from config/DB
                recipients = os.getenv("ALERT_EMAIL_RECIPIENTS", "admin@example.com").split(",")
                try:
                    self.channels[channel].send(alert, recipients)
                except Exception as e:
                    logger.error(f"Error sending alert via {channel.value}: {str(e)}")

    def acknowledge_alert(self, alert_id: str, user_id: Optional[str] = None) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.acknowledged = True
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = user_id
            logger.info(f"Alert acknowledged: {alert_id} by {user_id}")
            return True
        return False

    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get all unacknowledged alerts, optionally filtered by severity"""
        alerts = [a for a in self.alerts.values() if not a.acknowledged]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return sorted(alerts, key=lambda x: x.triggered_at, reverse=True)

    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get recent alert history"""
        alerts = sorted(self.alerts.values(), key=lambda x: x.triggered_at, reverse=True)
        return alerts[:limit]

    def subscribe(self, callback: Callable[[Alert], None]):
        """Subscribe to alert events"""
        self.listeners.append(callback)

    def unsubscribe(self, callback: Callable[[Alert], None]):
        """Unsubscribe from alert events"""
        if callback in self.listeners:
            self.listeners.remove(callback)

    def get_statistics(self) -> Dict:
        """Get alert statistics"""
        total = len(self.alerts)
        acknowledged = sum(1 for a in self.alerts.values() if a.acknowledged)
        by_severity = {}
        for severity in AlertSeverity:
            by_severity[severity.value] = sum(1 for a in self.alerts.values() if a.severity == severity)

        return {
            "total_alerts": total,
            "acknowledged": acknowledged,
            "unacknowledged": total - acknowledged,
            "by_severity": by_severity,
            "active_rules": len([r for r in self.rules.values() if r.enabled])
        }


# Global instance
_alert_manager: Optional[AlertManager] = None


def get_alert_manager(redis_client=None) -> AlertManager:
    """Get or create global alert manager"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager(redis_client)
    return _alert_manager
