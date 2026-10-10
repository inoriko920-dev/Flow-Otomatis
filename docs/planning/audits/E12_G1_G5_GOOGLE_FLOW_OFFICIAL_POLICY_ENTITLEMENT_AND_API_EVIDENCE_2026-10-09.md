# Flow-Otomatis — G1/G5 official Google Flow policy, entitlements, credits and supported API audit

**Checked:** 2026-10-09 WIB. **Scope: official public-doc review only**, no account access, browser automation, quota tests, Google Flow Generate/Download, spending, schema/app changes, or PR merge. **Decision: G1 automated multi-account/browser actions remain UNKNOWN / BLOCKED. G5 per-account evidence remains UNVERIFIED.** This is a pre-implementation and safety audit, **NOT permission**.

## Executive finding

Google's public Terms and Flow help pages provide general service restrictions, supported regions, credit disclosures and first-party interactive features. **The researched public official pages do NOT provide affirmative permission for a third-party Windows app to operate several individually signed-in Flow accounts with browser/CDP automation, aggregate their free credits and dispatch billed generations in parallel.** The absence of an explicit permission in those pages is **not a categorical statement that all browser automation is forbidden**, but it **cannot clear G1**. Require an applicable provider authorization/policy determination for the specific operation; otherwise disable live mutations and provide allowed manual/official pathways.

The Google Terms prohibit abuse, bypassing protective systems, deceptive behavior, and automated access that violates machine-readable site instructions; Google Flow also documents throttling when generations happen too quickly and unusual-activity warnings. **Do not route new jobs through other accounts in response to a quota, activity warning, failed/ambiguous submit, or free-tier exhaustion; do not automate MFA/captcha or anti-bot circumvention.** [TOS-01] [FLOW-START]

## 1. Source-of-evidence register (official first-party URLs)

| ID | Source | Direct URL | What it proves | What it does NOT prove |
|---|---|---|---|---|
| TOS-01 | Google Terms of Service, effective 2026-07-30 | https://policies.google.com/terms?hl=id | Abuse/anti-circumvention and automated access contrary to machine-readable instructions prohibited. | No explicit Flow multi-account third-party automation permission. |
| FLOW-START | Get started with Google Flow | https://support.google.com/flow/answer/16353333?hl=id | Age/region/subscription guidance, generation throttling, abnormal activity; Model/credits vary. | No Chrome CDP automation authorization; page's subscription requirements conflict with separate current free-credit guidance. |
| FLOW-REGION | Where you can use Google Flow | https://support.google.com/flow/answer/16353544?hl=en | **Indonesia is listed** as a supported country; feature eligibility may differ by region; some content classes unsupported. | No guarantee for a particular Google account/model or browser automation. |
| FLOW-CREDIT | Manage your Google Flow credits | https://support.google.com/flow/answer/16526234?hl=id | Public credit allocations, per-generation tariffs, account credit activity; costs may change. | No proof that user's accounts have 50 available today, or that a free account has Omni Flash 720p eligibility. |
| FLOW-AGENT | Use the Google Flow Agent | https://support.google.com/flow/answer/17093911?hl=id | First-party Agent can help create media, including multiple variations, inside Flow with credit awareness and configurable confirmation. | Not third-party browser/multi-account automation authorization or an external Agent API. |
| FLOW-POLICY | Generative AI Prohibited Use Policy | https://policies.google.com/terms/generative-ai/use-policy?hl=id | Do not bypass protections/abuse and respect safety/content restrictions. | Does not explicitly grant multi-profile automation. |
| API-DOC | Video generation in Gemini API (Omni Flash and Veo) | https://ai.google.dev/gemini-api/docs/video | Official developer API exists, including Omni Flash, separate from Flow website. | Does not transfer or spend Google Flow free/subscription credits. |
| API-OMNI | Gemini Omni Flash in Gemini API | https://ai.google.dev/gemini-api/docs/omni | Official programmable Omni Flash workflow via Interactions API. | Not proof of parity with website's signed-in Flow entitlement/frozen exact output settings. |
| API-PRICE | Gemini Developer API pricing | https://ai.google.dev/gemini-api/docs/pricing | `gemini-omni-1.1-flash` is paid-tier only: no free API tier, approximate US$0.10 per 720p output-video second **plus separate input billing**; quoted public baseline. | No free Flow credits via API, no promise of billing or availability for the user's Google account. |
| API-TERMS | Gemini API Additional Terms effective 2026-03-23 | https://ai.google.dev/gemini-api/terms.md | Developer API has separate rules, regional/usage restrictions. | Cannot be used as a blanket license for browser-automating consumer Flow. |

**Caveat:** web pages can change. The above is a research snapshot, not legal advice; check current on-screen product notice and obtain provider-specific review before any live action.

## 2. G1 policy analysis — separate rights and technical access

| Proposed action | Evidence | Classification | Gate action |
|---|---|---|---|
| Plan scenes/credits on Windows offline with no provider access | Internal program behavior only | **Allowed internal planning scope** | May prepare docs/simulations; does not trigger provider mutation. |
| Owner manually signs in to a legitimately owned Google account in standard Chrome | First-party interactive UI described; privacy/identity gate is separate | **Normal manual user interaction in supported region, subject to account terms** | No credential/session storage or unattended MFA; no claim of automated access permission. |
| Third-party Chrome/CDP worker reads session/profile or credits | No explicit affirmative third-party Flow API/automation policy located in researched official pages | **UNKNOWN for proposed mode** | G1 blocks unattended browser/session automation, even if technically feasible. |
| Third-party worker presses Flow Generate / Download from a signed-in browser | No affirmative authorization for proposed automated operation; service restrictions apply | **G1 BLOCKED (not verified permitted)** | No live mutating browser actions. Login success or screenshots cannot clear G1. |
| 2+ accounts automatically route requests to pool free Flow credits/avoid throttles | No affirmative multi-account allowance; free/abuse controls and account-bound credit semantics | **HIGH-RISK / BLOCKED** | Do not implement quota-fallback/auto-rotation or bypass behavior; request explicit provider clearance for the particular use. |
| Manual use of Google Flow Agent by owner within UI | Google directly documents Agent actions and confirmation settings | **Official interactive feature**, conditional on account eligibility | Can be discussed as a compliant human-operated path, not as authorization to automate the Agent externally. |
| Use `gemini-omni-1.1-flash` via documented Gemini API | Google publishes API and paid rates | **Official programmable alternative (paid)** | Requires separate owner agreement to the feature/cost, project/region/credential protection and API Terms; **not** the free-credits implementation originally requested. |

**Important interpretation:** Google's Terms prohibit automated access **that violates site machine-readable instructions**, not necessarily every automated activity categorically. The researched official materials do not show Flow-specific machine-readable instructions, consent or a third-party UI automation license for the intended account aggregation. Therefore the product must default **DENY for live automation while G1 remains UNKNOWN**, rather than incorrectly asserting universal legal prohibition or positive permission.

## 3. G5 public credit facts vs actual balance/eligibility

Official Flow credit guide (checked 2026-10-09) states:

- Users *without a subscription* are described as receiving **50 daily Flow credits**, with peak-hour restrictions and no daily rollover. Plus adds **200 monthly**, Pro **1,000 monthly**, and Ultra tier(s) further monthly amounts. Credit pools/activity are **account-bound**, not device-bound; purchased AI credits and family sharing have separate rules. **Do not infer every new account is eligible to generate the fixed Omni Flash model.**
- **Frozen project profile**: `Gemini Omni Flash 1.1 / 720p / 16:9`, video durations **4/6/8/10s**, one independently priced generated output. The official **Gemini Omni Flash (720p)** page tariff is **7/10/12/15 Flow credits per generated video**, corresponding to **4/6/8/10 seconds** respectively. Edits and other models cost differently; multi-output requests multiply chargeable outputs. All prices are **public reference**, not actual user's account quote.
- Credit snapshot **must** include current profile identity, actual relevant model eligibility, provider-observed balance and expiry, per-output cost, count of outputs, timestamp/source evidence, owner's budget cap, and user-approved plan digest. Unknown or stale ⇒ **simulation only**, not dispatch.
- **Documented content discrepancy requiring per-account check**: the official *Get started with Flow* page still says subscription required to access Flow and that Pro enables latest Omni Flash. Meanwhile the current *Manage Flow credits* page says non-subscribers can receive 50/day and quotes 720p Omni Flash tariffs for “all users”; another Flow help section limits certain no-subscription free credits to specific Veo variants. These may reflect partial rollouts, documentation lag, or differentiated entitlements — **do not resolve this contradiction by guessing**. Particular Omni Flash availability must be verified *for each profile* before any future authorized action.
- The user does **not** need to supply account login, password, cookies, Chrome profile dumps, tokens or personal account identifiers to the repo/chat for documentation review.

## 4. Official API path: real alternative, not a free-credit loophole

- Google documents `gemini-omni-1.1-flash` (API) on the **paid tier**, **Free Tier: Not available**. Public effective standard price around **US$0.10 per output second of 720p video** (5,792 video tokens/sec at US$17.50/million video output tokens). **Input video/image/text/audio tokens are billed separately**; not a complete per-clip quote.
- Programmatic service is under **Gemini API Additional Terms**, not automatically governed by Flow website credit subscriptions. API keys, developer project billing, rates, region, settings and model capabilities must be independently checked before design/activation.
- **Do not silently switch Flow-Otomatis** to Gemini API, another model, lower resolution, paid charges, or a credit-card requirement. It would require a new explicit product decision and budget/credential gates.

## 5. Operational decision and next evidence checklist

**G1 = UNKNOWN/BLOCKED; G5 public-reference tariff = documented/partial; G5 actual per-account credits/model access = UNVERIFIED; G6 READY after full app restart = UNVERIFIED.** These gates are independent of owner approval of architecture D01–D06 and G0 canonical references. One signoff does not waive them.

**No provider mutation before verification.** The next responsible review asks Google/official support for written guidance specifically on:
1. Third-party desktop application (Python/PySide6) using Chrome browser/CDP to interact with signed-in Flow, including Generate and Download.
2. Whether multiple separately owner-authorized Google accounts may be concurrently controlled from one local machine.
3. Whether credit pooling/task-shifting across accounts is allowed, particularly around free-tier limits and anti-abuse throttles.
4. Whether any **documented first-party API/approved integration** exists to generate/download via Flow subscriptions without automation of consumer UI; otherwise official paid Gemini API is a *separate* optional product.
5. Per-account/regional entitlement for Omni Flash 720p at 4/6/8/10s and approved output counts, limits, and quote refresh rules.

Until an affirmative, applicable determination is recorded: **no live account automation**, no active scheduler dispatch, no auto-switching after exhausted quotas, and no trial generation using credits. Work may continue in review-only docs, mock UI already approved, offline deterministic simulation and safety acceptance test *planning* as allowed by repository governance — **new source coding still blocked**.

## 6. Cross-PR governance and audit trail

- PR #25: 22 owner-approved UI PNG + 2 DOCX, **24/24 archive PASS**, draft/unmerged, original 30-UI visual authority selected by owner.
- PR #26: ADR-020..023 and T06 D01–D06 **OWNER APPROVED DESIGN ONLY**, draft/unmerged, no new coordinator source/tests.
- PR #27: six original planning DOCX **6/6 remote archive PASS**, G0-A/B/C canonical source choice **OWNER APPROVED**, draft/unmerged.
- This G1/G5 report: documentation-only and **does not modify any of those PRs** or `main`. Previous references to unpaid/50 credits never imply live automation permission.
