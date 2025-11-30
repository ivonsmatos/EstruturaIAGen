"""
RBAC Management UI Components for Dash
User and role management interface
"""

from dash import dcc, html, callback, Input, Output, State, ctx, ALL
import dash_bootstrap_components as dbc
from app.security.rbac import (
    get_rbac_manager, RoleType, ResourceType, Action
)


def create_rbac_panel() -> dbc.Container:
    """Create RBAC management panel"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("👥 Access Control Management", className="mb-4")
            ], width=12)
        ], className="mb-4"),

        # Stats Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Total Users", className="text-muted"),
                        html.H3(id="total-users-stat", children="0"),
                        html.Small("Registered users", className="text-info")
                    ])
                ])
            ], lg=3, md=6, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Active Users", className="text-muted"),
                        html.H3(id="active-users-stat", children="0"),
                        html.Small("Currently active", className="text-success")
                    ])
                ])
            ], lg=3, md=6, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Total Roles", className="text-muted"),
                        html.H3(id="total-roles-stat", children="0"),
                        html.Small("Configured roles", className="text-warning")
                    ])
                ])
            ], lg=3, md=6, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("2FA Enabled", className="text-muted"),
                        html.H3(id="2fa-users-stat", children="0"),
                        html.Small("Enhanced security", className="text-danger")
                    ])
                ])
            ], lg=3, md=6, className="mb-3"),
        ], className="mb-4"),

        # Tabs
        dbc.Tabs([
            # Users Management Tab
            dbc.Tab([
                html.Div([
                    html.H5("User Management", className="mt-4 mb-3"),
                    dbc.Button("Add New User", id="btn-add-user", color="success", className="mb-3"),
                    
                    # Add User Modal
                    dbc.Modal([
                        dbc.ModalHeader(dbc.ModalTitle("Add New User")),
                        dbc.ModalBody([
                            dbc.Form([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Username"),
                                        dbc.Input(id="user-username-input", placeholder="Enter username", type="text")
                                    ], md=6),
                                    dbc.Col([
                                        dbc.Label("Email"),
                                        dbc.Input(id="user-email-input", placeholder="user@example.com", type="email")
                                    ], md=6)
                                ], className="mb-3"),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Password"),
                                        dbc.Input(id="user-password-input", type="password")
                                    ], md=6),
                                    dbc.Col([
                                        dbc.Label("Confirm Password"),
                                        dbc.Input(id="user-password-confirm-input", type="password")
                                    ], md=6)
                                ], className="mb-3"),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Assign Roles"),
                                        dbc.Checklist(id="user-roles-check", options=[])
                                    ], width=12)
                                ], className="mb-3")
                            ])
                        ]),
                        dbc.ModalFooter([
                            dbc.Button("Cancel", id="btn-cancel-user", className="me-2"),
                            dbc.Button("Create User", id="btn-create-user", color="success")
                        ])
                    ], id="modal-add-user", is_open=False),
                    
                    html.Div(id="users-container", children=[
                        html.P("No users found", className="text-muted")
                    ])
                ])
            ], label="👤 Users", tab_id="users"),

            # Roles Management Tab
            dbc.Tab([
                html.Div([
                    html.H5("Role Management", className="mt-4 mb-3"),
                    dbc.Button("Create Custom Role", id="btn-create-role-modal", color="success", className="mb-3"),
                    
                    # Create Role Modal
                    dbc.Modal([
                        dbc.ModalHeader(dbc.ModalTitle("Create Custom Role")),
                        dbc.ModalBody([
                            dbc.Form([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Role Name"),
                                        dbc.Input(id="role-name-input", placeholder="e.g., Data Analyst", type="text")
                                    ], md=6),
                                    dbc.Col([
                                        dbc.Label("Description"),
                                        dbc.Input(id="role-desc-input", placeholder="Role description", type="text")
                                    ], md=6)
                                ], className="mb-3"),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Permissions"),
                                        html.Div(id="role-permissions-check", children=[])
                                    ], width=12)
                                ], className="mb-3")
                            ])
                        ]),
                        dbc.ModalFooter([
                            dbc.Button("Cancel", id="btn-cancel-role-modal", className="me-2"),
                            dbc.Button("Create Role", id="btn-confirm-create-role", color="success")
                        ])
                    ], id="modal-create-role", is_open=False),
                    
                    html.Div(id="roles-container", children=[
                        html.P("No roles found", className="text-muted")
                    ])
                ])
            ], label="🔐 Roles", tab_id="roles"),

            # Audit Log Tab
            dbc.Tab([
                html.Div([
                    html.H5("Audit Log", className="mt-4 mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Input(id="audit-filter-user", placeholder="Filter by user...", type="text")
                        ], md=4),
                        dbc.Col([
                            dbc.Select(
                                id="audit-filter-status",
                                options=[
                                    {"label": "All Status", "value": ""},
                                    {"label": "Success", "value": "success"},
                                    {"label": "Denied", "value": "denied"},
                                    {"label": "Error", "value": "error"}
                                ]
                            )
                        ], md=4),
                        dbc.Col([
                            dbc.Button("Refresh", id="btn-refresh-audit", color="info", className="me-2"),
                            dbc.Button("Export", id="btn-export-audit", color="warning")
                        ], md=4)
                    ], className="mb-3"),
                    html.Div(id="audit-log-container", children=[
                        html.P("No audit log entries", className="text-muted")
                    ])
                ])
            ], label="📋 Audit Log", tab_id="audit"),

            # Security Settings Tab
            dbc.Tab([
                html.Div([
                    html.H5("Security Settings", className="mt-4 mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader(html.H6("Password Policy")),
                                dbc.CardBody([
                                    dbc.Checklist(
                                        id="security-policy-check",
                                        options=[
                                            {"label": " Require strong passwords", "value": "strong"},
                                            {"label": " Enable 2FA", "value": "2fa"},
                                            {"label": " Session timeout", "value": "timeout"},
                                            {"label": " IP whitelist", "value": "ip"}
                                        ],
                                        value=["strong", "2fa"]
                                    )
                                ])
                            ])
                        ], lg=6, className="mb-3"),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader(html.H6("Access Policies")),
                                dbc.CardBody([
                                    dbc.Checklist(
                                        id="access-policy-check",
                                        options=[
                                            {"label": " Audit all access", "value": "audit"},
                                            {"label": " API rate limiting", "value": "ratelimit"},
                                            {"label": " Require approval for admin", "value": "approval"},
                                            {"label": " Log sensitive operations", "value": "sensitive"}
                                        ],
                                        value=["audit", "ratelimit"]
                                    )
                                ])
                            ])
                        ], lg=6, className="mb-3")
                    ])
                ])
            ], label="🔒 Security", tab_id="security")
        ], id="rbac-tabs", active_tab="users", className="mb-4"),

        # Auto-refresh interval
        dcc.Interval(id="rbac-interval", interval=30000, n_intervals=0),

        # Hidden div to store data
        dcc.Store(id="rbac-data-store")
    ], fluid=True)


def register_rbac_callbacks(app):
    """Register RBAC callbacks"""

    # Update statistics
    @app.callback(
        Output("total-users-stat", "children"),
        Output("active-users-stat", "children"),
        Output("total-roles-stat", "children"),
        Output("2fa-users-stat", "children"),
        Input("rbac-interval", "n_intervals")
    )
    def update_rbac_stats(n_intervals):
        rbac = get_rbac_manager()
        stats = rbac.get_user_statistics()

        return (
            stats['total_users'],
            stats['active_users'],
            stats['total_roles'],
            stats['users_with_2fa']
        )

    # Render users
    @app.callback(
        Output("users-container", "children"),
        Input("rbac-interval", "n_intervals")
    )
    def render_users(n_intervals):
        rbac = get_rbac_manager()
        users = rbac.list_users()

        if not users:
            return html.P("No users found", className="text-muted text-center py-5")

        user_items = []
        for user in users:
            roles_text = ", ".join([r.name for r in user.roles]) or "No roles"
            status_badge = "success" if user.is_active else "secondary"
            status_text = "Active" if user.is_active else "Inactive"

            user_items.append(
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6(user.username, className="mb-1"),
                                html.Small(user.email, className="text-muted d-block")
                            ]),
                            dbc.Col([
                                dbc.Badge(status_text, color=status_badge, className="me-2"),
                                dbc.Badge("2FA" if user.is_2fa_enabled else "No 2FA", color="info")
                            ], width="auto")
                        ], justify="between", align="center"),
                        html.Hr(className="my-2"),
                        html.Small([
                            html.Strong("Roles: "),
                            roles_text
                        ], className="d-block mb-2"),
                        html.Small([
                            html.Strong("Created: "),
                            user.created_at.strftime("%Y-%m-%d %H:%M")
                        ], className="d-block"),
                        html.Hr(className="my-2"),
                        dbc.ButtonGroup([
                            dbc.Button("Edit", size="sm", color="info", outline=True),
                            dbc.Button("Reset Password", size="sm", color="warning", outline=True),
                            dbc.Button("Delete", size="sm", color="danger", outline=True)
                        ], size="sm")
                    ])
                ], className="mb-3")
            )

        return user_items

    # Render roles
    @app.callback(
        Output("roles-container", "children"),
        Input("rbac-interval", "n_intervals")
    )
    def render_roles(n_intervals):
        rbac = get_rbac_manager()
        roles = rbac.list_roles()

        if not roles:
            return html.P("No roles found", className="text-muted text-center py-5")

        role_items = []
        for role in roles:
            perm_count = len(role.permissions)
            is_builtin = role.role_type.value != "custom"

            role_items.append(
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6(role.name, className="mb-1"),
                                html.Small(role.description or "No description", className="text-muted d-block")
                            ]),
                            dbc.Col([
                                dbc.Badge(
                                    "Built-in" if is_builtin else "Custom",
                                    color="primary" if is_builtin else "success"
                                ),
                                dbc.Badge(f"{perm_count} permissions", color="info", className="ms-2")
                            ], width="auto")
                        ], justify="between", align="center"),
                        html.Hr(className="my-2"),
                        html.Small("Sample permissions: " + ", ".join([p.action.value for p in list(role.permissions)[:3]]) + "...", 
                                  className="text-muted"),
                        html.Hr(className="my-2"),
                        dbc.ButtonGroup([
                            dbc.Button("View", size="sm", color="info", outline=True),
                            dbc.Button("Edit" if not is_builtin else "Disabled", 
                                      size="sm", color="warning" if not is_builtin else "secondary", 
                                      outline=True, disabled=is_builtin)
                        ], size="sm")
                    ])
                ], className="mb-3")
            )

        return role_items

    # Render audit log
    @app.callback(
        Output("audit-log-container", "children"),
        Input("rbac-interval", "n_intervals"),
        Input("btn-refresh-audit", "n_clicks")
    )
    def render_audit_log(n_intervals, refresh_clicks):
        rbac = get_rbac_manager()
        logs = rbac.get_audit_log(limit=50)

        if not logs:
            return html.P("No audit log entries", className="text-muted text-center py-5")

        log_items = []
        for log in logs:
            status_badge = {
                "success": "success",
                "denied": "danger",
                "error": "warning"
            }.get(log.status, "secondary")

            log_items.append(
                dbc.ListGroupItem([
                    dbc.Row([
                        dbc.Col([
                            html.Strong(f"User {log.user_id}"),
                            html.Br(),
                            html.Small(f"{log.action} on {log.resource}", className="text-muted")
                        ], md=4),
                        dbc.Col([
                            dbc.Badge(log.status.upper(), color=status_badge),
                            html.Br(),
                            html.Small(f"IP: {log.ip_address}", className="text-muted d-block mt-2")
                        ], md=4),
                        dbc.Col([
                            html.Small(log.timestamp.strftime("%Y-%m-%d %H:%M:%S"), className="text-muted")
                        ], md=4, className="text-end")
                    ], align="center")
                ])
            )

        return dbc.ListGroup(log_items)

    # Toggle Add User Modal
    @app.callback(
        Output("modal-add-user", "is_open"),
        Input("btn-add-user", "n_clicks"),
        Input("btn-cancel-user", "n_clicks"),
        Input("btn-create-user", "n_clicks"),
        State("modal-add-user", "is_open"),
        prevent_initial_call=True
    )
    def toggle_user_modal(add_clicks, cancel_clicks, create_clicks, is_open):
        if ctx.triggered:
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if trigger_id == "btn-add-user":
                return True
            elif trigger_id in ["btn-cancel-user", "btn-create-user"]:
                return False
        return is_open

    # Toggle Create Role Modal
    @app.callback(
        Output("modal-create-role", "is_open"),
        Input("btn-create-role-modal", "n_clicks"),
        Input("btn-cancel-role-modal", "n_clicks"),
        Input("btn-confirm-create-role", "n_clicks"),
        State("modal-create-role", "is_open"),
        prevent_initial_call=True
    )
    def toggle_role_modal(create_clicks, cancel_clicks, confirm_clicks, is_open):
        if ctx.triggered:
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if trigger_id == "btn-create-role-modal":
                return True
            elif trigger_id in ["btn-cancel-role-modal", "btn-confirm-create-role"]:
                return False
        return is_open
