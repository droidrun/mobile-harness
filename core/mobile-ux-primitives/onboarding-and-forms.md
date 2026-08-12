# Onboarding & Forms

## Intro carousels
First-launch screens often present 2-5 full-screen panels (illustration + short text) with dots at the bottom indicating position, advanced by swiping or an explicit "Next" button, and a "Skip" option usually top-right or top-left. These are marketing/orientation content, not configuration — skipping is almost always safe and reversible (nothing is being set that can't be changed later in settings).

## Coach marks / tooltips
Short-lived overlays that highlight one specific UI element the first time it's relevant (a spotlight or circle around an icon, with a brief explanation and a "Got it"/"×" dismissal). These indicate the app itself expects this to be a point of confusion, so the behaviour they describe is worth capturing — as your own paraphrase of what the overlay teaches plus the element it points at, never as the overlay's own imperative sentence copied across. See `core/learn-from-tutorial/GUIDE.md`, which owns the capture rules and why they exist.

## Progress indicators in multi-step forms
A fraction ("Step 2 of 4"), a horizontal progress bar, or a row of dots communicates how much of a flow remains. Use this to distinguish "this form has more steps coming" from "this is the final confirmation" before assuming a flow is complete.

## Inline validation
Many forms validate a field as soon as it loses focus (tapping the next field) rather than only on submit — an error message appearing under a field you just left is expected behavior, not a sign the previous action failed. Conversely, a submit button that stays visually disabled/greyed usually means a required field is still invalid or empty somewhere on the screen, including possibly one not currently visible.

## Autofill and saved data
Tapping a field sometimes surfaces a suggestion bar (saved passwords, addresses, payment info) above the keyboard. Selecting a suggestion fills the field immediately — treat that as equivalent to typing the value manually, not as a separate confirmation step.

## OAuth / SSO handoffs
"Continue with Google/Apple/Facebook" buttons hand off to that provider's own login UI (either an in-app webview or a full app-switch) and return automatically on success. Expect the returned screen to differ from where the button was tapped (usually landing on a home/dashboard screen post-auth) — this is success, not disorientation.

## Required vs. optional fields
Asterisks, "(optional)" labels, or subtly different field styling typically distinguish required fields from optional ones. When a submit action is blocked with no visible error, check optional-looking fields too — some forms mark requirements inconsistently across screens within the same app.
