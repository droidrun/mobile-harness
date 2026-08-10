# Gmail Android Card

Package: `com.google.android.gm`

Use this card only when Gmail is the foreground package or the task explicitly targets Gmail.

## Useful Labels

- Compose: often visible as `Compose`.
- Search: often visible as `Search in mail`.
- Navigation drawer: content description may include `Open navigation drawer`.
- Account switcher: profile avatar near the top-right.

## Flow Notes

- Prefer structured state labels over coordinate taps.
- After launching, wait for inbox or account picker before acting.
- If Gmail asks to add an account, sign in, or verify identity, stop and read `core/credentials/GUIDE.md`.

## Compose

- `compose_button` opens the composer. Fields: `peoplekit_autocomplete_chip_group` (To), `subject`, `editor` (body). Sent recipients show as `peoplekit_chip` buttons.
- The body `editor` is **not clickable** — tap `composearea_tap_trap_bottom` to focus it. That places the caret at position 0, so `key('delete')` there is a no-op; tap directly on the text to edit the end.
- Add recipients one at a time: re-resolve the empty `EditText` inside the chip group each time (it moves as chips wrap), tap it, type the address, then type `,` to chip it.
- Navigate up (`Navigate up` in `compose_toolbar`) saves the draft; verify it under drawer → `Drafts`.

## Traps

- **`type()` goes to whatever field is actually focused.** If the body is not focused, an entire body silently appends to the subject with no error. Read the destination field back after every write.
- **`clear_input()` does not clear the body** (rich text) and has been seen to clear the *subject* while `editor` reported `is_focused=True`. Do not trust it to target the field you think you are in.
- A contacts-permission dialog (`Allow Gmail to access your contacts?`) and a `Help me write` smart-features bottom sheet can appear mid-typing and swallow keystrokes. Decline both (`DON'T ALLOW`, `No thanks`) — neither is needed to compose — then re-verify what was typed.
- Tapping a fixed coordinate in the To row hits an existing chip and opens a contact sheet or chip popup menu (`Remove the recipient`); `key('back')` backs out.
- Inbox rows can have repeated text; verify the opened message subject after tapping.
- Search results can lag. Observe again before acting on the first result.
- Do not store email contents in memory unless the user explicitly asks.
