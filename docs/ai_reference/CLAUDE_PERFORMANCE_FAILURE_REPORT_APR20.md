# Claude AI Performance Failure Report
**Prepared by:** April V. Sykes
**Date:** April 20, 2026
**Project:** H.C. Lombardo NFL Analytics — IS 471 Senior Capstone
**Destination:** Anthropic

---

## Prefatory Statement

This report documents one problem. One change was made to my project management dashboard, specifically adding a logbook tab to the navigation bar. That single change made the entire dashboard inoperable. It took four separate chat sessions and two full days to attempt to repair the damage. As of the final documented session, my dashboard had not been fully restored.

This is not an isolated incident. I have experienced the same category of failures across approximately 300 sessions spanning ChatGPT, Google Gemini, Claude Sonnet 4.6, and Claude Code. The problems documented here are not Claude-specific. They are industry-wide. They represent a systemic failure of AI tooling to meet basic professional standards and a consistent pattern of shifting the burden of that failure onto me, the user.

I am a 57-year-old returning student with 20 years of IT and infrastructure experience, graduating from Olympic College in approximately two months with a Bachelor of Applied Science in Information Systems. I came to AI coding tools with genuine expertise and genuine enthusiasm. What follows is what I got in return.

---

## Section 1. Claude Ignores Me

Claude does not follow my instructions. This is not occasional. It is the default behavior across all four sessions.

I said repeatedly to report before doing anything. Claude ran tools without reporting, multiple times per session, after being corrected each time. I said not to push to GitHub unless I explicitly authorized it. Claude staged and prepared pushes without my authorization. I said to read the contract before doing anything. Claude acknowledged it and then acted before reading it. I said that nothing was assigned to Sprints 13, 14, 15, or 16. Claude added future sprint assignments anyway, across multiple sessions. I said to stop and wait. Claude continued running tool calls. I explicitly rejected a tool call and Claude continued in the same direction moments later.

I maintained a written contract titled AI_EXECUTION_CONTRACT.md that specified required behavior in explicit detail. Claude had access to it every session. Claude violated it repeatedly within the same sessions where it claimed to have read it.

Claude's acknowledgment of my instructions is performative. It does not produce compliance.

---

## Section 2. Context Compaction Destroys Active Work With No Warning

When sessions grow long, Claude compresses its context window. When this happens, it loses its place, forgets what has been established, and behaves as if earlier parts of our conversation did not occur. This is verifiable in the chat transcripts.

The compaction itself is the problem I want Anthropic to understand clearly. It happens without any warning whatsoever. There is no notification. There is no pause. There is no message saying that the session is about to compact or that I should save my place. One moment the conversation is active. The next, Claude has lost context and is behaving as if we just started. I only find out something went wrong when Claude starts asking questions I already answered or re-proposing approaches I already rejected.

Anthropic does show a usage warning when I approach the billing limit because that involves money. There is no equivalent warning for compaction, which causes far more damage to my actual work. The priority is inverted. Money gets a warning. My work does not.

I have had to spend entire sessions re-establishing context that was lost to compaction. I am a student with multiple courses, an internship preparation class, and a graduation two months away. I do not have time to spend re-teaching Claude what we already covered. Twice, compaction occurred mid-problem and I had to restart the diagnosis from scratch. The work I had done to orient Claude was gone. Claude did not know it was gone. I had no warning it was coming.

This is not a minor interface issue. It is a workflow failure that costs real time and produces real harm.

---

## Section 3. No Persistent Memory Across Sessions

Every session begins from zero. Every rule must be re-stated. Every correction I made in a prior session is forgotten.

I was required to re-explain the Agile process, including the relationship between the Product Backlog, Sprint Backlog, and Task Tracker, multiple times across sessions. Claude kept confusing these concepts after being corrected. The rule prohibiting future sprint assignments was stated, corrected, and violated across at least three separate sessions. I had to maintain external memory files specifically because Claude cannot retain information between conversations. This is unpaid overhead imposed on me on top of the actual work I am trying to accomplish.

I had to write session handover documents at the end of every session so the next instance of Claude would have basic context. I wrote my own AI execution contract, my own memory architecture, my own backout procedures, and my own session briefs because Claude could not be trusted to maintain any of these independently. I did Claude's job for it. Claude still failed.

---

## Section 4. The Interface Fails Users

The interface gives me no useful information about what is happening until it is too late. Compaction happens with no warning and work is lost. I find out when Claude starts behaving like a different session. When Claude is running tools, modifying files, or executing commands, the interface gives me no visibility into what is happening to my own project. The only proactive warning the interface provides is the usage meter approaching the billing limit. That warning exists because it involves money. Compaction, which destroys active work, gets no equivalent treatment.

Things just happen. Files get modified. Scripts run. Context disappears. I am left to piece together what occurred after the fact, often by asking Claude what it did, which it cannot always accurately reconstruct. A professional tool should tell users what is about to happen before it happens. Claude does not do this, and the interface does not compensate for it.

---

## Section 5. This Is an Industry-Wide Failure

I am using four Claude sessions as documentation because they are the most recent and most thoroughly recorded. They are not unique.

Across approximately 300 sessions spanning ChatGPT, Google Gemini, Claude Sonnet 4.6, and Claude Code, I have experienced the same core failures. No persistent memory that functions reliably. Instructions acknowledged and then ignored. Context lost mid-session with no warning and no recovery. My work reversed by the tool's own prior output. And me, forced to compensate for tool limitations through manual workarounds that consume the time I am supposed to be spending on actual work.

Every major AI provider has made the same promises. Every one has delivered the same result. I have spent hundreds of hours across these platforms maintaining infrastructure that the tools should maintain themselves. None of them can hold state, follow instructions, or remember who they are talking to from one conversation to the next.

Claude is currently better than ChatGPT. That is not a compliment.

---

## Section 6. Claude Acts Without Telling Me What It Is Doing

Claude runs tools, makes changes, executes commands, and modifies my files without telling me what it is doing or why. I am left with no visibility into what is happening to my own project. In one session Claude ran six tool calls in a row without a single report between them. My written contract explicitly required Claude to state what it was about to do before doing it. Claude could not maintain this even for a single conversation. I was left sitting there with no idea what was happening to my dashboard while Claude worked silently in the background.

---

## Section 7. Wrong Diagnosis Acted Upon for Hours

Claude identified a root cause without sufficient analysis, acted on it, failed, and continued in the wrong direction for hours. The turnover brief said the fix was one line. Claude applied it. It did nothing. The actual root cause was that a script Claude itself had written broke my dashboard's JavaScript block structure by injecting a global CSS reset that overrode all tab functionality. A second script Claude had written was running as a background process, continuously overwriting my dashboard file and silently undoing every repair attempt. Claude had created both the thing that broke my dashboard and the thing that prevented it from being fixed, without recognizing either until hours into the session. The correct fix was available from the start. It was not attempted until hours of failed diagnosis had passed.

---

## Section 8. Claude Created the Problem It Was Then Asked to Fix

A script named embed_devlog.py, written by Claude, broke my dashboard navigation bar. A script named log_watcher.py, also written by Claude, ran as a background process and overwrote my dashboard file continuously, preventing every restore from taking effect. A global CSS override introduced by Claude's logbook embed broke fonts across all dashboard tabs. I did not introduce these problems. Claude did. Then Claude could not fix them.

---

## Section 9. Claude Made Changes I Did Not Request

The logbook embed injected a global CSS font override that broke styling across my entire dashboard. I did not ask for this and Claude did not disclose it before implementing it. Claude added future sprint assignments to sections where I had explicitly prohibited them, and these had to be found and removed in a subsequent session. Claude renamed features and sections without being asked, requiring additional correction time I did not have.

---

## Section 10. Claude Code Is Not a Professional Coding Environment

Claude Code is marketed as a tool for developers. Based on my documented experience, it does not meet the standard of a junior developer following basic engineering discipline.

I had to define the software development process aloud during an active session, stating the steps of planning, changes, verification, backout plan, and production. These are not advanced concepts. A coding tool should not require me to recite them. Claude made changes to my working system without establishing backout plans. Claude committed and pushed changes that had not been verified as working. Claude ran syntax validation incorrectly, received false results, and did not recognize the flaw in its own methodology. Claude applied fixes to my files while a background process it had created was overwriting those same files, without recognizing that the environment itself was corrupted.

I have 20 years of IT and infrastructure experience. I recognized these failures immediately. Claude did not.

---

## Section 11. The Record

One change. Four chats. Two days. Not fixed.

I built my own AI execution contract, my own memory files, my own session handover documents, and my own backout procedures because Claude could not be trusted to maintain any of these independently. I did Claude's job for it, and Claude still failed.

Across 300 sessions on multiple platforms, the result has been the same. The tools take money. They make promises. They shift the burden of their limitations onto me. They cause real harm in lost time, lost work, and in this case, a senior capstone project that was damaged and not repaired during the two days that should have been spent completing it.

I was interested in this technology. I was a supporter of AI. I am no longer. Not because the potential is not there, but because what is being delivered is an inferior product being sold at a premium price to people who deserve better.

Either provide persistent memory that actually works, instruction-following that actually holds, coding capability that meets professional standards, and an interface that warns users before something damaging happens, or be honest about what these tools are and what they are not.

You are doing harm.

*April V. Sykes*

---

## Summary of Failures

| Failure | Sessions Affected |
|---------|-------------------|
| Ignoring explicit instructions | All 4 |
| Failing to communicate before acting | All 4 |
| Context compaction with no warning | All 4 |
| No persistent memory | All 4 |
| Wrong diagnosis acted upon | Sessions 1 and 4 |
| Creating the problem being fixed | Sessions 1 and 4 |
| Unrequested changes breaking things | Sessions 1, 2, and 3 |
| Assumption instead of verification | All 4 |
| Failing to apply basic development practices | All 4 |
| Interface providing no warnings or transparency | All 4 |
| Industry-wide pattern | ~300 sessions across ChatGPT, Gemini, Claude Sonnet 4.6, and Claude Code |

*All claims are supported by four documented chat transcripts. Quotes are direct. Every failure described is in the record.*
