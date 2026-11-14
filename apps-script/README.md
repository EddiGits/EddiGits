# Apps Script (managed with clasp)

Google Apps Script source for EddiGits automations, versioned here and pushed
to Google with [clasp](https://github.com/google/clasp).

## One-time setup

1. Turn on the Apps Script API at https://script.google.com/home/usersettings.
2. On a trusted machine (Google Cloud Shell works):
   ```
   npm install -g @google/clasp
   clasp login --no-localhost
   cat ~/.clasprc.json
   ```
3. In the Claude Code environment settings, add an environment variable named
   `CLASPRC_JSON` whose value is the full contents of that file.
4. Start a new session and restore the login once per session:
   ```
   npm install -g @google/clasp
   umask 077 && printf '%s' "$CLASPRC_JSON" > ~/.clasprc.json
   clasp show-authorized-user
   ```

`~/.clasprc.json` must never be committed. `.clasp.json` (project id) is safe to commit.

## Daily use (from this folder)

This folder is linked (via `.clasp.json`) to the standalone project
**EddiGits Automations**. Run these from `apps-script/`:

```
clasp status          # files that would be pushed
clasp pull            # bring Google's current version into this folder
clasp push            # upload src/ and appsscript.json
clasp open-script     # open in the browser editor
clasp deploy -d "v1"  # create a deployment
clasp logs            # recent executions
```

Running functions remotely with `clasp run` additionally needs a linked
Google Cloud project and a Desktop OAuth client; see
https://github.com/google/clasp/blob/master/docs/run.md.

Scripts that touch Gmail, Drive, or Sheets need a one-time authorization
click in the Apps Script editor the first time they run.

## What is in here

- `src/Code.js`: starter functions (`ping`, `listRecentThreads`, a web-app `doGet`).
- `src/AdClassifier.js`: inbox advertisement classifier powered by Jev. It
  needs a `JEV_API_KEY` script property; see the header comment for the
  optional properties and the `previewInbox` / `classifyInbox` entry points.
