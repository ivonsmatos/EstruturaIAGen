"""
Alert UI Components for Dash Dashboard
Displays real-time alerts and alert management interface
"""

from dash import dcc, html, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
from datetime import datetime
from typing import List, Optional, Dict
import plotly.graph_objects as go

from app.alerts.alert_manager import (
    AlertManager, AlertSeverity, AlertChannel, get_alert_manager, Alert, AlertRule
)


def create_alert_badge(severity: AlertSeverity) -> str:
    """Create colored badge for alert severity"""
    colors = {
        AlertSeverity.LOW: "primary",
        AlertSeverity.MEDIUM: "warning",
        AlertSeverity.HIGH: "danger",
        AlertSeverity.CRITICAL: "dark"
    }
    return colors.get(severity, "secondary")


def create_alerts_panel() -> dbc.Container:
    """Create main alerts management panel"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("⚠️ Alert Management System", className="mb-4")
            ], width=12)
        ], className="mb-4"),

        # Stats Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Active Alerts", className="text-muted"),
                        html.H3(id="active-alerts-count", children="0"),
                        html.Small("Unacknowledged", className="text-danger")
                    ])
                ])
            ], lg=3, md=6, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Active Rules", className="text-muted"),
                        html.H3(id="active-rules-count", children="0"),
                        html.Small("Monitoring", className="text-info")
                    ])
                ])
            ], lg=3, md=6, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Critical Alerts", className="text-muted"),
                        html.H3(id="critical-alerts-count", children="0"),
                        html.Small("Require immediate action", className="text-dark")
                    ])
                ])
            ], lg=3, md=6, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Acknowledged", className="text-muted"),
                        html.H3(id="acknowledged-alerts-count", children="0"),
                        html.Small("Out of total", className="text-success")
                    ])
                ])
            ], lg=3, md=6, className="mb-3"),
        ], className="mb-4"),

        # Tabs
        dbc.Tabs([
            # Active Alerts Tab
            dbc.Tab([
                html.Div([
                    html.H5("Active Alerts", className="mt-4 mb-3"),
                    dbc.Button("Refresh", id="btn-refresh-alerts", color="info", className="mb-3"),
                    html.Div(id="alerts-container", children=[
                        html.P("No active alerts", className="text-success")
                    ])
                ])
            ], label="🔴 Active Alerts", tab_id="alerts"),

            # Rules Management Tab
            dbc.Tab([
                html.Div([
                    html.H5("Alert Rules", className="mt-4 mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("Add New Rule", id="btn-add-rule", color="success", className="mb-3")
                        ], width="auto")
                    ]),
                    dbc.Modal([
                        dbc.ModalHeader(dbc.ModalTitle("Create Alert Rule")),
                        dbc.ModalBody([
                            dbc.Form([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Rule Name"),
                                        dbc.Input(id="rule-name-input", placeholder="e.g., High Error Rate", type="text")
                                    ], md=6),
                                    dbc.Col([
                                        dbc.Label("Metric"),
                                        dbc.Select(
                                            id="rule-metric-select",
                                            options=[
                                                {"label": "Error Rate", "value": "error_rate"},
                                                {"label": "Response Time", "value": "response_time"},
                                                {"label": "CPU Usage", "value": "cpu_usage"},
                                                {"label": "Memory Usage", "value": "memory_usage"},
                                                {"label": "Cost", "value": "cost"},
                                                {"label": "Request Count", "value": "request_count"}
                                            ]
                                        )
                                    ], md=6)
                                ], className="mb-3"),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Condition"),
                                        dbc.Select(
                                            id="rule-condition-select",
                                            options=[
                                                {"label": "Greater Than", "value": "greater_than"},
                                                {"label": "Less Than", "value": "less_than"},
                                                {"label": "Equals", "value": "equals"},
                                                {"label": "Greater or Equal", "value": "greater_equal"},
                                                {"label": "Less or Equal", "value": "less_equal"},
                                                {"label": "Not Equal", "value": "not_equal"}
                                            ]
                                        )
                                    ], md=6),
                                    dbc.Col([
                                        dbc.Label("Threshold Value"),
                                        dbc.Input(id="rule-threshold-input", placeholder="e.g., 5", type="number")
                                    ], md=6)
                                ], className="mb-3"),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Severity"),
                                        dbc.Select(
                                            id="rule-severity-select",
                                            options=[
                                                {"label": "Low", "value": "low"},
                                                {"label": "Medium", "value": "medium"},
                                                {"label": "High", "value": "high"},
                                                {"label": "Critical", "value": "critical"}
                                            ],
                                            value="medium"
                                        )
                                    ], md=6),
                                    dbc.Col([
                                        dbc.Label("Check Interval (seconds)"),
                                        dbc.Input(id="rule-interval-input", placeholder="300", type="number", value=300)
                                    ], md=6)
                                ], className="mb-3"),
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Notification Channels"),
                                        dbc.Checklist(
                                            id="rule-channels-check",
                                            options=[
                                                {"label": " Email", "value": "email"},
                                                {"label": " Slack", "value": "slack"},
                                                {"label": " Webhook", "value": "webhook"}
                                            ],
                                            value=["email"],
                                            inline=True
                                        )
                                    ], width=12)
                                ], className="mb-3")
                            ])
                        ]),
                        dbc.ModalFooter([
                            dbc.Button("Cancel", id="btn-cancel-rule", className="me-2"),
                            dbc.Button("Create Rule", id="btn-create-rule", color="success")
                        ])
                    ], id="modal-add-rule", is_open=False),
                    html.Div(id="rules-container", children=[
                        html.P("No alert rules configured", className="text-muted")
                    ])
                ])
            ], label="⚙️ Rules Management", tab_id="rules"),

            # Alert History Tab
            dbc.Tab([
                html.Div([
                    html.H5("Alert History", className="mt-4 mb-3"),
                    dcc.Graph(id="alerts-timeline-graph"),
                    html.Div(id="alerts-history-container", children=[
                        html.P("No alert history", className="text-muted")
                    ])
                ])
            ], label="📊 History & Analytics", tab_id="history")
        ], id="alerts-tabs", active_tab="alerts", className="mb-4"),

        # Auto-refresh interval
        dcc.Interval(id="alerts-interval", interval=10000, n_intervals=0),

        # Hidden div to store alerts data
        dcc.Store(id="alerts-data-store")
    ], fluid=True)


def register_alert_callbacks(app):
    """Register all Dash callbacks for alert UI"""

    # Update alerts stats
    @app.callback(
        Output("active-alerts-count", "children"),
        Output("active-rules-count", "children"),
        Output("critical-alerts-count", "children"),
        Output("acknowledged-alerts-count", "children"),
        Input("alerts-interval", "n_intervals"),
        Input("btn-refresh-alerts", "n_clicks")
    )
    def update_alert_stats(n_intervals, refresh_clicks):
        alert_manager = get_alert_manager()
        stats = alert_manager.get_statistics()

        critical_count = stats['by_severity'].get('critical', 0)
        total = stats['total_alerts']
        acknowledged = stats['acknowledged']

        return (
            stats['unacknowledged'],
            stats['active_rules'],
            critical_count,
            f"{acknowledged}/{total}"
        )

    # Render active alerts
    @app.callback(
        Output("alerts-container", "children"),
        Input("alerts-interval", "n_intervals"),
        Input("btn-refresh-alerts", "n_clicks")
    )
    def render_active_alerts(n_intervals, refresh_clicks):
        alert_manager = get_alert_manager()
        alerts = alert_manager.get_active_alerts()

        if not alerts:
            return html.P("✅ No active alerts", className="text-success text-center py-5")

        alert_items = []
        for alert in alerts:
            severity_badge = create_alert_badge(alert.severity)
            alert_items.append(
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Badge(
                                    alert.severity.value.upper(),
                                    color=severity_badge,
                                    className="me-2"
                                ),
                                html.Strong(alert.rule_name)
                            ], width="auto"),
                            dbc.Col([
                                dbc.Button(
                                    "Acknowledge",
                                    id={"type": "btn-ack-alert", "index": alert.id},
                                    size="sm",
                                    color="success",
                                    outline=True
                                )
                            ], width="auto")
                        ], justify="between"),
                        html.Hr(className="my-2"),
                        html.P(alert.message, className="mb-2"),
                        dbc.Row([
                            dbc.Col([
                                html.Small([
                                    html.Strong("Current: "),
                                    str(alert.current_value)
                                ], className="text-muted me-3")
                            ], width="auto"),
                            dbc.Col([
                                html.Small([
                                    html.Strong("Threshold: "),
                                    str(alert.threshold)
                                ], className="text-muted me-3")
                            ], width="auto"),
                            dbc.Col([
                                html.Small([
                                    html.Strong("Triggered: "),
                                    alert.triggered_at.strftime("%Y-%m-%d %H:%M:%S")
                                ], className="text-muted")
                            ], width="auto")
                        ], className="mt-2")
                    ], className="py-3")
                ], className="mb-3", color=severity_badge, outline=True)
            )

        return alert_items

    # Render alert rules
    @app.callback(
        Output("rules-container", "children"),
        Input("alerts-interval", "n_intervals")
    )
    def render_rules(n_intervals):
        alert_manager = get_alert_manager()
        rules = alert_manager.list_rules()

        if not rules:
            return html.P("No alert rules configured", className="text-muted text-center py-5")

        rule_items = []
        for rule in rules:
            severity_badge = create_alert_badge(rule.severity)
            channels = ", ".join([ch.value for ch in rule.channels])
            status_badge = "success" if rule.enabled else "secondary"
            status_text = "Enabled" if rule.enabled else "Disabled"

            rule_items.append(
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6(rule.name, className="mb-1"),
                                html.Small(f"Metric: {rule.metric}", className="text-muted d-block")
                            ]),
                            dbc.Col([
                                dbc.Badge(status_text, color=status_badge, className="me-2"),
                                dbc.Badge(f"Severity: {rule.severity.value}", color=severity_badge)
                            ], width="auto")
                        ], justify="between", align="center"),
                        html.Hr(className="my-2"),
                        dbc.Row([
                            dbc.Col([
                                html.Small([
                                    html.Strong("Condition: "),
                                    f"{rule.condition} {rule.threshold}"
                                ], className="d-block mb-2")
                            ]),
                            dbc.Col([
                                html.Small([
                                    html.Strong("Channels: "),
                                    channels
                                ], className="d-block mb-2")
                            ]),
                            dbc.Col([
                                html.Small([
                                    html.Strong("Check Interval: "),
                                    f"{rule.check_interval}s"
                                ], className="d-block")
                            ])
                        ]),
                        html.Hr(className="my-2"),
                        dbc.ButtonGroup([
                            dbc.Button(
                                "Enable" if not rule.enabled else "Disable",
                                id={"type": "btn-toggle-rule", "index": rule.id},
                                size="sm",
                                color="info",
                                outline=True
                            ),
                            dbc.Button(
                                "Edit",
                                id={"type": "btn-edit-rule", "index": rule.id},
                                size="sm",
                                color="warning",
                                outline=True
                            ),
                            dbc.Button(
                                "Delete",
                                id={"type": "btn-delete-rule", "index": rule.id},
                                size="sm",
                                color="danger",
                                outline=True
                            )
                        ], size="sm")
                    ], className="py-3")
                ], className="mb-3", outline=True)
            )

        return rule_items

    # Alert history timeline
    @app.callback(
        Output("alerts-timeline-graph", "figure"),
        Input("alerts-interval", "n_intervals")
    )
    def update_alerts_timeline(n_intervals):
        alert_manager = get_alert_manager()
        alerts = alert_manager.get_alert_history(limit=20)

        if not alerts:
            return go.Figure().add_annotation(text="No alert history")

        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        timestamps = []

        for alert in sorted(alerts, key=lambda x: x.triggered_at):
            severity_counts[alert.severity.value] += 1
            timestamps.append(alert.triggered_at.strftime("%Y-%m-%d %H:%M"))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=list(range(1, len(timestamps) + 1)),
            mode='lines+markers',
            name='Alert Count',
            line=dict(color='#FF6B6B', width=2),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title="Alert Timeline",
            xaxis_title="Time",
            yaxis_title="Cumulative Alerts",
            hovermode='x unified',
            template='plotly_white',
            height=300
        )

        return fig

    # Toggle rule enabled status
    @app.callback(
        Output("alerts-data-store", "data"),
        Input({"type": "btn-toggle-rule", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def toggle_rule(n_clicks):
        if ctx.triggered:
            rule_id = ctx.triggered[0]["id"]["index"]
            alert_manager = get_alert_manager()
            rule = alert_manager.get_rule(rule_id)
            if rule:
                if rule.enabled:
                    alert_manager.disable_rule(rule_id)
                else:
                    alert_manager.enable_rule(rule_id)
        return None

    # Acknowledge alert
    @app.callback(
        Output("alerts-container", "id"),
        Input({"type": "btn-ack-alert", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def acknowledge_alert(n_clicks):
        if ctx.triggered:
            alert_id = ctx.triggered[0]["id"]["index"]
            alert_manager = get_alert_manager()
            alert_manager.acknowledge_alert(alert_id, user_id="system")
        return "alerts-container"

    # Toggle add rule modal
    @app.callback(
        Output("modal-add-rule", "is_open"),
        Input("btn-add-rule", "n_clicks"),
        Input("btn-cancel-rule", "n_clicks"),
        Input("btn-create-rule", "n_clicks"),
        State("modal-add-rule", "is_open"),
        prevent_initial_call=True
    )
    def toggle_rule_modal(add_clicks, cancel_clicks, create_clicks, is_open):
        if ctx.triggered:
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if trigger_id == "btn-add-rule":
                return True
            elif trigger_id in ["btn-cancel-rule", "btn-create-rule"]:
                return False
        return is_open

    # Create new rule
    @app.callback(
        Output("rules-container", "id"),
        Input("btn-create-rule", "n_clicks"),
        State("rule-name-input", "value"),
        State("rule-metric-select", "value"),
        State("rule-condition-select", "value"),
        State("rule-threshold-input", "value"),
        State("rule-severity-select", "value"),
        State("rule-interval-input", "value"),
        State("rule-channels-check", "value"),
        prevent_initial_call=True
    )
    def create_new_rule(n_clicks, name, metric, condition, threshold, severity, interval, channels):
        if not all([name, metric, condition, threshold]):
            return "rules-container"

        alert_manager = get_alert_manager()
        channel_objs = [AlertChannel[ch.upper()] for ch in (channels or ["EMAIL"])]

        try:
            alert_manager.add_rule(
                name=name,
                metric=metric,
                condition=condition,
                threshold=float(threshold),
                severity=AlertSeverity[severity.upper()],
                channels=channel_objs,
                check_interval=int(interval or 300)
            )
        except Exception as e:
            print(f"Error creating rule: {str(e)}")

        return "rules-container"


# Compatibility with existing callbacks
ALL = {"type": "ALL"}
