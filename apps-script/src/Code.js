/**
 * EddiGits Apps Script starter.
 *
 * Deployed and managed with clasp from the EddiGits repo (apps-script/).
 * Replace or extend these functions with the automation you need.
 */

/** Returns a short summary of the most recent Gmail threads. */
function listRecentThreads(maxThreads) {
  var limit = maxThreads || 10;
  var threads = GmailApp.getInboxThreads(0, limit);
  return threads.map(function (t) {
    return {
      subject: t.getFirstMessageSubject(),
      from: t.getMessages()[0].getFrom(),
      date: t.getLastMessageDate().toISOString(),
      messageCount: t.getMessageCount()
    };
  });
}

/** Simple health check used to confirm the deployment works. */
function ping() {
  return 'ok ' + new Date().toISOString();
}

/** Web-app entry point so the script can be called over HTTPS. */
function doGet(e) {
  var out = { status: ping() };
  return ContentService.createTextOutput(JSON.stringify(out)).setMimeType(
    ContentService.MimeType.JSON
  );
}
