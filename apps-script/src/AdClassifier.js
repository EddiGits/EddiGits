/**
 * Inbox advertisement classifier, powered by Jev (TypeSafe AI "System One").
 *
 * For each thread in the Gmail inbox, the text of its messages is sent to
 * Jev, which answers "is this entirely an advertisement?" as a probability.
 * Threads judged to be advertisements get the label AD_LABEL and are moved
 * out of the inbox (a Gmail label is what Gmail shows as a "folder").
 * Every thread that has been looked at gets CHECKED_LABEL so re-runs skip it.
 *
 * Setup (once): Project Settings > Script properties > add
 *   JEV_API_KEY   your TypeSafe API key (required, never put it in code)
 * Optional properties:
 *   JEV_MODEL     default "jev-latest"
 *   AD_THRESHOLD  probability needed to count as an ad, default 0.8
 *   MAX_THREADS   threads per run, default 500
 *   AD_LABEL      default "Jev/Advertisements"
 *   CHECKED_LABEL default "Jev/Checked"
 *
 * Entry points (run from the editor):
 *   previewInbox()   classify but change nothing; results go to the log
 *   classifyInbox()  classify, label, and archive advertisements
 *   resetChecked()   remove CHECKED_LABEL from every thread so a run starts over
 */

var JEV_ENDPOINT = 'https://api.typesafe.ai/v1/systemone';

var DEFAULTS = {
  JEV_MODEL: 'jev-latest',
  AD_THRESHOLD: '0.8',
  MAX_THREADS: '500',
  AD_LABEL: 'Jev/Advertisements',
  CHECKED_LABEL: 'Jev/Checked'
};

// Apps Script kills a run after 6 minutes; stop early and let the next run
// continue from where this one left off (unchecked threads).
var TIME_BUDGET_MS = 5 * 60 * 1000;
var MAX_CHARS_PER_MESSAGE = 6000;
var MAX_CHARS_PER_THREAD = 20000;
var SEARCH_PAGE_SIZE = 50;

/** Classify inbox threads and log the decisions without changing anything. */
function previewInbox() {
  return runClassifier_(false);
}

/** Classify inbox threads, label advertisements, and move them out of the inbox. */
function classifyInbox() {
  return runClassifier_(true);
}

/** Forget which threads were already checked, so the next run reconsiders all of them. */
function resetChecked() {
  var cfg = getConfig_();
  var label = GmailApp.getUserLabelByName(cfg.CHECKED_LABEL);
  if (!label) return 'nothing to reset';
  var removed = 0;
  while (true) {
    var threads = label.getThreads(0, 100);
    if (threads.length === 0) break;
    label.removeFromThreads(threads);
    removed += threads.length;
  }
  return 'removed ' + cfg.CHECKED_LABEL + ' from ' + removed + ' threads';
}

function runClassifier_(apply) {
  var cfg = getConfig_();
  var started = Date.now();
  var adLabel = apply ? getOrCreateLabel_(cfg.AD_LABEL) : null;
  var checkedLabel = apply ? getOrCreateLabel_(cfg.CHECKED_LABEL) : null;
  var query = 'in:inbox -label:' + cfg.CHECKED_LABEL.replace(/ /g, '-');

  var stats = { looked: 0, ads: 0, notAds: 0, errors: 0, stoppedEarly: false };
  var offset = 0;

  while (stats.looked < cfg.MAX_THREADS) {
    if (Date.now() - started > TIME_BUDGET_MS) {
      stats.stoppedEarly = true;
      break;
    }
    var pageSize = Math.min(SEARCH_PAGE_SIZE, cfg.MAX_THREADS - stats.looked);
    // When applying, checked threads drop out of the query, so always read
    // from the start; in preview mode nothing changes, so page forward.
    var threads = GmailApp.search(query, apply ? 0 : offset, pageSize);
    if (threads.length === 0) break;
    offset += threads.length;

    for (var i = 0; i < threads.length; i++) {
      if (Date.now() - started > TIME_BUDGET_MS) {
        stats.stoppedEarly = true;
        break;
      }
      var thread = threads[i];
      stats.looked++;
      var subject = thread.getFirstMessageSubject();
      try {
        var verdict = judgeThread_(thread, cfg);
        var line =
          (verdict.isAd ? 'AD     ' : 'not ad ') +
          '(p=' + verdict.probability.toFixed(2) + ') ' +
          subject;
        Logger.log(line);
        if (verdict.isAd) stats.ads++;
        else stats.notAds++;
        if (apply) {
          if (verdict.isAd) {
            thread.addLabel(adLabel);
            thread.moveToArchive();
          }
          thread.addLabel(checkedLabel);
        }
      } catch (err) {
        stats.errors++;
        Logger.log('ERROR  ' + subject + ' :: ' + err);
        // Leave the thread unchecked so a later run retries it.
      }
    }
    if (stats.stoppedEarly) break;
  }

  var summary =
    (apply ? 'classifyInbox' : 'previewInbox') +
    ': looked at ' + stats.looked +
    ', ads ' + stats.ads +
    ', not ads ' + stats.notAds +
    ', errors ' + stats.errors +
    (stats.stoppedEarly ? ' (time budget hit, run again to continue)' : '');
  Logger.log(summary);
  return summary;
}

/** Ask Jev whether a thread is entirely an advertisement. */
function judgeThread_(thread, cfg) {
  var state = threadToState_(thread);
  var answers = askJev_(state, cfg);
  var ans = answers.is_ad;
  if (!ans || typeof ans.noul !== 'number') {
    throw new Error('unexpected Jev response: ' + JSON.stringify(answers));
  }
  return { probability: ans.noul, isAd: ans.noul >= cfg.AD_THRESHOLD };
}

/** Flatten a thread into the plain text Jev will judge. */
function threadToState_(thread) {
  var messages = thread.getMessages();
  var parts = [];
  var total = 0;
  for (var i = 0; i < messages.length && total < MAX_CHARS_PER_THREAD; i++) {
    var m = messages[i];
    var body = (m.getPlainBody() || '').replace(/\s+/g, ' ').trim();
    if (body.length > MAX_CHARS_PER_MESSAGE) {
      body = body.slice(0, MAX_CHARS_PER_MESSAGE) + ' [truncated]';
    }
    var text =
      'From: ' + m.getFrom() + '\n' +
      'To: ' + m.getTo() + '\n' +
      'Subject: ' + m.getSubject() + '\n' +
      'Body: ' + body;
    parts.push(text);
    total += text.length;
  }
  return parts.join('\n\n---\n\n');
}

/** One Jev call with retry on rate limit / overload. Returns the answers object. */
function askJev_(state, cfg) {
  var payload = {
    model: cfg.JEV_MODEL,
    state: state,
    questions: {
      is_ad: {
        type: 'noul',
        instructions:
          'Is this email entirely an advertisement? Answer yes only if the ' +
          'whole email exists to promote, sell, or market a product, service, ' +
          'offer, sale, or brand (marketing newsletters, promotions, deals, ' +
          'product launches, sponsored content). Answer no if any part of it ' +
          'is a personal or work message, a receipt or order or shipping ' +
          'update, a bill or invoice, an account or security notice, a ' +
          'one-time code, a calendar or meeting message, a support reply, or ' +
          'a message the recipient specifically asked for.'
      }
    }
  };
  var options = {
    method: 'post',
    contentType: 'application/json',
    headers: { Authorization: 'Bearer ' + cfg.JEV_API_KEY },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  var delay = 1000;
  for (var attempt = 0; attempt < 5; attempt++) {
    var res = UrlFetchApp.fetch(JEV_ENDPOINT, options);
    var code = res.getResponseCode();
    if (code === 200) {
      return JSON.parse(res.getContentText()).answers || {};
    }
    if (code === 429 || code === 529 || code >= 500) {
      Utilities.sleep(delay);
      delay *= 2;
      continue;
    }
    throw new Error('Jev HTTP ' + code + ': ' + res.getContentText().slice(0, 300));
  }
  throw new Error('Jev still failing after retries');
}

function getOrCreateLabel_(name) {
  return GmailApp.getUserLabelByName(name) || GmailApp.createLabel(name);
}

function getConfig_() {
  var props = PropertiesService.getScriptProperties();
  var cfg = {};
  Object.keys(DEFAULTS).forEach(function (k) {
    cfg[k] = props.getProperty(k) || DEFAULTS[k];
  });
  cfg.JEV_API_KEY = props.getProperty('JEV_API_KEY');
  if (!cfg.JEV_API_KEY) {
    throw new Error(
      'JEV_API_KEY is not set. Add it under Project Settings > Script properties.'
    );
  }
  cfg.AD_THRESHOLD = Number(cfg.AD_THRESHOLD);
  cfg.MAX_THREADS = Number(cfg.MAX_THREADS);
  return cfg;
}
