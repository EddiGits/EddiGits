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
   (clasp 3.x has no `clasp login --status`; `show-authorized-user` is the
   equivalent.)

`~/.clasprc.json` must never be committed. `.clasp.json` (project id) is safe to commit.

## Project

`.clasp.json` points at the standalone project "EddiGits Automations":
https://script.google.com/d/1OPucabRrIbNMniG3OM2j08RsyAxRRoc8lcxa0gzN_yA99upnMi8YAMV8/edit

It was created with
`clasp create --type standalone --title "EddiGits Automations" --rootDir .`.
Note that `clasp create` pulls Google's default manifest over `appsscript.json`;
after any future `create`, run `git checkout -- appsscript.json` before pushing.

## Daily use (from this folder)

```
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

## Inbox advertisement classifier (`src/AdClassifier.js`)

Sends each inbox thread to [Jev](https://docs.typesafe.ai) (TypeSafe AI) and
asks whether it is entirely an advertisement. Threads Jev judges to be ads get
the label `Jev/Advertisements` and are moved out of the inbox; every thread
that has been looked at gets `Jev/Checked` so the next run skips it.

Note that the text of every processed email is sent to TypeSafe's API.

Setup, once, in the Apps Script editor:

1. Project Settings > Script properties > add `JEV_API_KEY` with your TypeSafe
   key. The key lives only in script properties, never in this repo.
2. Optional properties: `AD_THRESHOLD` (default `0.8`), `MAX_THREADS`
   (default `500`), `AD_LABEL`, `CHECKED_LABEL`, `JEV_MODEL`.
3. Pick `previewInbox` in the function dropdown and Run. Grant the Gmail and
   external-request permissions when asked. The execution log shows one line
   per thread with the ad probability; nothing is changed.
4. When the preview looks right, run `classifyInbox`. It stops after
   `MAX_THREADS` threads or five minutes, whichever comes first; run it again
   to continue with the unchecked threads.

`resetChecked` removes `Jev/Checked` everywhere so a run starts over.
