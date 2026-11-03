# Mobilerun Ops Helper

Optional Node 20 helper for bounded Mobilerun Cloud checks from this repository. Normal device automation remains the root Python `mobilerun_core.Mobilerun` harness.

## Install

```bash
cd tools/mobilerun-ops
npm install
```

## Environment

```bash
export MOBILERUN_CLOUD_API_KEY="..."
export MOBILERUN_BASE_URL="https://api.mobilerun.ai/v1"
export MOBILERUN_CLOUD_DEVICE_ID="<device-id>"
```

`MOBILERUN_BASE_URL` is optional. The SDK defaults to Mobilerun Cloud. Do not put API keys or live device ids in source files.

## Commands

```bash
npm run check
node droidrun_mobilerun_ops.mjs --help
node droidrun_mobilerun_ops.mjs health
node droidrun_mobilerun_ops.mjs devices --page-size 5
node droidrun_mobilerun_ops.mjs apps --query settings --page-size 5
node droidrun_mobilerun_ops.mjs open-app --app com.android.settings
node droidrun_mobilerun_ops.mjs ui-summary
node droidrun_mobilerun_ops.mjs screenshot
node droidrun_mobilerun_ops.mjs warmup
```

Commands print sanitized JSON. Task based commands write result metadata under `tools/mobilerun-ops/evidence/` when a task id is returned. The helper intentionally refuses to run cloud calls without `MOBILERUN_CLOUD_API_KEY`.

## Notes

- The helper uses `@mobilerun/sdk` and the public task APIs.
- `open-app`, `ui-summary`, `screenshot`, and `warmup` require `MOBILERUN_CLOUD_DEVICE_ID` or `--device-id`.
- Passive commands instruct the cloud agent not to submit forms, send messages, pay, delete, or change account settings.
- If a credential, payment, one-time code, KYC, legal consent, or destructive action appears, stop and ask the user for exact authorization.
