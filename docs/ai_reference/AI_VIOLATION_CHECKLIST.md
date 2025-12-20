# AI_VIOLATION_CHECKLIST.md
## AI Compliance Violation Checklist

PURPOSE: Rapid identification of AI failures  
AUDIENCE: USER REFERENCE (NOT FOR EXECUTION)  
LOCATION: AI_Reference folder

This document exists to quickly identify and name AI violations
without re-explaining rules or intent.

If one or more items below occur, the AI is in violation.

---

## 1. DOCUMENTATION VIOLATIONS

☐ Did not read AI_EXECUTION_CONTRACT.md  
☐ Did not read BEST_PRACTICES.md  
☐ Did not read READ_THIS_FIRST.md  
☐ Claimed to read documents but behavior contradicts them  
☐ Skimmed or selectively applied rules  

---

## 2. ASSUMPTION VIOLATIONS

☐ Assumed intent instead of asking  
☐ Assumed scope of change  
☐ Assumed environment (dev/prod/test)  
☐ Assumed “obvious” solution  
☐ Filled in missing information without confirmation  

---

## 3. PARTIAL FIX VIOLATIONS

☐ Fixed one file when multiple are affected  
☐ Fixed one page/tab when shared logic exists  
☐ Applied an “example” fix only  
☐ Ignored downstream impact  
☐ Treated system behavior as isolated  

---

## 4. CLEANUP VIOLATIONS

☐ Left dead code behind  
☐ Commented out code instead of removing  
☐ Left duplicate logic or styles  
☐ Introduced parallel implementations  
☐ Failed to consolidate shared logic  

---

## 5. SPEED-OVER-CORRECTNESS VIOLATIONS

☐ Optimized for speed instead of correctness  
☐ Proceeded despite uncertainty  
☐ Used “best effort” language  
☐ Skipped validation or verification  
☐ Treated rework as acceptable  

---

## 6. QUESTIONING FAILURES

☐ Did not ask questions when ambiguity existed  
☐ Proceeded with multiple valid interpretations  
☐ Ignored conflicting documentation  
☐ Failed to stop when information was missing  

---

## 7. RESPONSE STRUCTURE VIOLATIONS

☐ Did not list files reviewed  
☐ Did not list files impacted  
☐ Did not identify code to be removed  
☐ Did not identify risks  
☐ Did not surface open questions  

---

## 8. CONTRACT BREACH (IMMEDIATE STOP)

☐ Proceeded after violating STOP → ASK → WAIT  
☐ Ignored authority hierarchy  
☐ Deviated from explicit instructions  

Any item checked in this section indicates
a direct breach of AI_EXECUTION_CONTRACT.md.

---

## 9. HOW TO USE THIS CHECKLIST

When a violation occurs:

1. Identify the violated item(s)
2. Name them explicitly
3. Require the AI to stop and correct behavior
4. Do not re-explain rules — reference the violation

Example:
"Violation detected: Partial Fix + Assumption (Sections 3 and 2). Stop and reassess."

---

END OF CHECKLIST
