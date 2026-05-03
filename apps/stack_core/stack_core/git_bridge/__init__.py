"""Two-way sync engine between the live Frappe site and a config-as-code git repo.

Layout (per PLAN.md §8):

  exporter.py  - dumps Stack Blueprint + Workflow Def state to JSON files
                 in the config repo working tree.
  committer.py - stages + commits the working tree, optionally pushes a branch.
  pr_opener.py - opens a GitHub PR via gh CLI (with REST API fallback).
  differ.py    - structured diff between site state and config-repo HEAD.
  applier.py   - the inverse direction (git -> site), idempotent.
"""
