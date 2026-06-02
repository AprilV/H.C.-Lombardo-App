# STARTUP_MODES

Define operating modes so startup behavior is explicit.

## Mode 1: Local Development
- Purpose: active coding and quick verification.
- Expected runtime: local services only.
- Typical checks: health endpoint, key API endpoints.

## Mode 2: Demo/Release Verification
- Purpose: pre-release confidence check.
- Expected runtime: stable app mode.
- Typical checks: smoke test matrix and critical path checks.

## Mode 3: Recovery/Incident
- Purpose: diagnose failures safely.
- Expected runtime: minimal changes, maximum evidence capture.
- Typical checks: logs, health status, service availability.

## Startup Lock Interaction
- Order 66 runs before implementation in any mode.
- Summary must report selected mode and runtime status.
- Commit and resource policies apply in every mode.
