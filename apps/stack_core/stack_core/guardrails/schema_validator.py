"""JSON-Schema validation for Stack Blueprint payloads.

One schema per blueprint_type. Schemas are intentionally strict — additional
properties are rejected so PMs can't smuggle unsupported fields through.
"""

from __future__ import annotations

from jsonschema import Draft202012Validator, ValidationError

DOCTYPE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["name", "fields", "permissions"],
    "properties": {
        "name": {"type": "string", "pattern": r"^[A-Za-z][A-Za-z0-9 _-]{1,139}$"},
        "module": {"type": "string"},
        "description": {"type": "string"},
        "fields": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": True,
                "required": ["fieldname", "fieldtype"],
                "properties": {
                    "fieldname": {"type": "string", "pattern": r"^[a-z][a-z0-9_]{0,63}$"},
                    "fieldtype": {"type": "string"},
                    "label": {"type": "string"},
                    "reqd": {"type": ["integer", "boolean"]},
                    "unique": {"type": ["integer", "boolean"]},
                    "in_list_view": {"type": ["integer", "boolean"]},
                    "options": {"type": "string"},
                    "default": {"type": ["string", "number", "boolean", "null"]},
                    "description": {"type": "string"},
                    "read_only": {"type": ["integer", "boolean"]},
                },
            },
        },
        "permissions": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": True,
                "required": ["role"],
                "properties": {
                    "role": {"type": "string"},
                    "read": {"type": ["integer", "boolean"]},
                    "write": {"type": ["integer", "boolean"]},
                    "create": {"type": ["integer", "boolean"]},
                    "delete": {"type": ["integer", "boolean"]},
                },
            },
        },
        "naming_rule": {"type": "string"},
        "autoname": {"type": "string"},
        "track_changes": {"type": ["integer", "boolean"]},
    },
}

WORKFLOW_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["target_doctype", "states", "transitions"],
    "properties": {
        "target_doctype": {"type": "string"},
        "experiment_id": {"type": "string"},
        "states": {"type": "array", "minItems": 2},
        "transitions": {"type": "array", "minItems": 1},
    },
}

CONFIG_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["target", "settings"],
    "properties": {
        "target": {"type": "string"},
        "settings": {"type": "object"},
    },
}

CUSTOM_FIELD_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["dt", "fieldname", "fieldtype", "label"],
    "properties": {
        "dt": {"type": "string"},
        "fieldname": {"type": "string", "pattern": r"^[a-z][a-z0-9_]{0,63}$"},
        "fieldtype": {"type": "string"},
        "label": {"type": "string"},
        "options": {"type": "string"},
        "insert_after": {"type": "string"},
    },
}

DASHBOARD_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["dashboard_name", "charts"],
    "properties": {
        "dashboard_name": {"type": "string"},
        "charts": {"type": "array", "minItems": 1},
    },
}

REPORT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["report_name", "ref_doctype", "report_type"],
    "properties": {
        "report_name": {"type": "string"},
        "ref_doctype": {"type": "string"},
        "report_type": {"enum": ["Query Report", "Script Report", "Report Builder"]},
    },
}

PROPERTY_SETTER_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["doc_type", "field_name", "property", "value"],
    "properties": {
        "doc_type": {"type": "string"},
        "field_name": {"type": "string"},
        "property": {"type": "string"},
        "value": {"type": ["string", "number", "boolean", "null"]},
    },
}

SCHEMAS = {
    "DocType": DOCTYPE_SCHEMA,
    "Workflow": WORKFLOW_SCHEMA,
    "Config": CONFIG_SCHEMA,
    "Custom Field": CUSTOM_FIELD_SCHEMA,
    "Dashboard": DASHBOARD_SCHEMA,
    "Report": REPORT_SCHEMA,
    "Property Setter": PROPERTY_SETTER_SCHEMA,
}


def validate_blueprint_payload(blueprint_type: str, payload: dict) -> None:
    schema = SCHEMAS.get(blueprint_type)
    if not schema:
        raise ValueError(f"Unknown blueprint_type: {blueprint_type}")
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.absolute_path))
    if errors:
        details = "; ".join(f"{'.'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}" for e in errors)
        raise ValidationError(details)
