from __future__ import annotations

from dash import Dash, Input, Output, no_update

from dashboard import components as comp


def register(app: Dash) -> None:
    @app.callback(
        [
            Output(comp.ID_ANALYSIS_PANEL, "style"),
            Output(comp.ID_DASHBOARD_PANEL, "style"),
            Output(comp.ID_HISTORY_PANEL, "style"),
            Output(comp.ID_COMPARE_PANEL, "style"),
            Output(comp.ID_SETTINGS_PANEL, "style"),
        ],
        Input(comp.ID_TABS, "active_tab"),
    )
    def switch_tab(active_tab):
        hidden = {"display": "none"}
        shown = {"display": "block"}
        if active_tab == comp.ID_TAB_DASHBOARD:
            return hidden, shown, hidden, hidden, hidden
        if active_tab == comp.ID_TAB_HISTORY:
            return hidden, hidden, shown, hidden, hidden
        if active_tab == comp.ID_TAB_COMPARE:
            return hidden, hidden, hidden, shown, hidden
        if active_tab == comp.ID_TAB_SETTINGS:
            return hidden, hidden, hidden, hidden, shown
        # Chat / default
        return shown, hidden, hidden, hidden, hidden

    @app.callback(
        [
            Output(comp.ID_NAV_CHAT, "className"),
            Output(comp.ID_NAV_DASHBOARD, "className"),
            Output(comp.ID_NAV_HISTORY, "className"),
            Output(comp.ID_NAV_COMPARE, "className"),
            Output(comp.ID_NAV_SETTINGS, "className"),
        ],
        Input(comp.ID_TABS, "active_tab"),
    )
    def highlight_nav(active_tab):
        def cls(is_active: bool) -> str:
            return "nav-item active" if is_active else "nav-item"

        return (
            cls(active_tab == comp.ID_TAB_CHAT),
            cls(active_tab == comp.ID_TAB_DASHBOARD),
            cls(active_tab == comp.ID_TAB_HISTORY),
            cls(active_tab == comp.ID_TAB_COMPARE),
            cls(active_tab == comp.ID_TAB_SETTINGS),
        )

    @app.callback(
        Output(comp.ID_TABS, "active_tab"),
        [
            Input(comp.ID_NAV_CHAT, "n_clicks"),
            Input(comp.ID_NAV_DASHBOARD, "n_clicks"),
            Input(comp.ID_NAV_HISTORY, "n_clicks"),
            Input(comp.ID_NAV_COMPARE, "n_clicks"),
            Input(comp.ID_NAV_SETTINGS, "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def nav_to_tab(n_chat, n_dash, n_hist, n_compare, n_settings):
        from dash import callback_context

        if not callback_context.triggered:
            return no_update
        tid = callback_context.triggered[0]["prop_id"].split(".")[0]
        if tid == comp.ID_NAV_DASHBOARD:
            return comp.ID_TAB_DASHBOARD
        if tid == comp.ID_NAV_HISTORY:
            return comp.ID_TAB_HISTORY
        if tid == comp.ID_NAV_COMPARE:
            return comp.ID_TAB_COMPARE
        if tid == comp.ID_NAV_SETTINGS:
            return comp.ID_TAB_SETTINGS
        return comp.ID_TAB_CHAT

