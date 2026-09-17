# FormSG layer reference

What each layer id in `classify_changes.py` means, and why the rule order is
what it is. Update this alongside the `RULES` list.

## The spine

The request path the diagram draws:

```
frontend app shell
  → features
      → api client (*Service.ts, queries.ts, mutations.ts, src/services/)
          │ HTTP
backend routes (routes/api/v3/<domain>/<domain>.routes.ts)
  → middlewares (auth session/permissions, celebrate/Joi, rate limit, captcha)
      → controllers (*.controller.ts — parse, orchestrate, Result → HTTP)
          → services (*.service.ts, plus app/services/ for mail/sms infra)
              → models (Mongoose, *.server.model.ts)
```

`packages/shared` is imported by both sides and must never import from `apps/*`.
`packages/sdk` is consumed by the backend, the frontend, and published to
third-party form owners — changes there reach outside this repo.

## Layer ids

| id | Paths | Role |
|---|---|---|
| `fe-shell` | `apps/frontend/src/{app,pages}/`, `src/index.tsx` | react-router table, auth gating, static/landing pages |
| `fe-feature` | `apps/frontend/src/features/` | Product surface: `admin-form/`, `public-form/`, `workspace/`, `login/`, … Feature pages (`*Page.tsx`) live here, not in `fe-shell` |
| `fe-ui` | `src/{components,templates,theme,assets}/` | Design-system primitives and composed presentational blocks |
| `fe-api` | `src/services/`, `**/*Service.ts(x)`, `**/queries.ts`, `**/mutations.ts`, `**/mutations/` | All HTTP to the backend. Axios via `services/ApiService.ts`, wrapped in react-query hooks |
| `fe-state` | `src/contexts/`, `**/*Store.ts(x)`, `**/*Context.tsx`, `**/*Provider.tsx` | zustand stores and React contexts |
| `fe-hooks` | `src/hooks/`, `**/hooks/` | Shared and feature-local hooks |
| `fe-i18n` | `src/i18n/` | Locale strings |
| `fe-utils` | `src/{utils,constants,typings}/`, vite config, `env.ts` | Frontend-only helpers and config |
| `fe-mocks` | `src/mocks/` | MSW request handlers — test infrastructure |
| `shared` | `packages/shared/` | **The frontend↔backend contract.** `types/`, `constants/` (incl. `routes.ts`), isomorphic `utils/*-validation.ts`, `modules/logic/` |
| `sdk` | `packages/sdk/` | `@opengovsg/formsg-sdk` — published crypto/webhook SDK |
| `be-route` | `app/routes/`, `**/*.routes.ts` | Express router wiring: path → middleware chain → handler |
| `be-middleware` | `**/*.middleware(s).ts`, `app/utils/{pipeline-middleware,limit-rate}.ts` | Auth, Joi validation, rate limiting, captcha/turnstile |
| `be-controller` | `app/modules/**/*.controller.ts` | Request handling, neverthrow `Result` → HTTP mapping |
| `be-service` | `app/modules/**/*.service.ts`, `app/services/` | Domain logic; `app/services/` is cross-cutting infra (mail, sms) |
| `be-model` | `app/models/`, `**/*.server.{model,schema}.ts`, module-local `*.model.ts` | Mongoose persistence |
| `be-support` | `app/modules/**/*.{errors,types,utils,constants,class}.ts` | Per-module non-layer files |
| `be-types` | `apps/backend/src/{types,shared}/` | Document/DTO typings mirroring the models |
| `be-utils` | `app/utils/` | Encryption, hashing, S3, `field-validation/` |
| `be-infra` | `app/{loaders,config,constants}/`, `server.ts` | Bootstrap, convict config, express loaders |
| `be-views` | `app/views/templates/` | Server-rendered email/HTML |
| `email-templates` | `packages/react-email-preview/` | react-email templates |
| `services` | `services/`, `functions/` | Lambdas: payment reconciliation, pdf-gen, virus scanner |
| `scripts` | `scripts/` | Dated one-off migrations, `<YYYYMMDD>_<slug>/`. No migration framework |
| `infra` | `deploy/`, `.github/`, Dockerfiles, husky, lint config | |
| `docs` | `docs/`, `*.md`, `.claude/` | |
| `e2e` | root `__tests__/` | Playwright end-to-end specs |
| `unknown` | — | Nothing matched. A non-empty bucket means the rules are stale |

## How the layers collapse into the diagram

The 27 layers above are the right resolution for *classifying* a path, but too
fragmented for a PR description — a reviewer thinks in about ten boxes, not
thirty. `DIAGRAM` in the script maps them down:

| Diagram node | Collapses |
|---|---|
| Pages & features | `fe-shell`, `fe-feature`, `fe-state`, `fe-hooks`, `fe-i18n`, `fe-utils`, `fe-mocks`, `fe-other` |
| UI components | `fe-ui` |
| API client | `fe-api` |
| packages/shared | `shared` |
| packages/sdk | `sdk` |
| Routes | `be-route` |
| Middlewares | `be-middleware` |
| Controllers | `be-controller` |
| Services | `be-service`, `be-support` |
| Validation & utils | `be-utils` |
| Models | `be-model`, `be-types` |

`fe-ui` stays separate from features because it is frequently the centre of
gravity on its own — a new field type is mostly a new input widget, and folding
it into features hides that.

Everything in `PERIPHERAL` (`be-infra`, `be-views`, `email-templates`,
`services`, `scripts`, `infra`, `docs`, `e2e`, `unknown`) is outside the request
path. Touched peripheral layers become a one-line footnote under the diagram
rather than nodes, so the spine stays readable.

## Ambiguous paths, and how they resolve

These match more than one rule; the ordered list picks the winner deliberately.

- `app/loaders/express/**` (`helmet.ts`, `session.ts`, `error-handler.ts`) — matched
  as **`be-infra`** before the middleware rule. It is app-level bootstrap wiring,
  not a per-route concern, and lumping it into middleware would make every
  server-config change look like a request-path change.
- `app/routes/api/v3/forms/public-form.middleware.ts` — lives under `routes/` but
  is **`be-middleware`**. The middleware rule runs first.
- `app/services/{captcha,turnstile}/*.middleware.ts` — same: **`be-middleware`**,
  not `be-service`.
- `features/**/*Service.ts`, `features/**/queries.ts`, `features/**/mutations.ts` —
  **`fe-api`**, not `fe-feature`. These are the HTTP boundary even though they sit
  inside feature folders; treating them as features would hide every
  frontend→backend crossing.
- `features/**/*Page.tsx` — stays **`fe-feature`**. The real product screens live
  in features; `fe-shell` is only the router and the static pages.
- `pages/Landing/Home/queries.ts` — **`fe-api`**, since the api-client rules
  precede the `pages/` rule.

## The test axis

Test-ness is recorded separately from layer, in `kind` (`source` / `test` /
`story`). Before classification, `__tests__/` and `__mocks__/` segments are
stripped from the path and `.spec` / `.test` / `.stories` suffixes removed, so
`app/models/__tests__/timeField.model.spec.ts` classifies as `be-model` with
`kind: test`.

This matters because backend specs sit in `__tests__/` beside their source while
frontend specs sit directly alongside it — a single "tests" layer would erase
which part of the system the coverage belongs to, and on a test-heavy PR that is
most of the diff.

`source_touched` on each layer is false when only tests moved there.

## Stale directories

Ignore `/shared/` and `/react-email-preview/` at the repo root — leftovers from
the pre-monorepo layout containing only `node_modules`. Also `dist`, `coverage`,
`playwright-report`, `test-results`. `functions/form-payment-reconciliation/` is
an empty stub; the real lambda is under `services/`.
