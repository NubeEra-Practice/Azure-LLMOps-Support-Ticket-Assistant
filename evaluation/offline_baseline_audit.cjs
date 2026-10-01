const fs = require('node:fs');
const input = process.argv[2];
if (!input) throw new Error('CSV path argument required');
const text = fs.readFileSync(input, 'utf8');
const records = [];
let row = [], field = '', quoted = false;
for (let i = 0; i < text.length; i += 1) {
  const ch = text[i];
  if (quoted) {
    if (ch === '"' && text[i + 1] === '"') { field += '"'; i += 1; }
    else if (ch === '"') quoted = false;
    else field += ch;
  } else if (ch === '"') quoted = true;
  else if (ch === ',') { row.push(field); field = ''; }
  else if (ch === '\n' || ch === '\r') {
    row.push(field); field = '';
    if (row.some((v) => v.length > 0)) records.push(row);
    row = [];
    if (ch === '\r' && text[i + 1] === '\n') i += 1;
  } else field += ch;
}
if (field.length || row.length) { row.push(field); records.push(row); }
const headers = records.shift();
const rows = records.map((values) => Object.fromEntries(headers.map((key, index) => [key, values[index] ?? ''])));
const rules = [
  ['Account Access', ['login', 'sign in', 'password', 'account', 'access', 'mfa']],
  ['AI Services', ['model', 'prompt', 'token', 'inference', 'ai service', 'deployment']],
  ['Billing', ['bill', 'invoice', 'charge', 'payment', 'cost', 'quota']],
  ['Cloud Storage', ['blob', 'storage', 'container', 'upload', 'file', 'disk']],
  ['Networking', ['network', 'dns', 'firewall', 'connectivity', 'route', 'endpoint']],
  ['Compute', ['vm', 'compute', 'cpu', 'memory', 'instance', 'container app']],
];
function predict(row) {
  const t = `${row.description} ${row.product}`.toLowerCase();
  const category = rules.find(([, terms]) => terms.some((term) => t.includes(term)))?.[0] ?? 'Compute';
  const critical = ['outage', 'production down', 'data loss', 'security breach'];
  const high = ['blocked', 'unavailable', 'failed', 'cannot access', "can't access"];
  const priority = critical.some((term) => t.includes(term)) ? 'Critical'
    : high.some((term) => t.includes(term)) ? 'High' : 'Medium';
  return { category, priority };
}
function metrics(actual, predicted, labels) {
  const perClass = {};
  const n = actual.length;
  let correct = 0;
  let weightedPrecision = 0, weightedRecall = 0, weightedF1 = 0;
  for (const label of labels) {
    let tp = 0, fp = 0, fn = 0, support = 0;
    for (let i = 0; i < n; i += 1) {
      if (actual[i] === label) { support += 1; if (predicted[i] === label) tp += 1; else fn += 1; }
      else if (predicted[i] === label) fp += 1;
    }
    const precision = tp + fp ? tp / (tp + fp) : 0;
    const recall = tp + fn ? tp / (tp + fn) : 0;
    const f1 = precision + recall ? 2 * precision * recall / (precision + recall) : 0;
    perClass[label] = { precision, recall, f1, support };
    weightedPrecision += n ? precision * support / n : 0;
    weightedRecall += n ? recall * support / n : 0;
    weightedF1 += n ? f1 * support / n : 0;
  }
  correct = actual.reduce((sum, value, index) => sum + Number(value === predicted[index]), 0);
  return { accuracy: n ? correct / n : null, weighted: { precision: weightedPrecision, recall: weightedRecall, f1: weightedF1 }, per_class: perClass, n };
}
const labelsCategory = [...new Set(rows.map((r) => r.category))].sort();
const labelsPriority = [...new Set(rows.map((r) => r.priority))].sort();
const predictions = rows.map(predict);
const result = {
  rows: rows.length,
  category: metrics(rows.map((r) => r.category), predictions.map((r) => r.category), labelsCategory),
  priority: metrics(rows.map((r) => r.priority), predictions.map((r) => r.priority), labelsPriority),
  sample1: {
    category_prediction: predictions[0].category,
    category_actual: rows[0].category,
    priority_prediction: predictions[0].priority,
    priority_actual: rows[0].priority,
  },
};
process.stdout.write(JSON.stringify(result, null, 2));
