# Local Credentials

This folder is for optional user-provided credential notes. Runtime credential files are ignored by git.

Read `core/credentials/SKILL.md` before using anything here.

Rules:

- The agent must ask before reading or using a credential file.
- Use one file per package: `credentials/<package>.md`.
- Never commit real credentials.
- Never copy credentials into `memory/`.
- Redact secrets in logs and summaries.
