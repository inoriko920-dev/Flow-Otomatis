# UI IMPLEMENTATION OVERRIDES — STEP 04 Final Review

These written rules are more authoritative than accidental text artifacts in generated UI images.

- UI-IMG-002D: artwork shows an incorrect resolution label; implement **720p** and locked **Omni Flash 1.1 • 720p • 16:9**.
- UI-IMG-003C: handoff output is **VIDEO** (.mp4/official video format), not PNG; summary language is video generated/downloaded.
- UI-IMG-004B: public-person names/avatar/email are illustrative only; runtime uses the user's own profile labels/data.
- UI-IMG-008A: no automatic AI retry; Agent proposes, material retry requires preview + approval. Diagnostics generate/download refers to VIDEO output.
- UI-IMG-008B: S017 diagnostic maps to SCENE_017; SCENE_016 text is an artwork artifact. Sensitive paths/IDs stay redacted.
- UI-IMG-009A: Recovery Center is not a permanent sidebar item. Open it through recovery banner/prompt/temporary route.
- UI-IMG-010C: retry/download wording means retry VIDEO output. Agent may not silently change Target, Selected Flow duration, approved image mapping, prompt, or profile.

Other frozen rules:
- approved reference image normal path = auto-map SCENE_###;
- Target is Audio/SRT source-of-truth;
- 4/6/8/10 are Flow generation choices, user-confirmed and never shorter than Target;
- Generate and Download are separate;
- login/MFA/CAPTCHA is human handoff;
- ambiguous external job is verified before any resubmit.
