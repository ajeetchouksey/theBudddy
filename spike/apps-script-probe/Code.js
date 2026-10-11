/**
 * Spike probe for tests 6, 7 and 20 (docs/spike-results.md).
 *
 * Checks that a web app with ONLY the drive.file scope can create a sheet and write to it
 * through the Sheets API, that long links arrive intact, and that a repeated nonce writes
 * nothing twice. Throwaway code: the real action-link app is task P8.
 *
 *   ?a=setup                 create the "Spike probe" sheet (once)
 *   ?a=write&n=<nonce>       append one row; the same nonce again writes nothing
 *   ?a=status                rows so far
 *   ?a=long&len=200&pad=...&end=END   check a long link arrived unchanged
 */

const SHEET_TITLE = 'Spike probe';
const NONCE_PATTERN = /^[A-Za-z0-9_-]{1,64}$/;

function doGet(e) {
  const p = (e && e.parameter) || {};
  const lock = LockService.getUserLock();
  lock.waitLock(10000);
  try {
    switch (p.a || 'status') {
      case 'setup':
        return page_(setup_());
      case 'write':
        return page_(write_(String(p.n || ''), String(p.src || '')));
      case 'long':
        return page_(checkLong_(p));
      case 'status':
        return page_(status_());
      default:
        return page_('Unknown action.');
    }
  } catch (err) {
    return page_('Error: ' + err.message);
  } finally {
    lock.releaseLock();
  }
}

function sheetId_() {
  return PropertiesService.getUserProperties().getProperty('sheetId');
}

function setup_() {
  const existing = sheetId_();
  if (existing) return 'Already set up. Sheet: ' + sheetUrl_(existing);
  const created = Sheets.Spreadsheets.create({
    properties: { title: SHEET_TITLE },
    sheets: [{ properties: { title: 'Log' } }],
  });
  const id = created.spreadsheetId;
  Sheets.Spreadsheets.Values.update(
    { values: [['ts', 'nonce', 'src', 'value']] },
    id,
    'Log!A1:D1',
    {
      valueInputOption: 'RAW',
    }
  );
  PropertiesService.getUserProperties().setProperty('sheetId', id);
  return 'Created with drive.file only. Sheet: ' + sheetUrl_(id);
}

function write_(nonce, src) {
  const id = sheetId_();
  if (!id) return 'Run ?a=setup first.';
  if (!NONCE_PATTERN.test(nonce)) return 'Bad nonce. Use letters, digits, - or _ (max 64).';
  const seen = Sheets.Spreadsheets.Values.get(id, 'Log!B2:B').values || [];
  if (seen.some((row) => row[0] === nonce)) {
    return 'Already done: ' + nonce + '. Nothing was written twice.';
  }
  Sheets.Spreadsheets.Values.append(
    { values: [[new Date().toISOString(), nonce, src.slice(0, 20), 'PROBE-WRITE-OK']] },
    id,
    'Log!A:D',
    { valueInputOption: 'RAW', insertDataOption: 'INSERT_ROWS' }
  );
  return 'Written: ' + nonce + '. Tap the same link again: it should say "Already done".';
}

function status_() {
  const id = sheetId_();
  if (!id) return 'Not set up yet. Open ?a=setup.';
  const rows = Sheets.Spreadsheets.Values.get(id, 'Log!A2:D').values || [];
  return 'PROBE-STATUS-OK · rows: ' + rows.length + ' · sheet: ' + sheetUrl_(id);
}

function checkLong_(p) {
  const want = Number(p.len || 0);
  const pad = String(p.pad || '');
  const ok = want > 0 && pad.length === want && p.end === 'END' && p.n && p.k;
  return ok
    ? 'params ok (pad ' + pad.length + ' chars, every parameter arrived)'
    : 'params broken: pad ' + pad.length + ' of ' + want + ', end=' + (p.end || 'missing');
}

function sheetUrl_(id) {
  return 'https://docs.google.com/spreadsheets/d/' + id;
}

function page_(message) {
  const safe = String(message).replace(/[&<>"']/g, (c) => '&#' + c.charCodeAt(0) + ';');
  return HtmlService.createHtmlOutput(
    '<meta name="viewport" content="width=device-width, initial-scale=1">' +
      '<p style="font:16px system-ui;margin:16px">' +
      safe +
      '</p>'
  ).setTitle('Spike probe');
}
