/**
 * McCahill Co — July 2026 Schedule Builder
 * =========================================
 * HOW TO USE:
 *  1. Go to sheet.new in your browser  (creates a blank Google Sheet)
 *  2. Click  Extensions → Apps Script
 *  3. Delete all existing code, paste this entire file, and Save (Ctrl+S)
 *  4. Click Run → buildMcCahillSchedule
 *  5. Accept any permission prompts
 *  6. Return to the spreadsheet — three tabs will be built automatically
 *
 * Tabs created:
 *   🗓 July 2026   — full day-by-day calendar
 *   👥 Clients     — client reference with addresses & frequencies
 *   📊 Visit Count — how many visits each client gets in July
 *
 * Colour key:
 *   Lavender  = Full team (Trudy)
 *   Blue      = Kyle + Kierran only
 *   Green     = Booker only
 *   Yellow    = Both teams, different sites
 *   Peach     = Project / special day
 *   Pink-Red  = Canada Day
 *   Light grey= Open day
 */

// ── Colour palette ────────────────────────────────────────────────────────────
const C = {
  navy    : '#1a3a5c',
  blue    : '#2c5f8a',
  lavender: '#d9d2e9',
  skyBlue : '#dae8fc',
  green   : '#d5e8d4',
  yellow  : '#fff2cc',
  peach   : '#fce4d6',
  red     : '#f4cccc',
  grey    : '#f3f3f3',
  notesBg : '#efefef',
  white   : '#ffffff',
  muted   : '#666666',
};

// ── Entry point ───────────────────────────────────────────────────────────────
function buildMcCahillSchedule() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // Remove any previously built versions of these sheets
  ['🗓 July 2026', '👥 Clients', '📊 Visit Count'].forEach(name => {
    const s = ss.getSheetByName(name);
    if (s) ss.deleteSheet(s);
  });

  const cal     = ss.insertSheet('🗓 July 2026',    0);
  const clients = ss.insertSheet('👥 Clients',      1);
  const visits  = ss.insertSheet('📊 Visit Count',  2);

  // Remove the default blank Sheet1 (if it exists and isn't the only sheet)
  try {
    const blank = ss.getSheetByName('Sheet1');
    if (blank) ss.deleteSheet(blank);
  } catch (e) {}

  buildCalSheet(cal);
  buildClientSheet(clients);
  buildVisitSheet(visits);

  ss.setActiveSheet(cal);
  SpreadsheetApp.getUi().alert('✅  McCahill Co – July 2026 schedule is ready!');
}

// ── Shared helper ─────────────────────────────────────────────────────────────
function banner(range, bg) {
  range.setBackground(bg)
       .setFontColor(C.white)
       .setFontWeight('bold')
       .setVerticalAlignment('middle');
}


// ═════════════════════════════════════════════════════════════════════════════
//  CALENDAR SHEET
// ═════════════════════════════════════════════════════════════════════════════
function buildCalSheet(sh) {
  sh.clear();
  sh.clearFormats();
  sh.setTabColor(C.navy);

  // Use explicit row tracking — appendRow(['','','','','']) doesn't advance
  // getLastRow() (all-empty rows don't register), which causes merge conflicts.
  let r = 1;

  // Row 1: Title
  sh.getRange(r, 1, 1, 5).setValues([['McCahill Co  —  July 2026 Field Schedule', '', '', '', '']]);
  const title = sh.getRange(r, 1, 1, 5);
  title.merge();
  banner(title, C.navy);
  title.setFontSize(15).setHorizontalAlignment('center');
  sh.setRowHeight(r, 44);
  r++;

  // Row 2: Legend
  sh.getRange(r, 1).setValue('Colour key:')
    .setFontWeight('bold').setFontSize(8).setFontColor(C.muted);
  sh.getRange(r, 2, 1, 4).merge()
    .setValue('Lavender = Full Team  |  Blue = Kyle + Kierran  |  Green = Booker  |  Yellow = Both Teams (diff sites)  |  Peach = Project / Special  |  Pink = Canada Day')
    .setFontSize(8).setFontColor(C.muted).setFontStyle('italic').setVerticalAlignment('middle');
  sh.getRange(r, 1, 1, 5).setBackground('#f8f8f8');
  sh.setRowHeight(r, 20);
  r++;

  // Row 3: Column headers (freeze here)
  sh.getRange(r, 1, 1, 5).setValues([['Date', 'Day', 'Kyle + Kierran  (Team A)', 'Booker  (Team B)', 'Notes']]);
  const hdr = sh.getRange(r, 1, 1, 5);
  banner(hdr, C.blue);
  hdr.setFontSize(10).setHorizontalAlignment('center');
  sh.setRowHeight(r, 30);
  sh.setFrozenRows(r);
  r++;

  // Data rows
  const bgMap = {
    all: C.lavender, a: C.skyBlue, b: C.green,
    split: C.yellow, project: C.peach, holiday: C.red, open: C.grey,
  };

  calData().forEach(row => {

    // ── thin spacer between weeks ─────────────────────────────────
    if (row.type === 'spacer') {
      sh.getRange(r, 1).setValue(' '); // non-empty so the row registers
      sh.setRowHeight(r, 6);
      sh.getRange(r, 1, 1, 5).setBackground('#d0d0d0');
      r++;
      return;
    }

    // ── week banner ───────────────────────────────────────────────
    if (row.type === 'weekHeader') {
      sh.getRange(r, 1, 1, 5).setValues([['   ' + row.label, '', '', '', '']]);
      const wrng = sh.getRange(r, 1, 1, 5);
      wrng.merge();
      banner(wrng, C.navy);
      wrng.setFontSize(10).setHorizontalAlignment('left');
      sh.setRowHeight(r, 30);
      r++;
      return;
    }

    // ── regular day row ───────────────────────────────────────────
    sh.getRange(r, 1, 1, 5).setValues([[row.date, row.day, row.a, row.b, row.notes]]);
    const bg = bgMap[row.type] || C.grey;

    sh.getRange(r, 1, 1, 4).setBackground(bg);
    sh.getRange(r, 5).setBackground(C.notesBg);
    sh.getRange(r, 1, 1, 5).setFontSize(9).setVerticalAlignment('top').setWrap(true);
    sh.getRange(r, 1).setFontWeight('bold');
    sh.getRange(r, 2).setFontColor(C.muted);
    sh.getRange(r, 5).setFontColor(C.muted).setFontStyle('italic').setFontSize(8);

    // Estimate row height from line count
    const lines = Math.max(
      (row.a.match(/\n/g) || []).length + 1,
      (row.b.match(/\n/g) || []).length + 1,
      (row.notes.match(/\n/g) || []).length + 1,
      3
    );
    sh.setRowHeight(r, Math.max(55, lines * 15 + 12));

    // Bottom divider
    sh.getRange(r, 1, 1, 5).setBorder(
      false, false, true, false, false, false,
      '#cccccc', SpreadsheetApp.BorderStyle.SOLID
    );
    r++;
  });

  // Column widths
  sh.setColumnWidth(1, 105);
  sh.setColumnWidth(2,  85);
  sh.setColumnWidth(3, 275);
  sh.setColumnWidth(4, 275);
  sh.setColumnWidth(5, 200);

  // Outer border
  sh.getRange(1, 1, sh.getLastRow(), 5).setBorder(
    true, true, true, true, false, false,
    '#888888', SpreadsheetApp.BorderStyle.SOLID_MEDIUM
  );
}

// ── Calendar data ─────────────────────────────────────────────────────────────
function calData() {
  return [

    // ── Canada Day Week ───────────────────────────────────────────────────────
    { type:'spacer' },
    { type:'weekHeader', label:'CANADA DAY WEEK  ·  Jul 1–3' },
    { type:'holiday',
      date:'Wed  Jul 1', day:'Wednesday',
      a:'Trudy\n11108 Chalet Rd\n8:00 am – 4:00 pm  ·  8 h',
      b:'Trudy\n11108 Chalet Rd\n8:00 am – 4:00 pm  ·  8 h',
      notes:'🇨🇦 Canada Day\nFull team working' },
    { type:'a',
      date:'Thu  Jul 2', day:'Thursday',
      a:'Ramsay\n11150 Chalet Rd\n8:00 am – 11:00 am  ·  3 h',
      b:'', notes:'' },
    { type:'open',
      date:'Fri  Jul 3', day:'Friday',
      a:'', b:'', notes:'Open' },

    // ── Week 1 ────────────────────────────────────────────────────────────────
    { type:'spacer' },
    { type:'weekHeader', label:'WEEK 1  ·  Jul 6–10  |  Group A bi-weekly' },
    { type:'a',
      date:'Mon  Jul 6', day:'Monday',
      a:'Stratta (Oak Park)\n830 Rogers Ave\n8:00 am – 11:30 am  ·  3.5 h\n\nSens\n4865 Sea Ridge Dr\n12:00 pm – 1:30 pm  ·  1.5 h',
      b:'', notes:'' },
    { type:'split',
      date:'Tue  Jul 7', day:'Tuesday',
      a:'Madeline\n287 King George Terrace\n8:00 am – 12:00 pm  ·  4 h\n\nAnita\n4521 Cheeseman Rd\n12:30 pm – 4:30 pm  ·  4 h',
      b:'Justin\n289 King George Terrace\n8:00 am – 12:00 pm  ·  4 h\n\nLaurie\n495 Norris Rd\n12:30 pm – 2:30 pm  ·  2 h',
      notes:'Both teams start at\nKing George Terrace\n(A @ #287 / B @ #289)' },
    { type:'all',
      date:'Wed  Jul 8', day:'Wednesday',
      a:'Trudy\n11108 Chalet Rd\n8:00 am – 4:00 pm  ·  8 h',
      b:'Trudy\n11108 Chalet Rd\n8:00 am – 4:00 pm  ·  8 h',
      notes:'' },
    { type:'a',
      date:'Thu  Jul 9', day:'Thursday',
      a:'Ramsay\n11150 Chalet Rd\n8:00 am – 11:00 am  ·  3 h',
      b:'', notes:'' },
    { type:'project',
      date:'Fri  Jul 10', day:'Friday',
      a:'Carol Ann\n4070 Lockehaven Dr\n8:00 am – 4:00/5:00 pm\nRegular Service  +  Power Wash Day 1',
      b:'', notes:'Power Wash Day 1\nNo sun required' },
    { type:'project',
      date:'Sat  Jul 11', day:'Saturday',
      a:'Carol Ann\n4070 Lockehaven Dr\nPower Wash Day 2  ☀️',
      b:'', notes:'☀️ Sun required\nFallback: Sat Jul 18\nor Sat Jul 25' },

    // ── Week 2 ────────────────────────────────────────────────────────────────
    { type:'spacer' },
    { type:'weekHeader', label:'WEEK 2  ·  Jul 13–17  |  Group B bi-weekly  +  Stephanie monthly' },
    { type:'a',
      date:'Mon  Jul 13', day:'Monday',
      a:'Stratta (Oak Park)\n830 Rogers Ave\n8:00 am – 11:30 am  ·  3.5 h\n\nSens\n4865 Sea Ridge Dr\n12:00 pm – 1:30 pm  ·  1.5 h\n\nAnita  ⟵ moved from Tue\n4521 Cheeseman Rd\n2:00 pm – 6:00 pm  ·  4 h',
      b:'', notes:'⚠️ Long day\nAnita moved from Tue\n(Stephanie conflict)' },
    { type:'a',
      date:'Tue  Jul 14', day:'Tuesday',
      a:'Stephanie\n1140 Boardman Ln, East Sooke\n8:00 am – ~3:00 pm  ·  5–7 h + travel',
      b:'', notes:'East Sooke full day\n~45 min each way\nDedicated trip' },
    { type:'all',
      date:'Wed  Jul 15', day:'Wednesday',
      a:'Trudy\n11108 Chalet Rd\n8:00 am – 4:00 pm  ·  8 h',
      b:'Trudy\n11108 Chalet Rd\n8:00 am – 4:00 pm  ·  8 h',
      notes:'' },
    { type:'split',
      date:'Thu  Jul 16', day:'Thursday',
      a:'Ramsay\n11150 Chalet Rd\n8:00 am – 11:00 am  ·  3 h\n\nJenicas\n9708 Glenelg Ave\n11:30 am – 4:30 pm  ·  5 h',
      b:'Ian & Judy\n8431 Lawrence Rd\n8:00 am – 2:00 pm  ·  6 h',
      notes:'★ All 3 in\nNorth Saanich / Sidney' },
    { type:'split',
      date:'Fri  Jul 17', day:'Friday',
      a:'Bills\n4475 Tyndall Ave\n8:00 am – 12:00/2:00 pm  ·  4–6 h\n\nJosh\n1026 Roslyn Rd\n12:30/2:30 pm  ·  2 h',
      b:'Andrei\n5577 Alderley Dr\n8:00 am – 12:00 pm  ·  4 h',
      notes:'' },

    // ── Week 3 ────────────────────────────────────────────────────────────────
    { type:'spacer' },
    { type:'weekHeader', label:'WEEK 3  ·  Jul 20–24  |  Group A bi-weekly' },
    { type:'a',
      date:'Mon  Jul 20', day:'Monday',
      a:'Stratta (Oak Park)\n830 Rogers Ave\n8:00 am – 11:30 am  ·  3.5 h\n\nSens\n4865 Sea Ridge Dr\n12:00 pm – 1:30 pm  ·  1.5 h',
      b:'', notes:'' },
    { type:'split',
      date:'Tue  Jul 21', day:'Tuesday',
      a:'Madeline\n287 King George Terrace\n8:00 am – 12:00 pm  ·  4 h\n\nAnita\n4521 Cheeseman Rd\n12:30 pm – 4:30 pm  ·  4 h',
      b:'Justin\n289 King George Terrace\n8:00 am – 12:00 pm  ·  4 h\n\nLaurie\n495 Norris Rd\n12:30 pm – 2:30 pm  ·  2 h',
      notes:'Both teams start at\nKing George Terrace\n(A @ #287 / B @ #289)' },
    { type:'all',
      date:'Wed  Jul 22', day:'Wednesday',
      a:'Trudy\n11108 Chalet Rd\n8:00 am – 4:00 pm  ·  8 h',
      b:'Trudy\n11108 Chalet Rd\n8:00 am – 4:00 pm  ·  8 h',
      notes:'' },
    { type:'a',
      date:'Thu  Jul 23', day:'Thursday',
      a:'Ramsay\n11150 Chalet Rd\n8:00 am – 11:00 am  ·  3 h',
      b:'', notes:'' },
    { type:'a',
      date:'Fri  Jul 24', day:'Friday',
      a:'Carol Ann\n4070 Lockehaven Dr\n8:00 am – 12:00/2:00 pm  ·  4–6 h',
      b:'', notes:'' },

    // ── Week 4 ────────────────────────────────────────────────────────────────
    { type:'spacer' },
    { type:'weekHeader', label:'WEEK 4  ·  Jul 27–31  |  Group B bi-weekly  +  Linda & Fil monthly' },
    { type:'a',
      date:'Mon  Jul 27', day:'Monday',
      a:'Stratta (Oak Park)\n830 Rogers Ave\n8:00 am – 11:30 am  ·  3.5 h\n\nSens\n4865 Sea Ridge Dr\n12:00 pm – 1:30 pm  ·  1.5 h\n\nAnita  ⟵ moved from Tue\n4521 Cheeseman Rd\n2:00 pm – 6:00 pm  ·  4 h',
      b:'', notes:'⚠️ Long day\nAnita moved from Tue\n(Linda & Fil conflict)' },
    { type:'split',
      date:'Tue  Jul 28', day:'Tuesday',
      a:'Linda\n235 Anya Lane, Langford\n8:00 am – 2:00 pm  ·  6 h\n+ joins Fil at 2:00 pm',
      b:'Fil\n233 Anya Lane, Langford\n8:00 am – 2:00 pm  ·  6 h solo\n+ all 3 join 2:00–4:00 pm',
      notes:'★ Full team\nat Anya Lane\nSide-by-side properties' },
    { type:'all',
      date:'Wed  Jul 29', day:'Wednesday',
      a:'Trudy\n11108 Chalet Rd\n8:00 am – 4:00 pm  ·  8 h',
      b:'Trudy\n11108 Chalet Rd\n8:00 am – 4:00 pm  ·  8 h',
      notes:'' },
    { type:'split',
      date:'Thu  Jul 30', day:'Thursday',
      a:'Ramsay\n11150 Chalet Rd\n8:00 am – 11:00 am  ·  3 h\n\nJenicas\n9708 Glenelg Ave\n11:30 am – 4:30 pm  ·  5 h',
      b:'Ian & Judy\n8431 Lawrence Rd\n8:00 am – 2:00 pm  ·  6 h',
      notes:'★ All 3 in\nNorth Saanich / Sidney' },
    { type:'split',
      date:'Fri  Jul 31', day:'Friday',
      a:'Bills\n4475 Tyndall Ave\n8:00 am – 12:00/2:00 pm  ·  4–6 h\n\nJosh\n1026 Roslyn Rd\n12:30/2:30 pm  ·  2 h',
      b:'Andrei\n5577 Alderley Dr\n8:00 am – 12:00 pm  ·  4 h',
      notes:'' },
  ];
}


// ═════════════════════════════════════════════════════════════════════════════
//  CLIENT REFERENCE SHEET
// ═════════════════════════════════════════════════════════════════════════════
function buildClientSheet(sh) {
  sh.clear();
  sh.setTabColor('#34a853');

  sh.appendRow(['McCahill Co  —  Client Reference', '', '', '', '']);
  const title = sh.getRange(1, 1, 1, 5);
  title.merge();
  banner(title, C.navy);
  title.setFontSize(14).setHorizontalAlignment('center');
  sh.setRowHeight(1, 38);

  sh.appendRow(['Client', 'Address', 'Team', 'Frequency', 'Hours / Visit']);
  const hdr = sh.getRange(2, 1, 1, 5);
  banner(hdr, C.blue);
  hdr.setFontSize(10).setHorizontalAlignment('center');
  sh.setRowHeight(2, 28);
  sh.setFrozenRows(2);

  const bgMap = { all: C.lavender, a: C.skyBlue, b: C.green };

  [
    { client:'Stratta (Oak Park)', addr:'830 Rogers Ave',                 team:'Kyle + Kierran  (Kyle on-site)', freq:'Weekly — Monday',    hrs:'3.5 h',                    cat:'a'   },
    { client:'Trudy',              addr:'11108 Chalet Rd',                team:'Full Team  (Kyle on-site)',      freq:'Weekly — Wednesday', hrs:'8 h',                      cat:'all' },
    { client:'Ramsay',             addr:'11150 Chalet Rd',                team:'Kyle + Kierran',                 freq:'Weekly',             hrs:'3 h',                      cat:'a'   },
    { client:'Sens',               addr:'4865 Sea Ridge Dr',              team:'Kyle + Kierran',                 freq:'Weekly',             hrs:'1.5 h',                    cat:'a'   },
    { client:'Anita',              addr:'4521 Cheeseman Rd',              team:'Kyle + Kierran',                 freq:'Weekly',             hrs:'4 h',                      cat:'a'   },
    { client:'Carol Ann',          addr:'4070 Lockehaven Dr',             team:'Kyle + Kierran',                 freq:'Bi-weekly',          hrs:'4–6 h',                    cat:'a'   },
    { client:'Bills',              addr:'4475 Tyndall Ave',               team:'Kyle + Kierran',                 freq:'Bi-weekly',          hrs:'4–6 h',                    cat:'a'   },
    { client:'Madeline',           addr:'287 King George Terrace',        team:'Kyle + Kierran',                 freq:'Bi-weekly',          hrs:'4 h',                      cat:'a'   },
    { client:'Josh',               addr:'1026 Roslyn Rd',                 team:'Kyle + Kierran',                 freq:'Bi-weekly',          hrs:'2 h',                      cat:'a'   },
    { client:'Jenicas',            addr:'9708 Glenelg Ave',               team:'Kyle + Kierran',                 freq:'Bi-weekly',          hrs:'5 h',                      cat:'a'   },
    { client:'Justin',             addr:'289 King George Terrace',        team:'Booker',                         freq:'Bi-weekly',          hrs:'4 h',                      cat:'b'   },
    { client:'Ian & Judy',         addr:'8431 Lawrence Rd',               team:'Booker',                         freq:'Bi-weekly',          hrs:'6 h',                      cat:'b'   },
    { client:'Andrei',             addr:'5577 Alderley Dr',               team:'Booker',                         freq:'Bi-weekly',          hrs:'4 h',                      cat:'b'   },
    { client:'Laurie',             addr:'495 Norris Rd',                  team:'Booker',                         freq:'Bi-weekly',          hrs:'2 h',                      cat:'b'   },
    { client:'Stephanie',          addr:'1140 Boardman Ln, East Sooke',   team:'Kyle + Kierran',                 freq:'Monthly',            hrs:'5–7 h + travel',           cat:'a'   },
    { client:'Linda',              addr:'235 Anya Lane, Langford',        team:'Kyle + Kierran + Booker',        freq:'Monthly',            hrs:'6 h (2-man)',              cat:'all' },
    { client:'Fil',                addr:'233 Anya Lane, Langford',        team:'Booker → Full Team',             freq:'Monthly',            hrs:'6 h solo + 2 h all-in',    cat:'all' },
  ].forEach(row => {
    sh.appendRow([row.client, row.addr, row.team, row.freq, row.hrs]);
    const r  = sh.getLastRow();
    const bg = bgMap[row.cat] || C.grey;
    sh.getRange(r, 1, 1, 4).setBackground(bg);
    sh.getRange(r, 5).setBackground('#f0f0f0').setHorizontalAlignment('center');
    sh.getRange(r, 1, 1, 5).setFontSize(9).setVerticalAlignment('middle').setWrap(true);
    sh.getRange(r, 1).setFontWeight('bold');
    sh.setRowHeight(r, 26);
    sh.getRange(r, 1, 1, 5).setBorder(
      false, false, true, false, false, false,
      '#dddddd', SpreadsheetApp.BorderStyle.SOLID
    );
  });

  sh.setColumnWidth(1, 155);
  sh.setColumnWidth(2, 210);
  sh.setColumnWidth(3, 185);
  sh.setColumnWidth(4, 130);
  sh.setColumnWidth(5, 125);
}


// ═════════════════════════════════════════════════════════════════════════════
//  VISIT COUNT SHEET
// ═════════════════════════════════════════════════════════════════════════════
function buildVisitSheet(sh) {
  sh.clear();
  sh.setTabColor('#ea4335');

  sh.appendRow(['McCahill Co  —  July 2026 Visit Count', '', '']);
  const title = sh.getRange(1, 1, 1, 3);
  title.merge();
  banner(title, C.navy);
  title.setFontSize(14).setHorizontalAlignment('center');
  sh.setRowHeight(1, 38);

  sh.appendRow(['Client', 'Visits in July', 'Dates']);
  const hdr = sh.getRange(2, 1, 1, 3);
  banner(hdr, C.blue);
  hdr.setFontSize(10).setHorizontalAlignment('center');
  sh.setRowHeight(2, 28);
  sh.setFrozenRows(2);

  [
    ['Trudy',              '5', 'Jul 1, 8, 15, 22, 29'],
    ['Ramsay',             '5', 'Jul 2, 9, 16, 23, 30'],
    ['Stratta (Oak Park)', '4', 'Jul 6, 13, 20, 27'],
    ['Sens',               '4', 'Jul 6, 13, 20, 27'],
    ['Anita',              '4', 'Jul 7, 13, 21, 27'],
    ['Madeline',           '2', 'Jul 7, 21'],
    ['Justin',             '2', 'Jul 7, 21'],
    ['Laurie',             '2', 'Jul 7, 21'],
    ['Carol Ann',          '2 + power wash', 'Jul 10 (service + Power Wash Day 1),  Jul 11 Sat (Power Wash Day 2 ☀️),  Jul 24 (service)'],
    ['Bills',              '2', 'Jul 17, 31'],
    ['Josh',               '2', 'Jul 17, 31'],
    ['Jenicas',            '2', 'Jul 16, 30'],
    ['Ian & Judy',         '2', 'Jul 16, 30'],
    ['Andrei',             '2', 'Jul 17, 31'],
    ['Stephanie',          '1', 'Jul 14'],
    ['Linda & Fil',        '1', 'Jul 28'],
  ].forEach((v, i) => {
    sh.appendRow(v);
    const r  = sh.getLastRow();
    const bg = i % 2 === 0 ? '#f3f3f3' : C.white;
    sh.getRange(r, 1, 1, 3).setBackground(bg).setFontSize(9).setVerticalAlignment('middle').setWrap(true);
    sh.getRange(r, 2).setHorizontalAlignment('center').setFontWeight('bold').setFontSize(12);
    sh.setRowHeight(r, v[2].length > 70 ? 42 : 26);
  });

  sh.setColumnWidth(1, 170);
  sh.setColumnWidth(2, 130);
  sh.setColumnWidth(3, 400);
}
