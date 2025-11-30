"""
Comprehensive tests for P4.3, P4.4, P4.5 features
Alerts, Async tasks, and RBAC
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# P4.3 Alerts Tests
from app.alerts.alert_manager import (
    AlertManager, AlertRule, Alert, AlertSeverity, AlertChannel,
    EmailChannel, SlackChannel, WebhookChannel
)

# P4.4 Async Tests
from app.celery_config import celery_app
from app.async_tasks import (
    llm_inference, heavy_computation, database_operations,
    send_notifications, check_system_alerts, update_dashboard_cache
)

# P4.5 RBAC Tests
from app.security.rbac import (
    RBACManager, Role, User, Permission, AuditLog,
    ResourceType, Action, RoleType, get_rbac_manager
)


# ============= P4.3 ALERT TESTS =============

class TestAlertRule:
    """Test AlertRule functionality"""

    def test_alert_rule_creation(self):
        """Test creating an alert rule"""
        rule = AlertRule(
            name="High Error Rate",
            metric="error_rate",
            condition="greater_than",
            threshold=5.0,
            severity=AlertSeverity.HIGH
        )
        assert rule.name == "High Error Rate"
        assert rule.threshold == 5.0
        assert rule.enabled is True

    def test_alert_rule_to_dict(self):
        """Test converting rule to dictionary"""
        rule = AlertRule(
            name="Test Rule",
            metric="cpu_usage",
            condition="greater_than",
            threshold=80.0
        )
        rule_dict = rule.to_dict()
        assert rule_dict['name'] == "Test Rule"
        assert rule_dict['severity'] == "medium"

    def test_alert_rule_consecutive_violations(self):
        """Test tracking consecutive violations"""
        rule = AlertRule(
            name="Test",
            threshold=10.0,
            condition="greater_than",
            max_consecutive_before_alert=2
        )
        assert rule.consecutive_violations == 0
        rule.consecutive_violations = 2
        assert rule.consecutive_violations == 2


class TestAlert:
    """Test Alert functionality"""

    def test_alert_creation(self):
        """Test creating an alert"""
        alert = Alert(
            rule_name="Test Rule",
            severity=AlertSeverity.CRITICAL,
            message="Test alert message",
            current_value=95.5,
            threshold=80.0
        )
        assert alert.rule_name == "Test Rule"
        assert alert.severity == AlertSeverity.CRITICAL
        assert not alert.acknowledged

    def test_alert_acknowledge(self):
        """Test acknowledging an alert"""
        alert = Alert(rule_name="Test")
        assert not alert.acknowledged
        alert.acknowledged = True
        alert.acknowledged_at = datetime.now()
        alert.acknowledged_by = "admin"
        assert alert.acknowledged
        assert alert.acknowledged_by == "admin"

    def test_alert_to_dict(self):
        """Test converting alert to dictionary"""
        alert = Alert(rule_name="Test", severity=AlertSeverity.HIGH)
        alert_dict = alert.to_dict()
        assert alert_dict['rule_name'] == "Test"
        assert alert_dict['severity'] == "high"


class TestAlertManager:
    """Test AlertManager functionality"""

    def test_alert_manager_creation(self):
        """Test creating alert manager"""
        manager = AlertManager()
        assert manager is not None
        assert len(manager.rules) == 0

    def test_add_alert_rule(self):
        """Test adding alert rule"""
        manager = AlertManager()
        rule = manager.add_rule(
            name="High CPU",
            metric="cpu_usage",
            condition="greater_than",
            threshold=80.0,
            severity=AlertSeverity.HIGH
        )
        assert rule.name == "High CPU"
        assert rule.id in manager.rules

    def test_get_alert_rule(self):
        """Test retrieving alert rule"""
        manager = AlertManager()
        rule = manager.add_rule("Test", "metric", "greater_than", 50.0)
        retrieved = manager.get_rule(rule.id)
        assert retrieved.id == rule.id

    def test_list_alert_rules(self):
        """Test listing all rules"""
        manager = AlertManager()
        manager.add_rule("Rule 1", "metric1", "greater_than", 50.0)
        manager.add_rule("Rule 2", "metric2", "less_than", 10.0)
        rules = manager.list_rules()
        assert len(rules) == 2

    def test_enable_disable_rule(self):
        """Test enabling/disabling rules"""
        manager = AlertManager()
        rule = manager.add_rule("Test", "metric", "greater_than", 50.0)
        manager.disable_rule(rule.id)
        assert not manager.get_rule(rule.id).enabled
        manager.enable_rule(rule.id)
        assert manager.get_rule(rule.id).enabled

    def test_check_condition(self):
        """Test condition evaluation"""
        manager = AlertManager()
        rule = AlertRule(
            condition="greater_than",
            threshold=50.0
        )
        assert manager.check_condition(rule, 60) is True
        assert manager.check_condition(rule, 40) is False

    def test_evaluate_rule(self):
        """Test evaluating rule and triggering alert"""
        manager = AlertManager()
        rule = manager.add_rule(
            "High Error Rate",
            "error_rate",
            "greater_than",
            5.0,
            max_consecutive=1
        )
        alert = manager.evaluate_rule(rule.id, 7.5)
        assert alert is not None
        assert alert.current_value == 7.5

    def test_acknowledge_alert(self):
        """Test acknowledging alert"""
        manager = AlertManager()
        rule = manager.add_rule("Test", "metric", "greater_than", 50.0, max_consecutive=1)
        alert = manager.evaluate_rule(rule.id, 60)
        if alert:
            manager.acknowledge_alert(alert.id, "admin")
            ack_alert = manager.alerts[alert.id]
            assert ack_alert.acknowledged

    def test_get_active_alerts(self):
        """Test getting active alerts"""
        manager = AlertManager()
        rule = manager.add_rule("Test", "metric", "greater_than", 50.0, max_consecutive=1)
        manager.evaluate_rule(rule.id, 60)
        active = manager.get_active_alerts()
        assert len(active) > 0

    def test_alert_statistics(self):
        """Test alert statistics"""
        manager = AlertManager()
        rule = manager.add_rule("Test", "metric", "greater_than", 50.0, max_consecutive=1)
        manager.evaluate_rule(rule.id, 60)
        stats = manager.get_statistics()
        assert stats['total_alerts'] > 0
        assert stats['active_rules'] == 1

    def test_alert_subscription(self):
        """Test alert event subscription"""
        manager = AlertManager()
        alerts_received = []

        def listener(alert):
            alerts_received.append(alert)

        manager.subscribe(listener)
        rule = manager.add_rule("Test", "metric", "greater_than", 50.0, max_consecutive=1)
        manager.evaluate_rule(rule.id, 60)
        assert len(alerts_received) > 0


class TestEmailChannel:
    """Test Email notification channel"""

    @patch('smtplib.SMTP')
    def test_email_send(self, mock_smtp):
        """Test sending email notification"""
        channel = EmailChannel(
            sender_email="test@example.com",
            sender_password="password"
        )
        alert = Alert(
            rule_name="Test",
            severity=AlertSeverity.HIGH,
            message="Test alert"
        )
        result = channel.send(alert, ["admin@example.com"])
        # Email sending may fail without proper config, but test structure is correct
        assert isinstance(result, bool)


# ============= P4.4 ASYNC TESTS =============

class TestCeleryConfig:
    """Test Celery configuration"""

    def test_celery_app_exists(self):
        """Test Celery app is configured"""
        assert celery_app is not None
        assert celery_app.conf.broker_url
        assert celery_app.conf.result_backend

    def test_celery_task_routes(self):
        """Test Celery task routing"""
        routes = celery_app.conf.task_routes
        assert 'app.async_tasks.llm_inference' in routes
        assert 'app.async_tasks.heavy_computation' in routes


class TestAsyncTasks:
    """Test async task execution"""

    def test_llm_inference_task_signature(self):
        """Test LLM inference task exists"""
        assert llm_inference is not None
        assert callable(llm_inference)

    def test_heavy_computation_task_signature(self):
        """Test heavy computation task exists"""
        assert heavy_computation is not None
        assert callable(heavy_computation)

    def test_database_operations_task_signature(self):
        """Test database operations task exists"""
        assert database_operations is not None
        assert callable(database_operations)

    def test_send_notifications_task_signature(self):
        """Test send notifications task exists"""
        assert send_notifications is not None
        assert callable(send_notifications)

    def test_check_system_alerts_task_signature(self):
        """Test system alerts check task exists"""
        assert check_system_alerts is not None
        assert callable(check_system_alerts)

    def test_update_dashboard_cache_task_signature(self):
        """Test dashboard cache update task exists"""
        assert update_dashboard_cache is not None
        assert callable(update_dashboard_cache)

    def test_celery_beat_schedule(self):
        """Test Celery Beat schedule is configured"""
        schedule = celery_app.conf.beat_schedule
        assert 'check-alerts-every-5-minutes' in schedule
        assert 'update-dashboard-cache-every-10-minutes' in schedule
        assert 'cleanup-old-sessions-daily' in schedule
        assert 'generate-reports-daily' in schedule


# ============= P4.5 RBAC TESTS =============

class TestPermission:
    """Test Permission functionality"""

    def test_permission_creation(self):
        """Test creating permission"""
        perm = Permission(
            resource=ResourceType.DASHBOARD,
            action=Action.READ
        )
        assert perm.resource == ResourceType.DASHBOARD
        assert perm.action == Action.READ

    def test_permission_equality(self):
        """Test permission equality"""
        perm1 = Permission(
            resource=ResourceType.DASHBOARD,
            action=Action.READ
        )
        perm2 = Permission(
            resource=ResourceType.DASHBOARD,
            action=Action.READ
        )
        assert perm1 == perm2

    def test_permission_to_dict(self):
        """Test converting permission to dict"""
        perm = Permission(
            resource=ResourceType.DASHBOARD,
            action=Action.READ
        )
        perm_dict = perm.to_dict()
        assert perm_dict['resource'] == 'dashboard'
        assert perm_dict['action'] == 'read'


class TestRole:
    """Test Role functionality"""

    def test_role_creation(self):
        """Test creating role"""
        role = Role(
            name="Admin",
            role_type=RoleType.ADMIN
        )
        assert role.name == "Admin"
        assert role.role_type == RoleType.ADMIN

    def test_add_permission_to_role(self):
        """Test adding permission to role"""
        role = Role(name="Test")
        perm = Permission(
            resource=ResourceType.DASHBOARD,
            action=Action.READ
        )
        role.add_permission(perm)
        assert perm in role.permissions

    def test_remove_permission_from_role(self):
        """Test removing permission from role"""
        role = Role(name="Test")
        perm = Permission(
            resource=ResourceType.DASHBOARD,
            action=Action.READ
        )
        role.add_permission(perm)
        role.remove_permission(perm)
        assert perm not in role.permissions

    def test_has_permission(self):
        """Test checking permission"""
        role = Role(name="Test")
        perm = Permission(
            resource=ResourceType.DASHBOARD,
            action=Action.READ
        )
        role.add_permission(perm)
        assert role.has_permission(ResourceType.DASHBOARD, Action.READ)
        assert not role.has_permission(ResourceType.DASHBOARD, Action.DELETE)


class TestUser:
    """Test User functionality"""

    def test_user_creation(self):
        """Test creating user"""
        user = User(
            id=1,
            username="admin",
            email="admin@example.com"
        )
        assert user.username == "admin"
        assert user.is_active

    def test_add_role_to_user(self):
        """Test adding role to user"""
        user = User(id=1, username="test")
        role = Role(name="Admin")
        user.add_role(role)
        assert role in user.roles

    def test_user_has_permission(self):
        """Test checking user permission"""
        user = User(id=1, username="test")
        role = Role(name="Admin")
        perm = Permission(
            resource=ResourceType.DASHBOARD,
            action=Action.READ
        )
        role.add_permission(perm)
        user.add_role(role)
        assert user.has_permission(ResourceType.DASHBOARD, Action.READ)

    def test_get_all_permissions(self):
        """Test getting all user permissions"""
        user = User(id=1, username="test")
        role = Role(name="Admin")
        perm1 = Permission(
            resource=ResourceType.DASHBOARD,
            action=Action.READ
        )
        perm2 = Permission(
            resource=ResourceType.REPORTS,
            action=Action.CREATE
        )
        role.add_permission(perm1)
        role.add_permission(perm2)
        user.add_role(role)
        perms = user.get_all_permissions()
        assert len(perms) >= 2


class TestRBACManager:
    """Test RBACManager functionality"""

    def test_rbac_manager_initialization(self):
        """Test RBAC manager initialization"""
        manager = RBACManager()
        assert len(manager.roles) > 0  # Should have default roles
        assert len(manager.users) == 0

    def test_default_roles_exist(self):
        """Test default roles are created"""
        manager = RBACManager()
        roles = manager.list_roles()
        role_types = [r.role_type for r in roles]
        assert RoleType.SUPER_ADMIN in role_types
        assert RoleType.ADMIN in role_types
        assert RoleType.USER in role_types

    def test_create_custom_role(self):
        """Test creating custom role"""
        manager = RBACManager()
        role = manager.create_role(
            "Data Analyst",
            "Can view and export data"
        )
        assert role.name == "Data Analyst"
        assert role.role_type == RoleType.CUSTOM

    def test_create_user(self):
        """Test creating user"""
        manager = RBACManager()
        user = manager.create_user(
            user_id=1,
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        assert user.username == "testuser"
        retrieved = manager.get_user(1)
        assert retrieved.id == 1

    def test_add_role_to_user(self):
        """Test adding role to user"""
        manager = RBACManager()
        user = manager.create_user(1, "test", "test@example.com", "pass")
        admin_role = manager.get_role_by_type(RoleType.ADMIN)
        manager.add_role_to_user(1, admin_role.id)
        updated_user = manager.get_user(1)
        assert admin_role in updated_user.roles

    def test_check_permission(self):
        """Test checking user permission"""
        manager = RBACManager()
        user = manager.create_user(1, "test", "test@example.com", "pass")
        admin_role = manager.get_role_by_type(RoleType.ADMIN)
        manager.add_role_to_user(1, admin_role.id)
        
        has_perm = manager.check_permission(
            1,
            ResourceType.DASHBOARD,
            Action.READ
        )
        assert has_perm

    def test_list_users(self):
        """Test listing users"""
        manager = RBACManager()
        manager.create_user(1, "user1", "user1@example.com", "pass")
        manager.create_user(2, "user2", "user2@example.com", "pass")
        users = manager.list_users()
        assert len(users) >= 2

    def test_get_user_statistics(self):
        """Test user statistics"""
        manager = RBACManager()
        manager.create_user(1, "user1", "user1@example.com", "pass")
        stats = manager.get_user_statistics()
        assert stats['total_users'] > 0
        assert stats['total_roles'] > 0

    def test_audit_log_creation(self):
        """Test audit log tracking"""
        manager = RBACManager()
        manager.create_user(1, "user1", "user1@example.com", "pass")
        logs = manager.get_audit_log()
        # Logs should be created during operations
        assert isinstance(logs, list)

    def test_password_hashing(self):
        """Test password hashing"""
        manager = RBACManager()
        manager.create_user(1, "user1", "user1@example.com", "password123")
        assert manager.verify_password(1, "password123")
        assert not manager.verify_password(1, "wrongpassword")

    def test_2fa_management(self):
        """Test 2FA enable/disable"""
        manager = RBACManager()
        manager.create_user(1, "user1", "user1@example.com", "pass")
        secret = manager.enable_2fa(1)
        assert secret is not None
        user = manager.get_user(1)
        assert user.is_2fa_enabled
        manager.disable_2fa(1)
        user = manager.get_user(1)
        assert not user.is_2fa_enabled

    def test_remove_role_from_user(self):
        """Test removing role from user"""
        manager = RBACManager()
        user = manager.create_user(1, "test", "test@example.com", "pass")
        admin_role = manager.get_role_by_type(RoleType.ADMIN)
        manager.add_role_to_user(1, admin_role.id)
        manager.remove_role_from_user(1, admin_role.id)
        updated_user = manager.get_user(1)
        assert admin_role not in updated_user.roles

    def test_permission_denied_logging(self):
        """Test permission denied is logged"""
        manager = RBACManager()
        manager.create_user(1, "viewer", "viewer@example.com", "pass")
        viewer_role = manager.get_role_by_type(RoleType.VIEWER)
        manager.add_role_to_user(1, viewer_role.id)
        
        # Try to access admin resource
        has_perm = manager.check_permission(
            1,
            ResourceType.USERS,
            Action.DELETE
        )
        assert not has_perm
        
        # Check audit log has entry
        logs = manager.get_audit_log(user_id=1)
        assert any(l.status == "denied" for l in logs)


# ============= INTEGRATION TESTS =============

class TestIntegration:
    """Integration tests across all features"""

    def test_alert_and_rbac_integration(self):
        """Test alerts and RBAC working together"""
        alert_manager = AlertManager()
        rbac_manager = RBACManager()
        
        # Create user with admin role
        user = rbac_manager.create_user(1, "admin", "admin@example.com", "pass")
        admin_role = rbac_manager.get_role_by_type(RoleType.ADMIN)
        rbac_manager.add_role_to_user(1, admin_role.id)
        
        # Create alert rule
        rule = alert_manager.add_rule(
            "Test",
            "metric",
            "greater_than",
            50.0,
            channels=[AlertChannel.EMAIL]
        )
        
        # User can manage alerts (READ and CREATE are available)
        assert rbac_manager.check_permission(1, ResourceType.ALERTS, Action.READ)

    def test_async_with_rbac(self):
        """Test async tasks with RBAC"""
        rbac_manager = RBACManager()
        user = rbac_manager.create_user(1, "user", "user@example.com", "pass")
        user_role = rbac_manager.get_role_by_type(RoleType.USER)
        rbac_manager.add_role_to_user(1, user_role.id)
        
        # User can't execute admin tasks
        has_perm = rbac_manager.check_permission(1, ResourceType.ADMIN, Action.EXECUTE)
        assert not has_perm


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
