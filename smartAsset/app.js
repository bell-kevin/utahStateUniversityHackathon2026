const assetForm = document.getElementById('asset-form');
const scanResult = document.getElementById('scan-result');
const resultTemplate = document.getElementById('result-template');
const assetTableBody = document.getElementById('asset-table-body');

const riskProfiles = {
  'Dry Indoor': { corrosionWeight: 0.2, wearWeight: 0.6 },
  'Outdoor - Mild': { corrosionWeight: 0.45, wearWeight: 0.65 },
  'Outdoor - Marine': { corrosionWeight: 0.95, wearWeight: 0.7 },
  'Chemical Exposure': { corrosionWeight: 0.8, wearWeight: 0.75 },
  'High Humidity': { corrosionWeight: 0.7, wearWeight: 0.65 },
};

const conditionBands = [
  { threshold: 80, label: 'Severe Wear + Corrosion' },
  { threshold: 60, label: 'Moderate Corrosion Detected' },
  { threshold: 40, label: 'Early Wear Pattern' },
  { threshold: 0, label: 'Nominal Condition' },
];

function clamp(number, min, max) {
  return Math.min(max, Math.max(min, number));
}

function calculateRisk({ environment, serviceHours }) {
  const profile = riskProfiles[environment];
  const ageComponent = clamp(serviceHours / 1200, 0, 1);
  const wearSignal = profile.wearWeight * ageComponent;
  const corrosionSignal = profile.corrosionWeight * (0.4 + Math.random() * 0.6);
  const score = clamp(Math.round((wearSignal + corrosionSignal) * 55), 1, 99);
  const probability = clamp(Math.round(score * 0.95), 1, 99);

  return { score, probability };
}

function classifyCondition(score) {
  return conditionBands.find((band) => score >= band.threshold).label;
}

function determinePriority(score) {
  if (score >= 70) return 'High';
  if (score >= 45) return 'Medium';
  return 'Low';
}

function recommendation(priority, assetName) {
  if (priority === 'High') {
    return `Schedule urgent inspection for ${assetName}, trigger a maintenance work order, and set daily AI vision monitoring.`;
  }
  if (priority === 'Medium') {
    return `Plan preventative maintenance for ${assetName} within 14 days and increase visual scans to every shift.`;
  }
  return `${assetName} is stable. Continue baseline monitoring and re-scan next maintenance cycle.`;
}

function renderResult(data) {
  scanResult.querySelector('.empty')?.remove();
  scanResult.querySelector('.result-grid')?.parentElement?.remove();

  const fragment = resultTemplate.content.cloneNode(true);
  const fields = fragment.querySelectorAll('[data-field]');
  fields.forEach((field) => {
    field.textContent = data[field.dataset.field];
  });
  scanResult.appendChild(fragment);
}

function appendRow(data) {
  const row = document.createElement('tr');
  row.innerHTML = `
    <td>${data.name}</td>
    <td>${data.category}</td>
    <td>${data.condition}</td>
    <td>${data.riskScore}</td>
    <td><span class="badge ${data.priority.toLowerCase()}">${data.priority}</span></td>
    <td>${data.recommendation}</td>
  `;
  assetTableBody.prepend(row);
}

assetForm.addEventListener('submit', (event) => {
  event.preventDefault();

  const formData = new FormData(assetForm);
  const payload = {
    name: formData.get('name').trim(),
    category: formData.get('category'),
    environment: formData.get('environment'),
    serviceHours: Number(formData.get('serviceHours')),
  };

  const risk = calculateRisk(payload);
  const priority = determinePriority(risk.score);
  const output = {
    ...payload,
    condition: classifyCondition(risk.score),
    riskScore: String(risk.score),
    failureProbability: `${risk.probability}%`,
    priority,
    recommendation: recommendation(priority, payload.name),
  };

  renderResult(output);
  appendRow(output);
  assetForm.reset();
});
