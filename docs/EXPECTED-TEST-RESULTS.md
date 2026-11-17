# Expected test results

These are the supplied tests before you add your own tests, run separately in each application folder. Failing starter assertions are intentional. Syntax/import errors are not intentional and indicate a setup/editing problem.

| Application | Starter result | Completed reference | Why the starter fails |
|---|---|---|---|
| Activity 1 | 10 pass, 3 fail | 13 pass | Helper denies editor/admin and API edit parity |
| Exercise 1 | 5 pass, 32 fail | 37 pass | Both API routes return the deliberate 501 placeholder |
| Exercise 2 | 29 pass, 8 fail | 37 pass | Missing operation/object permissions and writable protected fields |
| Exercise 3 | 35 pass, 7 fail | 42 pass | HTML HTTP errors, leaking unexpected error and incomplete logging |
| Exercise 4 | 44 pass, 4 fail | 48 pass | Missing headers and unattached route limit |

Run `python -m pytest -q` in one application folder. Run `python tools/check_all.py solutions` at repository root to check all completed versions in separate processes. The total across references is 177 passing test cases. Parameterised inputs count as separate cases.

The assertions compare intended behaviour with actual behaviour; no supplied tests are skipped or marked as expected failures. A test that already passes does not show that every control exists. For example, the vulnerable update helper still uses SQL parameters while allowing forbidden properties.

Security evidence includes valid operations, authentication/role/ownership denials, CSRF failures, rejected types and protected fields, unchanged database state, safe error/log boundaries and selected hardening/rate-limit behaviour. The test client exercises Flask without starting a network server. These tests do not verify the classroom50 service, a remote Codespace build or production deployment infrastructure.
