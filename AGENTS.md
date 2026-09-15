# IAM ConCen Agent Instructions

## Mission

IAM ConCen is an AWS IAM-first portfolio project. Software supports identity lifecycle, authorization, cloud security, operations, and learning; it must not become a generic full-stack application.

## Required workflow

At the start of a session:

1. Check Git status and recent history.
2. Read `docs/PROJECT_STATE.md` and the current section of `docs/ROADMAP.md`.
3. Inspect existing code and run proportionate checks.
4. Work only on the phase explicitly approved by the project owner.

Before completing meaningful work:

1. Run relevant tests and a dashboard smoke check.
2. Review the diff and security impact.
3. Update affected documentation, especially `docs/PROJECT_STATE.md`.
4. Commit a coherent milestone when the work is successful.
5. Push only when a remote and safe authentication are available; never force-push.

## Architecture boundaries

- Keep lifecycle and policy logic provider-independent.
- Put AWS API behavior behind connectors.
- Use Streamlit as the visible control center for every phase.
- Default to `SIMULATION`; live lab writes require a later approved phase and explicit confirmation.
- Prefer Python, SQLite, pytest, PowerShell, and later narrowly justified Terraform/Docker.
- Do not introduce React, Node.js, Kubernetes, microservices, Redis, or Kafka without a documented need.

## Security boundaries

- Never commit secrets, `.env`, tokens, cloud keys, tenant credentials, or Terraform state.
- Never log or display credentials.
- Never use AWS root credentials or request broad production access.
- Prefer least-privilege identities, managed identities, roles, SSO/profiles, and environment-based configuration.
- Never claim a simulated or license-blocked feature worked live.
- Never perform destructive cloud operations automatically.

## Project memory

Repository state overrides chat memory. Maintain:

- `docs/PROJECT_STATE.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`
- `docs/SECURITY_MODEL.md`
- `docs/LEARNING_NOTES.md`
- `docs/DEMO_GUIDE.md`
- `docs/TROUBLESHOOTING.md`
