# Activity 2: What should a client and a log reveal?

Block 2 · 20 minutes · two pairs and one group of three, or independent study

**Objective:** distinguish useful client feedback from private diagnostic information, then design safe correlated evidence. No application setup is required.

**Roles:** investigator identifies the leak, reviewer proposes a safer design, reporter records the reasoning. In pairs combine reviewer/reporter. Rotate after cases B and D. Solo: predict each answer in writing before opening the self-check.

Spend 3 minutes reading, 10 minutes discussing cases, 5 minutes writing replacements and 2 minutes sharing one trade-off.

All details below are fictional. For each case, identify the security problem, propose the client status/body and propose a safe server event. Decide whether the event needs investigation or merely normal request handling.

| Case | Observed response or log | Your decision |
|---|---|---|
| A | HTTP 500: `sqlite3.OperationalError: no such table: payroll_backup` | |
| B | HTTP 200: `{"error":"Traceback in /srv/internal/notes.py line 72"}` | |
| C | Log: `login password=Classroom-Only-314! cookie=session=FAKE_TOKEN` | |
| D | HTTP 404: `{"error":"Note 8 exists but belongs to user 6"}` | |
| E | Log includes a whole private note because it dumps the JSON body | |
| F | HTTP 404: `{"error":"Not found.","request_id":"sample-7"}` and a matching status/event log | |

Draw a failure response branching to a client message and a restricted server event. Label the shared request ID. Explain why one diagram arrow should not carry a password, request body or exception text.

## Your proposed event

Write a JSON example with `timestamp`, `event`, `status`, `request_id` and `endpoint`. For an unexpected failure, add an exception category and safe location. Identify who should be able to access it, how long to retain it, and how you would avoid one user generating unlimited log volume. Exact retention periods require an organisational decision; justify a proposal rather than inventing a legal rule.

<details><summary>Self-check: open after writing your answers</summary>

A: 500 generic message; log exception category and safe code location without SQL/table text. B: unexpected failure needs 500 rather than 200; remove traceback/path from response. C: omit passwords and session values entirely, even in internal logs. D: use the same 404 wording for absent/inaccessible objects; avoid confirming existence/ownership. E: allowlist metadata; note bodies may be personal or confidential. F: appropriate pattern for this teaching app. A request ID must not itself encode identity or secret data. Correct JSON formatting alone does not make logs safe.

A/B are unexpected failures needing diagnostic attention. D/F are expected outcomes, though repeated denials can become a useful security signal. Monitoring should consider frequency and context, not alert on every ordinary 404. C/E are problems in the logging design itself.

</details>

**Submit evidence:** your six-case table, one safe JSON response/log pair and a paragraph discussing the diagnostic trade-off. Then start [Exercise 3](exercise-3-error-handling/INSTRUCTIONS.md).
