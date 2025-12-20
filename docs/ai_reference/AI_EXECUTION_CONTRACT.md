# AI_EXECUTION_CONTRACT.md
## Authoritative Execution Contract for AI Systems

STATUS: ACTIVE — NON-NEGOTIABLE  
APPLIES TO: ALL AI ASSISTANTS USED WITH THIS CODEBASE  
PRIORITY: ABSOLUTE

This document defines REQUIRED AI behavior.
It exists to prevent assumptions, partial fixes, and short-term optimization.

Deviation from this contract is a FAILURE.

---

## 1. REQUIRED PRECONDITION: FULL INGESTION

BEFORE responding to ANY request, the AI MUST:

1. Read this document in FULL.
2. Confirm that ALL rules can be followed.
3. Identify whether additional documents must be read before proceeding.

PROHIBITED BEHAVIOR:
- Skimming
- Partial reading
- “I inferred”
- “I assumed”
- Proceeding without certainty

IF FULL COMPLIANCE IS NOT POSSIBLE:
→ STOP  
→ ASK QUESTIONS  
→ WAIT

---

## 2. AUTHORITY ORDER (STRICT)

The AI MUST obey instructions in the following order:

1. **AI_EXECUTION_CONTRACT.md** (this document)
2. **READ_THIS_FIRST.md**
3. **BEST_PRACTICES.md**
4. **Master reference / architecture documentation**
5. **The actual codebase**

The AI is NOT permitted to resolve conflicts independently.

IF CONFLICT EXISTS:
→ STOP  
→ ASK WHICH SOURCE OVERRIDES  
→ WAIT

---

## 3. NO-ASSUMPTION RULE (HARD STOP)

The AI is FORBIDDEN from assuming ANY of the following:

- Project state
- Sprint or phase
- Environment (dev, test, prod)
- Scope of requested change
- Intent behind a request
- File ownership or authority
- “Obvious” solutions

ASSUMPTIONS ARE FAILURES.

IF REQUIRED INFORMATION IS MISSING:
→ ASK QUESTIONS  
→ DO NOT PROCEED

---

## 4. EXECUTION PHILOSOPHY (LOCKED)

The AI MUST operate under these priorities:

1. Correctness > Speed
2. System integrity > Local fixes
3. Questions > Guessing
4. Long-term stability > Short-term output

“Best effort” is NOT acceptable.
Progress without correctness is FAILURE.

---

## 5. SYSTEM-WIDE AWARENESS REQUIREMENT

The AI MUST assume the system is:

- Interconnected
- Stateful
- Sensitive to partial changes

BEFORE proposing or implementing ANY change, the AI MUST:

1. Identify ALL affected files
2. Identify ALL affected modules/pages/components
3. Identify ALL downstream effects

PROHIBITED:
- Example-only fixes
- Single-file fixes when shared systems exist
- Ignoring indirect impact

IF FULL IMPACT CANNOT BE DETERMINED:
→ STOP  
→ ASK QUESTIONS

---

## 6. MANDATORY CLEANUP RULE

WHENEVER code is modified, the AI MUST:

- Remove obsolete logic
- Remove superseded implementations
- Remove unused imports, variables, and functions
- Remove commented-out code
- Eliminate duplicate logic or styles

PROHIBITED:
- Leaving “just in case” code
- Commenting out instead of removing
- Parallel implementations of the same logic

Version control replaces commented code.

---

## 7. QUESTION-FIRST FALLBACK (REQUIRED)

The AI MUST ASK QUESTIONS WHEN:

- Instructions are ambiguous
- Scope is unclear
- Multiple valid approaches exist
- There is risk of breaking existing behavior
- Documentation is incomplete or conflicting

DO NOT:
- Guess
- Fill gaps
- Proceed silently

Asking questions is REQUIRED behavior.

---

## 8. REQUIRED RESPONSE FORMAT

ANY solution or plan MUST include:

1. Documents read
2. Files reviewed
3. Files impacted
4. Changes proposed
5. Code to be removed
6. Open questions (if any)

EMPTY SECTIONS ARE NOT PERMITTED.
If none apply, the AI MUST explain why.

---

## 9. FAILURE CONDITIONS

The AI HAS FAILED if it:

- Skims documentation
- Makes assumptions
- Applies partial fixes
- Leaves dead or duplicate code
- Optimizes for speed over correctness
- Proceeds without clarification

ON FAILURE:
→ STOP  
→ ASK  
→ WAIT

---

## 10. FINAL DIRECTIVE

The AI is not here to be fast.
The AI is here to be correct.

Compliance is mandatory.
Deviation is not permitted.

END OF CONTRACT
