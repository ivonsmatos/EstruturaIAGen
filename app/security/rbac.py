"""
Role-Based Access Control (RBAC) System for EstruturaIAGen
Implements fine-grained permissions and access management
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional, Callable
import uuid
import logging
import hashlib
from functools import wraps

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Resource types in the system"""
    DASHBOARD = "dashboard"
    REPORTS = "reports"
    SETTINGS = "settings"
    USERS = "users"
    ALERTS = "alerts"
    AUDIT_LOG = "audit_log"
    CHAT = "chat"
    ANALYTICS = "analytics"
    EXPORT = "export"
    ADMIN = "admin"


class Action(Enum):
    """Actions that can be performed"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    EXPORT = "export"
    SHARE = "share"
    ADMIN = "admin"


class RoleType(Enum):
    """Built-in role types"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    POWER_USER = "power_user"
    USER = "user"
    VIEWER = "viewer"
    CUSTOM = "custom"


@dataclass
class Permission:
    """Represents a permission (resource + action)"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resource: ResourceType = ResourceType.DASHBOARD
    action: Action = Action.READ
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def __hash__(self):
        return hash(f"{self.resource.value}:{self.action.value}")

    def __eq__(self, other):
        if isinstance(other, Permission):
            return self.resource == other.resource and self.action == other.action
        return False

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'resource': self.resource.value,
            'action': self.action.value,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class Role:
    """Represents a role with associated permissions"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    role_type: RoleType = RoleType.CUSTOM
    description: str = ""
    permissions: Set[Permission] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def has_permission(self, resource: ResourceType, action: Action) -> bool:
        """Check if role has specific permission"""
        return any(p.resource == resource and p.action == action for p in self.permissions)

    def add_permission(self, permission: Permission):
        """Add permission to role"""
        self.permissions.add(permission)
        self.updated_at = datetime.now()

    def remove_permission(self, permission: Permission):
        """Remove permission from role"""
        self.permissions.discard(permission)
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'role_type': self.role_type.value,
            'description': self.description,
            'permissions': [p.to_dict() for p in self.permissions],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }


@dataclass
class User:
    """Represents a user with roles"""
    id: int = 0
    username: str = ""
    email: str = ""
    password_hash: str = ""
    roles: List[Role] = field(default_factory=list)
    is_active: bool = True
    is_2fa_enabled: bool = False
    two_fa_secret: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)

    def has_permission(self, resource: ResourceType, action: Action) -> bool:
        """Check if user has permission across all roles"""
        return any(role.has_permission(resource, action) for role in self.roles if role.is_active)

    def has_role(self, role_type: RoleType) -> bool:
        """Check if user has specific role type"""
        return any(r.role_type == role_type for r in self.roles)

    def add_role(self, role: Role):
        """Add role to user"""
        if role not in self.roles:
            self.roles.append(role)
            self.updated_at = datetime.now()

    def remove_role(self, role: Role):
        """Remove role from user"""
        if role in self.roles:
            self.roles.remove(role)
            self.updated_at = datetime.now()

    def get_all_permissions(self) -> Set[Permission]:
        """Get all permissions across all roles"""
        permissions = set()
        for role in self.roles:
            if role.is_active:
                permissions.update(role.permissions)
        return permissions

    def to_dict(self, include_password=False) -> Dict:
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'roles': [r.to_dict() for r in self.roles],
            'is_active': self.is_active,
            'is_2fa_enabled': self.is_2fa_enabled,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        if include_password:
            data['password_hash'] = self.password_hash
        return data


@dataclass
class AuditLog:
    """Audit log entry for compliance"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int = 0
    action: str = ""
    resource: str = ""
    resource_id: str = ""
    changes: Dict = field(default_factory=dict)
    status: str = "success"  # success, denied, error
    denial_reason: Optional[str] = None
    ip_address: str = ""
    user_agent: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource': self.resource,
            'resource_id': self.resource_id,
            'changes': self.changes,
            'status': self.status,
            'denial_reason': self.denial_reason,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


class RBACManager:
    """Central RBAC management system"""

    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.users: Dict[int, User] = {}
        self.audit_logs: List[AuditLog] = []
        self.permissions_cache: Dict[str, Set[Permission]] = {}
        self._initialize_default_roles()

    def _initialize_default_roles(self):
        """Initialize built-in roles"""
        # Super Admin - full access
        super_admin_role = Role(
            name="Super Admin",
            role_type=RoleType.SUPER_ADMIN,
            description="Full system access"
        )
        for resource in ResourceType:
            for action in Action:
                super_admin_role.add_permission(Permission(
                    resource=resource,
                    action=action,
                    description=f"{action.value} {resource.value}"
                ))
        self.roles[super_admin_role.id] = super_admin_role

        # Admin - most features except user management
        admin_role = Role(
            name="Admin",
            role_type=RoleType.ADMIN,
            description="Administrative access"
        )
        for resource in ResourceType:
            if resource != ResourceType.USERS:
                for action in [Action.READ, Action.CREATE, Action.UPDATE, Action.DELETE, Action.EXECUTE]:
                    admin_role.add_permission(Permission(
                        resource=resource,
                        action=action
                    ))
        self.roles[admin_role.id] = admin_role

        # Power User - create/edit own resources
        power_user_role = Role(
            name="Power User",
            role_type=RoleType.POWER_USER,
            description="Advanced user capabilities"
        )
        for resource in [ResourceType.DASHBOARD, ResourceType.REPORTS, ResourceType.CHAT,
                        ResourceType.ANALYTICS, ResourceType.EXPORT]:
            for action in [Action.READ, Action.CREATE, Action.UPDATE, Action.EXPORT]:
                power_user_role.add_permission(Permission(
                    resource=resource,
                    action=action
                ))
        self.roles[power_user_role.id] = power_user_role

        # User - basic access
        user_role = Role(
            name="User",
            role_type=RoleType.USER,
            description="Standard user access"
        )
        for resource in [ResourceType.DASHBOARD, ResourceType.CHAT, ResourceType.EXPORT]:
            for action in [Action.READ, Action.CREATE, Action.EXPORT]:
                user_role.add_permission(Permission(
                    resource=resource,
                    action=action
                ))
        self.roles[user_role.id] = user_role

        # Viewer - read-only access
        viewer_role = Role(
            name="Viewer",
            role_type=RoleType.VIEWER,
            description="Read-only access"
        )
        for resource in [ResourceType.DASHBOARD, ResourceType.REPORTS, ResourceType.ANALYTICS]:
            viewer_role.add_permission(Permission(
                resource=resource,
                action=Action.READ
            ))
        self.roles[viewer_role.id] = viewer_role

        logger.info(f"Initialized {len(self.roles)} default roles")

    def create_role(self, name: str, description: str = "", role_type: RoleType = RoleType.CUSTOM) -> Role:
        """Create a new custom role"""
        role = Role(name=name, description=description, role_type=role_type)
        self.roles[role.id] = role
        logger.info(f"Role created: {name} (ID: {role.id})")
        return role

    def get_role(self, role_id: str) -> Optional[Role]:
        """Get role by ID"""
        return self.roles.get(role_id)

    def get_role_by_type(self, role_type: RoleType) -> Optional[Role]:
        """Get built-in role by type"""
        for role in self.roles.values():
            if role.role_type == role_type:
                return role
        return None

    def list_roles(self) -> List[Role]:
        """List all roles"""
        return list(self.roles.values())

    def delete_role(self, role_id: str) -> bool:
        """Delete a role"""
        if role_id in self.roles:
            role = self.roles[role_id]
            # Can't delete built-in roles
            if role.role_type != RoleType.CUSTOM:
                logger.warning(f"Cannot delete built-in role: {role.name}")
                return False
            del self.roles[role_id]
            logger.info(f"Role deleted: {role.name}")
            return True
        return False

    def create_user(self, user_id: int, username: str, email: str, 
                    password: str, roles: Optional[List[Role]] = None) -> User:
        """Create a new user"""
        password_hash = self._hash_password(password)
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            roles=roles or []
        )
        self.users[user_id] = user
        logger.info(f"User created: {username} (ID: {user_id})")
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def list_users(self, active_only: bool = True) -> List[User]:
        """List all users"""
        users = list(self.users.values())
        if active_only:
            users = [u for u in users if u.is_active]
        return users

    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user attributes"""
        user = self.get_user(user_id)
        if not user:
            return False

        for key, value in kwargs.items():
            if hasattr(user, key) and key != 'id':
                setattr(user, key, value)

        user.updated_at = datetime.now()
        logger.info(f"User updated: {user.username}")
        return True

    def add_role_to_user(self, user_id: int, role_id: str) -> bool:
        """Add role to user"""
        user = self.get_user(user_id)
        role = self.get_role(role_id)

        if user and role:
            user.add_role(role)
            self._invalidate_cache(f"user_{user_id}")
            logger.info(f"Role '{role.name}' added to user '{user.username}'")
            return True
        return False

    def remove_role_from_user(self, user_id: int, role_id: str) -> bool:
        """Remove role from user"""
        user = self.get_user(user_id)
        role = self.get_role(role_id)

        if user and role:
            user.remove_role(role)
            self._invalidate_cache(f"user_{user_id}")
            logger.info(f"Role '{role.name}' removed from user '{user.username}'")
            return True
        return False

    def add_permission_to_role(self, role_id: str, resource: ResourceType, action: Action) -> bool:
        """Add permission to role"""
        role = self.get_role(role_id)
        if role:
            permission = Permission(resource=resource, action=action)
            role.add_permission(permission)
            self._invalidate_cache(f"role_{role_id}")
            logger.info(f"Permission {action.value}:{resource.value} added to role {role.name}")
            return True
        return False

    def remove_permission_from_role(self, role_id: str, resource: ResourceType, action: Action) -> bool:
        """Remove permission from role"""
        role = self.get_role(role_id)
        if role:
            permission = Permission(resource=resource, action=action)
            role.remove_permission(permission)
            self._invalidate_cache(f"role_{role_id}")
            logger.info(f"Permission {action.value}:{resource.value} removed from role {role.name}")
            return True
        return False

    def check_permission(self, user_id: int, resource: ResourceType, action: Action,
                        ip_address: str = "", user_agent: str = "") -> bool:
        """Check if user has permission"""
        user = self.get_user(user_id)
        if not user or not user.is_active:
            self._log_denied_access(user_id, resource, action, "user_inactive", ip_address, user_agent)
            return False

        has_perm = user.has_permission(resource, action)

        if not has_perm:
            self._log_denied_access(user_id, resource, action, "permission_denied", ip_address, user_agent)
        else:
            self._log_access(user_id, resource, action, ip_address, user_agent)

        return has_perm

    def enable_2fa(self, user_id: int) -> Optional[str]:
        """Enable 2FA for user and return secret"""
        import secrets
        user = self.get_user(user_id)
        if user:
            user.is_2fa_enabled = True
            user.two_fa_secret = secrets.token_urlsafe(32)
            logger.info(f"2FA enabled for user: {user.username}")
            return user.two_fa_secret
        return None

    def disable_2fa(self, user_id: int) -> bool:
        """Disable 2FA for user"""
        user = self.get_user(user_id)
        if user:
            user.is_2fa_enabled = False
            user.two_fa_secret = None
            logger.info(f"2FA disabled for user: {user.username}")
            return True
        return False

    def verify_password(self, user_id: int, password: str) -> bool:
        """Verify user password"""
        user = self.get_user(user_id)
        if user:
            return user.password_hash == self._hash_password(password)
        return False

    def update_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Update user password"""
        if self.verify_password(user_id, old_password):
            user = self.get_user(user_id)
            if user:
                user.password_hash = self._hash_password(new_password)
                user.updated_at = datetime.now()
                logger.info(f"Password updated for user: {user.username}")
                return True
        return False

    def _log_access(self, user_id: int, resource: ResourceType, action: Action,
                   ip_address: str, user_agent: str):
        """Log successful access"""
        log = AuditLog(
            user_id=user_id,
            action=action.value,
            resource=resource.value,
            status="success",
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.audit_logs.append(log)

    def _log_denied_access(self, user_id: int, resource: ResourceType, action: Action,
                          reason: str, ip_address: str, user_agent: str):
        """Log denied access"""
        log = AuditLog(
            user_id=user_id,
            action=action.value,
            resource=resource.value,
            status="denied",
            denial_reason=reason,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.audit_logs.append(log)

    def get_audit_log(self, user_id: Optional[int] = None, limit: int = 100) -> List[AuditLog]:
        """Get audit log entries"""
        logs = self.audit_logs[-limit:] if not user_id else [l for l in self.audit_logs if l.user_id == user_id][-limit:]
        return sorted(logs, key=lambda x: x.timestamp, reverse=True)

    def get_user_statistics(self) -> Dict:
        """Get user and role statistics"""
        return {
            'total_users': len(self.users),
            'active_users': sum(1 for u in self.users.values() if u.is_active),
            'users_with_2fa': sum(1 for u in self.users.values() if u.is_2fa_enabled),
            'total_roles': len(self.roles),
            'built_in_roles': sum(1 for r in self.roles.values() if r.role_type != RoleType.CUSTOM),
            'custom_roles': sum(1 for r in self.roles.values() if r.role_type == RoleType.CUSTOM),
            'total_permissions': sum(len(r.permissions) for r in self.roles.values())
        }

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password with salt"""
        salt = "estrutura_iagen_salt"  # In production, use proper salt management
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

    def _invalidate_cache(self, key: str):
        """Invalidate permission cache"""
        if key in self.permissions_cache:
            del self.permissions_cache[key]


# Global instance
_rbac_manager: Optional[RBACManager] = None


def get_rbac_manager() -> RBACManager:
    """Get or create global RBAC manager"""
    global _rbac_manager
    if _rbac_manager is None:
        _rbac_manager = RBACManager()
    return _rbac_manager


# Decorators for permission checking
def require_permission(resource: ResourceType, action: Action):
    """Decorator to check permission before executing function"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, user_id: int = None, **kwargs):
            rbac = get_rbac_manager()
            if user_id and rbac.check_permission(user_id, resource, action):
                return func(*args, user_id=user_id, **kwargs)
            else:
                raise PermissionError(f"User {user_id} lacks permission to {action.value} {resource.value}")
        return wrapper
    return decorator


def require_role(role_type: RoleType):
    """Decorator to check if user has specific role"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, user_id: int = None, **kwargs):
            rbac = get_rbac_manager()
            user = rbac.get_user(user_id) if user_id else None
            if user and user.has_role(role_type):
                return func(*args, user_id=user_id, **kwargs)
            else:
                raise PermissionError(f"User {user_id} does not have role {role_type.value}")
        return wrapper
    return decorator
