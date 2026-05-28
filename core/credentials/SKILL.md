---
name: android-mobile-credentials
description: Use when an Android screen asks for login, password, API key, OTP, 2FA, recovery code, payment details, or other secrets while using mobile-harness-android.
---

# Android Credentials

Default behavior: stop and ask the user if credentials are not already explicitly authorized.

## Credential Screens

Treat these as credential or human-gated screens:

- username, email, phone login
- password
- API key or access token
- OTP, 2FA, authenticator code, recovery code
- captcha or anti-bot challenge
- payment card, bank, billing, or purchase confirmation
- account deletion, logout, uninstall, data wipe, or destructive consent

## Ask Before Acting

Ask one short question and wait. Offer concrete options:

- user takes over on the device
- user provides/authorizes a local credentials file
- user enters credentials on the device
- user approves skipping the login-gated task

Do not ask the user to paste secrets into the chat unless they explicitly choose that path.

## Local Credential Files

`credentials/` is local and ignored by git. If the user explicitly authorizes stored credentials, read only the file for the current package:

```text
credentials/<package>.md
```

Example shape:

```markdown
# com.example.app

- username: user@example.com
- password: stored outside chat
- notes: ask user for OTP every login
```

Use only the minimum required field. Redact values in logs and summaries.

## Never

- Write credentials to `memory/`.
- Commit credential files.
- Print secrets back to the user.
- Reuse credentials for a different app/package.
- Submit payment, purchase, deletion, or account recovery without explicit approval for that exact action.
