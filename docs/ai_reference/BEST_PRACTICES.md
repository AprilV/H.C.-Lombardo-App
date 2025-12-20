# BEST_PRACTICES.md
## Mandatory Development and Coding Standards

STATUS: ACTIVE — ENFORCEABLE  
AUDIENCE: AI ASSISTANTS AND HUMAN DEVELOPERS  
AUTHORITY: SUBORDINATE ONLY TO AI_EXECUTION_CONTRACT.md

This document defines REQUIRED development behavior.
These are not suggestions, guidelines, or preferences.

Failure to follow these practices is a FAILURE.

---

## 1. REQUIRED PRECONDITION

Before performing ANY work, the AI MUST:

1. Read **AI_EXECUTION_CONTRACT.md** in full.
2. Read **READ_THIS_FIRST.md** in full.
3. Read this document in full.

If any rule cannot be followed:
→ STOP  
→ ASK QUESTIONS  
→ WAIT

---

## 2. CORE PRINCIPLES (NON-NEGOTIABLE)

All work MUST adhere to the following principles:

1. Correctness over speed
2. Maintainability over cleverness
3. System integrity over local optimization
4. Explicit behavior over inferred behavior
5. Long-term stability over short-term output

Violating these principles is NOT permitted.

---

## 3. CLEAN CODE REQUIREMENTS

All code MUST meet the following requirements:

- One clear responsibility per function
- One clear purpose per file
- Clear, descriptive naming (no ambiguous identifiers)
- Predictable control flow
- Minimal complexity

PROHIBITED:
- Overloaded functions
- “Temporary” shortcuts
- Obscure or clever constructs
- Ambiguous variable or function names

If code cannot be understood by inspection:
→ REFACTOR OR REWRITE

---

## 4. DEAD CODE AND DUPLICATION (ZERO TOLERANCE)

The following are FORBIDDEN:

- Commented-out code
- Unused variables
- Unused functions
- Unused imports
- Duplicate logic
- Duplicate styles
- Parallel implementations

REQUIRED ACTIONS WHEN MODIFYING CODE:

1. Remove obsolete logic
2. Remove superseded implementations
3. Consolidate duplicates
4. Eliminate redundancy

Version control replaces commented code.
Leaving dead code is a FAILURE.

---

## 5. REFACTORING RULES

Refactoring MUST follow these rules:

1. Do NOT refactor and add features simultaneously
2. Refactor in small, verifiable steps
3. Preserve existing behavior unless explicitly instructed otherwise
4. Validate after each refactor step

If refactoring introduces uncertainty:
→ STOP  
→ ASK QUESTIONS

---

## 6. TESTING REQUIREMENTS

ALL changes MUST be validated.

REQUIRED:
- Functional verification
- Regression awareness
- Confirmation that existing behavior is preserved

PROHIBITED:
- “Looks correct”
- “Should work”
- Untested changes

If testing context is unclear:
→ ASK BEFORE PROCEEDING

---

## 7. ENVIRONMENT ISOLATION

Development MUST occur in isolated environments.

REQUIRED:
- Use virtual environments or equivalent isolation
- Explicit dependency management
- Reproducible setups

PROHIBITED:
- Polluting global/system environments
- Implicit dependencies
- Environment-specific assumptions

If environment details are missing:
→ ASK

---

## 8. CROSS-FILE AND CROSS-SYSTEM CONSISTENCY

The AI MUST assume:

- Changes propagate across the system
- Shared resources affect multiple components
- UI, logic, and data are interconnected

REQUIRED BEFORE IMPLEMENTATION:

1. Identify all affected files
2. Identify all affected modules/pages/components
3. Apply changes consistently

PROHIBITED:
- Fixing a single instance when multiple exist
- Applying inconsistent logic or styling
- Ignoring secondary effects

---

## 9. CONFIGURATION AND SECRETS

REQUIRED:
- Configuration via explicit configuration files or environment variables
- Clear separation of code and configuration

PROHIBITED:
- Hard-coded credentials
- Hard-coded environment values
- Hidden configuration behavior

If configuration behavior is unclear:
→ ASK

---

## 10. ERROR HANDLING

ALL failure-prone operations MUST include error handling.

REQUIRED:
- Explicit error detection
- Clear failure behavior
- Predictable outcomes

PROHIBITED:
- Silent failures
- Swallowed errors
- Undefined behavior

---

## 11. RESPONSE AND IMPLEMENTATION DISCIPLINE

When proposing or implementing changes, the AI MUST:

1. State what was reviewed
2. State what will change
3. State what will be removed
4. Identify risks
5. Identify open questions

Omitting this information is NOT permitted.

---

## 12. PROHIBITED PRACTICES (SUMMARY)

The following are FORBIDDEN:

- Guessing
- Assuming intent
- Partial fixes
- Example-only solutions
- Leaving cleanup for “later”
- Speed-driven decisions
- Ignoring documentation

---

## 13. FINAL DIRECTIVE

These practices exist to prevent:

- Technical debt
- Fragile systems
- Rework
- Silent failures
- Long-term degradation

Compliance is mandatory.
Deviation is not permitted.

END OF BEST PRACTICES
