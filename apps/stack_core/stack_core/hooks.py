app_name = "stack_core"
app_title = "Stack Core"
app_publisher = "Dhwani Rural Information Systems"
app_description = "Frappe support app for the frappe-stack Claude Code plugin"
app_email = "noreply@dhwaniris.com"
app_license = "MIT"

# Doc events --------------------------------------------------------------
# Block hard-delete on audit-tagged DocTypes.
doc_events = {
    "*": {
        "before_delete": "stack_core.guardrails.permission_enforcer.block_hard_delete_on_audit_tagged",
    },
}

# Fixtures ----------------------------------------------------------------
# Every Stack Blueprint row IS a fixture; the rest are app-level.
fixtures = [
    "Stack Blueprint",
    "Stack Workflow Def",
]

# Boot session -----------------------------------------------------------
# Surface the audit log + experiment dashboard quick-links to System Manager.
boot_session = "stack_core.api._decorators.boot_session"

# Scheduled tasks --------------------------------------------------------
scheduler_events = {
    "daily": [
        "stack_core.git_bridge.applier.reconcile_drift",
    ],
}

# Permission query conditions -------------------------------------------
# Stack Audit Log: only System Manager + Stack Admin can read all rows;
# others see only rows where they were the actor.
permission_query_conditions = {
    "Stack Audit Log": "stack_core.doctype.stack_audit_log.stack_audit_log.permission_query",
}

# Required apps ---------------------------------------------------------
required_apps = ["frappe"]
