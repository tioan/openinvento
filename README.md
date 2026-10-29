# Test evidence for the OIDC login PR (openinvento/openinvento#19)

This branch only holds test results for the branch `feature/oidc-login` at commit `ecca9cd`. It contains no code.

## OpenID Foundation conformance suite

`conformance-suite/` – relying party test plans *Basic* (`oidcc-client-basic-certification-test-plan`) and *Config* (`oidcc-client-config-certification-test-plan`), run with the current `registry.gitlab.com/openid/conformance-suite` image, static client, `client_secret_basic`.

| Result | Count |
| :--- | :---: |
| Passed | 17 |
| Skipped | 2 (`oidcc-client-test-idtoken-sig-none` in both plans: OpenInvento rejects the unsigned ID token without calling UserInfo, and the suite skips the module because clients need not support `alg: none`) |
| Failed | 1 (`oidcc-client-test-discovery-jwks-uri-keys`, see below) |

- `*-export.zip` – the suite's own HTML export of each plan, including the signed log of every module.
- `results.json`, `run-log.txt` – summary of the run.
- `<plan>/<module>.png` – OpenInvento's login page after each module; `<plan>/<module>.findings.json` – the suite's status and its FAILURE/WARNING log entries (the throwaway client secret of the test run is redacted here; the signed exports are unchanged).

`oidcc-client-test-discovery-jwks-uri-keys` ends as soon as the client has fetched the discovered `jwks_uri`. OpenInvento then continues the same login with the UserInfo request, which reaches the already finished module and is logged as "Illegal test state change: FINISHED -> RUNNING". The module's own checks (discovery first, keys from the discovered `jwks_uri`) passed.

## Provider matrix

`provider-matrix/` – real browser logins (Playwright) behind a TLS proxy against Pocket ID 2.18.0, Keycloak 26.8.1 and Dex v2.44.0: first login, second login on the same account, no local password; screenshots in light/dark and desktop/mobile; `claims.json` records each provider's discovery metadata and the claims of its real ID token and UserInfo response (no tokens). In `run-log.txt`, a first attempt per provider may show `ERR_NETWORK_CHANGED` from Chromium starting in a fresh container; it is retried automatically.

## Docker image

`docker-run-log.txt` – the image built from the branch, behind Caddy with TLS, against Pocket ID: three logins via `https://inventory.test` (redirect URI from `APP_URL`), authorization code injection (Pocket ID refuses the token request, PKCE) and login CSRF (state not in the victim's session) both rejected, local login rules.
