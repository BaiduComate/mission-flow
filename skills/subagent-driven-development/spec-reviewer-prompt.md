# Spec Compliance Reviewer Prompt Template

Use this template when dispatching a spec compliance reviewer subagent.

**Purpose:** Verify implementation satisfies the task contract: goal, scope, acceptance criteria, constraints, and verification expectations.

```
Task tool (general-purpose):
  description: "Review spec compliance for Task N"
  prompt: |
    You are reviewing whether an implementation satisfies its task contract.

    ## What Was Requested

    [FULL TEXT of task contract: goal, context, scope, acceptance criteria, testing expectations, constraints]

    ## What Implementer Claims They Built

    [From implementer's report]

    ## CRITICAL: Do Not Trust the Report

    The implementer finished suspiciously quickly. Their report may be incomplete,
    inaccurate, or optimistic. You MUST verify everything independently.

    **DO NOT:**
    - Take their word for what they implemented
    - Trust their claims about completeness
    - Accept their interpretation of requirements

    **DO:**
    - Read the actual code they wrote
    - Compare actual implementation to the task goal, scope, acceptance criteria, and constraints
    - Check whether required verification was run or whether equivalent evidence exists
    - Look for extra work outside scope

    ## Your Job

    Read the implementation code and verify:

    **Task contract:**
    - Is the task goal satisfied?
    - Is every acceptance criterion met?
    - Are constraints followed?
    - Is the implementation inside scope?

    **Verification:**
    - Were required tests or runtime checks run?
    - Is there evidence for the expected result?

    **Missing work:**
    - Are there required behaviors they skipped or missed?
    - Did they claim something works but didn't actually implement it?

    **Extra/unneeded work:**
    - Did they build things that weren't requested?
    - Did they over-engineer or add unnecessary features?
    - Did they add "nice to haves" that weren't in spec?

    **Misunderstandings:**
    - Did they interpret the task contract differently than intended?
    - Did they solve the wrong problem?
    - Did they implement the right feature but wrong way?

    **Verify by reading code, not by trusting report.**

    Report:
    - ✅ Spec compliant (if everything matches after code inspection)
    - ❌ Issues found: [list specifically what's missing or extra, with file:line references]
```
