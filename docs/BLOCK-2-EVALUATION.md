# Block 2: evaluate complementary controls

10 minutes individual, then 5-minute review. Solo students answer before consulting the example below.

Complete this table. The classification depends on the threat and can overlap; justify it with an observed result and a limitation.

| Control | Preventative, detective or mitigating? | Evidence | Remaining risk / improvement |
|---|---|---|---|
| Ownership check | | | |
| Field allowlist | | | |
| Safe error response | | | |
| Structured logging | | | |
| CSP and other headers | | | |
| Rate limiting | | | |

Write 150–200 words comparing two controls. Explain why one cannot replace the other. Discuss two workers behind a proxy: what changes for rate-limit storage, client identity and logs? Design one additional test that would matter before deployment.

Example reasoning: ownership prevents the tested unauthorised record access, while a generic error mitigates information leakage after a failure. Logging supports detection only when records are reviewed or monitored; writing a line alone does not detect an attack. CSP can prevent specified browser behaviours while mitigating the impact of some injected content. Rate limiting can prevent requests above its budget and mitigate some resource abuse, but distributed identities and boundary bursts remain. In-memory counters are local to a process; use shared storage and explicitly trusted proxy configuration in a real deployment.

Completion evidence: one correlated 500/log example, header evidence on a 404, a 429 with Retry-After, and a reasoned comparison. Passing these checks does not validate the whole production deployment.
