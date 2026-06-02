# RESOURCE_EXPENDITURE_POLICY

## Purpose
Keep execution cost-aware and approval-driven across tools, services, and infrastructure.

## Default Stance
- Prefer zero-cost and existing resources first.
- Do not introduce paid services, subscriptions, or infrastructure by default.

## Approval Requirement
Explicit user approval is required before any paid expenditure, including:
- Cloud resources
- SaaS subscriptions
- Marketplace purchases
- Paid APIs
- New paid tooling licenses

## Cost Tier Model (Editable)
Use these default approval bands unless replaced by project policy.

- Tier 0: $0
  - Auto-allowed if technically appropriate.
- Tier 1: $1 to $99
  - Require explicit approval with brief rationale.
- Tier 2: $100 to $999
  - Require explicit approval plus options comparison.
- Tier 3: $1000+
  - Require formal decision with tradeoff summary and rollback plan.

## Required Decision Package For Paid Options
Before approval request, provide:
1. Problem being solved
2. Free/low-cost alternatives considered
3. Estimated monthly and annual cost
4. Operational risks and lock-in impact
5. Exit strategy

## Enforcement Notes
- If no approval exists, stop at recommendation stage.
- Do not execute spend-related commands while awaiting approval.
- Track approved spending choices in project docs for traceability.
