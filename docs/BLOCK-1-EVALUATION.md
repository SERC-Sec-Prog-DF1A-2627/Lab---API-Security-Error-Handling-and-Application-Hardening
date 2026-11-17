# Block 1: evaluation and test design

10 minutes individual, then 5-minute review led by the tutor. Solo students use the self-check below.

1. An editor with a valid CSRF token sends `{"title":"New","owner_id":3}` to their own note. Trace the checks and expected database state. Why are the role and CSRF checks insufficient?
2. Design a negative test that isolates object ownership. State the account, note, token, body, expected status and state assertion. Include one positive test to avoid “deny everything” passing as a secure solution.
3. In 100–150 words, evaluate shared permission helpers against copying inline conditions. Include one maintenance benefit, one remaining risk and evidence from your tests.
4. Explain why API5, API1 and API3 describe different defects in Exercise 2. These are the explicitly named 2023 edition categories, not a claim about a new edition.

Self-check: the field allowlist rejects the mixed body before any write, giving 400. A valid editor session/CSRF with note 3 should produce 404 and leave note 3 unchanged. A valid own-note update should return 200. Shared helpers reduce divergence but omissions at individual endpoints remain possible. Hiding controls or using unguessable IDs cannot replace permission enforcement.
