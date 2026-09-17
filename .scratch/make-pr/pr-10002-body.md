## Context

MyInfo-authed multirespondent forms (MRF) can't collect child data: Children fields are hard-rejected on submission and hidden from the MRF builder. This PR enables them end-to-end behind flags, so MRF forms can start collecting child records once we're ready to turn them on.

**Stack** — 2/7

#10001 fixed MyInfo hash verification on step-1 MRF submissions; this PR opens up the Children field itself, and #10003 adds read-only carry-forward of the answers to steps 2+.

```mermaid
graph LR
    main --> A["#10001<br/>MyInfo hash check"]
    A --> B["#10002<br/>core gates"]
    B --> C["#10003<br/>carry-forward"]
    C --> D["#10004<br/>hash verify"]
    D --> E["#10005<br/>emails &amp; PDF"]
    E --> F["#10006<br/>admin &amp; CSV"]
    F --> G["#10016<br/>scope labels"]
    style B fill:#d4f7d4,stroke:#2da44e,stroke-width:3px
```


## Implementation

Allow Children fields on MRF, gated behind the existing per-admin `betaFlags.children` **and** a new default-off `mrf-children` feature flag.

```mermaid
flowchart TB
  subgraph FE["Frontend"]
    direction LR
    feat["Pages &amp; features<br/><b>+12 −2</b>"]
    feui["UI components"]
    feapi["API client"]
  end
  subgraph CT["Shared contracts"]
    direction LR
    shared["packages/shared<br/><b>+1 −0</b>"]
    sdk["packages/sdk<br/><b>+2 −0</b>"]
  end
  subgraph BE["Backend"]
    direction LR
    route["Routes"]
    mw["Middlewares<br/><b>+7 −0</b>"]
    ctrl["Controllers"]
    svc["Services<br/><b>+125 −31</b>"]
    val["Validation &amp; utils<br/><b>+386 −14</b>"]
    model["Models"]
  end
  feat --> feui
  feat --> feapi
  feapi ==> route
  route --> mw
  mw --> ctrl
  ctrl --> svc
  svc --> val
  svc --> model
  feat -.-> shared
  model -.-> shared
  feat -.-> sdk
  svc -.-> sdk
  classDef touched fill:#1f6feb,stroke:#1f6feb,stroke-width:1px,color:#ffffff;
  classDef tests fill:none,stroke:#1f6feb,stroke-width:2px,color:#1f6feb;
  classDef dim fill:none,stroke:#8b949e,stroke-width:1px,color:#8b949e,stroke-dasharray:4 3;
  class feat,shared,sdk,mw,svc,val touched;
  class feui,feapi,route,ctrl,model dim;
  style FE fill:none,stroke:#8b949e,stroke-width:1px,color:#8b949e;
  style CT fill:none,stroke:#8b949e,stroke-width:1px,color:#8b949e;
  style BE fill:none,stroke:#8b949e,stroke-width:1px,color:#8b949e;
  linkStyle 0 stroke:#8b949e,stroke-width:1px,opacity:0.35;
  linkStyle 1 stroke:#8b949e,stroke-width:1px,opacity:0.35;
  linkStyle 2 stroke:#8b949e,stroke-width:1px,opacity:0.35;
  linkStyle 3 stroke:#8b949e,stroke-width:1px,opacity:0.35;
  linkStyle 4 stroke:#8b949e,stroke-width:1px,opacity:0.35;
  linkStyle 5 stroke:#8b949e,stroke-width:1px,opacity:0.35;
  linkStyle 7 stroke:#8b949e,stroke-width:1px,opacity:0.35;
  linkStyle 9 stroke:#8b949e,stroke-width:1px,opacity:0.35;
```

- **Submission gate (middleware + utils)** — `validateMrfFieldResponses` accepts a Children response only when the flag is on, it's the first workflow step (MyInfo sessions are step-1-only), and the form's auth is MyInfo. The flag check fails closed, mirroring the `mrf-payments` kill switch.
- **Validation** — `constructChildrenValidatorV4` was a no-op; it now enforces the V3 rules on the V4 answer shape: well-formed answer, max-children cap, answered attributes must exactly match the field's subfields, no empty values.
- **Shared contracts** — the `mrf-children` flag constant lands in `packages/shared`, with the V4 children answer types re-exported from the published SDK.
- **Builder (frontend)** — the MyInfo panel offers the Children section on MRF forms when both flags are on.

**Breaking Changes**

No — Children on MRF stays rejected until the default-off `mrf-children` flag is enabled; encrypt-mode behaviour is untouched.

## Tests

**TC1: flag off (default)**

- [ ] MRF + MyInfo form: step-1 Children submission is rejected (422)

**TC2: flag on, happy path**

- [ ] Step-1 Children submission with one complete child is accepted

**TC3: flag on, still rejected**

- [ ] Step-2 respondent posts a *changed* Children response → rejected
- [ ] Non-MyInfo MRF form with a Children response → rejected
- [ ] Tampered payload (extra attribute / empty value / over the max-children cap) → rejected

**TC4: builder**

- [ ] Children section appears for a beta-flagged admin on an MRF form only when the flag is on; encrypt forms unchanged

## Deploy Notes

**New feature flags**:

- `mrf-children` (GrowthBook) — default off; gates Children on MRF end-to-end

🤖 Generated with [Claude Code](https://claude.com/claude-code)
