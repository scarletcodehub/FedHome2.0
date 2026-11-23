const source = document.querySelector('#source');
const metric = document.querySelector('#metric');
const notice = document.querySelector('#notice');
const legend = document.querySelector('#legend');
const chart = document.querySelector('#chart');
const final = document.querySelector('#final');
const rounds = document.querySelector('#rounds');
const colors = ['#2356b6', '#b64030', '#187454'];
const percent = new Intl.NumberFormat('en', { style: 'percent', minimumFractionDigits: 1 });
const mock = Object.fromEntries([
  ['Clean FedAvg', .81, .80, .002],
  ['Poisoned FedAvg', .60, .57, -.001],
  ['Poisoned Median', .78, .77, .002],
].map(([name, accuracy, f1, step]) => [name, Array.from({ length: 25 }, (_, i) => {
  const round = i + 1;
  return { round, accuracy: accuracy + step * round, f1: f1 + step * round };
})]));

let simulation;
let series = [];

function drawChart() {
  const width = chart.clientWidth;
  const height = chart.clientHeight;
  if (!width || !height) return;
  const ratio = window.devicePixelRatio;
  chart.width = width * ratio;
  chart.height = height * ratio;
  const ctx = chart.getContext('2d');
  ctx.scale(ratio, ratio);
  if (!series.length) return;

  const left = 42;
  const top = 12;
  const plotWidth = width - left - 16;
  const plotHeight = height - top - 43;
  const lastRound = series[0][1].at(-1).round;
  const x = round => left + (round - 1) * plotWidth / (lastRound - 1);
  const y = value => top + (1 - value) * plotHeight;
  ctx.font = '12px system-ui';
  ctx.fillStyle = '#46566a';
  ctx.textAlign = 'right';
  for (let tick = 0; tick <= 4; tick++) {
    const value = tick / 4;
    ctx.strokeStyle = '#dce5ef';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(left, y(value));
    ctx.lineTo(left + plotWidth, y(value));
    ctx.stroke();
    ctx.fillText(Math.round(value * 100) + '%', left - 5, y(value) + 4);
  }
  ctx.textAlign = 'center';
  for (const round of [1, 5, 10, 15, 20, lastRound]) {
    ctx.fillText(round, x(round), height - 16);
  }
  ctx.fillText('Training round', left + plotWidth / 2, height - 1);
  series.forEach(([, values], index) => {
    ctx.strokeStyle = colors[index];
    ctx.lineWidth = 2.5;
    ctx.setLineDash([[], [7, 4], [2, 3]][index]);
    ctx.beginPath();
    values.forEach((row, i) => {
      const point = [x(row.round), y(row[metric.value])];
      if (i === 0) ctx.moveTo(...point);
      else ctx.lineTo(...point);
    });
    ctx.stroke();
  });
}

function render() {
  const showingMock = source.value === 'mock';
  series = Object.entries((showingMock ? mock : simulation) ?? {});
  const metricName = metric.selectedOptions[0].text;
  chart.setAttribute('aria-label', metricName + ' by training round. Exact values are in the table below.');
  notice.textContent = showingMock
    ? 'Mock data. These example values are illustrative.'
    : simulation
      ? 'Results from the included simulation, evaluated on held-out synthetic data.'
      : 'Simulation results could not load. Select Hardcoded visual demo to view example data.';
  legend.replaceChildren(...series.map(([name], index) => {
    const item = document.createElement('li');
    const swatch = document.createElement('span');
    swatch.className = 'swatch';
    swatch.style.backgroundColor = colors[index];
    item.append(swatch, name);
    return item;
  }));
  final.replaceChildren();
  for (const [name, values] of series) {
    const row = final.insertRow();
    const last = values.at(-1);
    for (const value of [name, percent.format(last.accuracy), percent.format(last.f1)]) {
      row.insertCell().textContent = value;
    }
  }
  rounds.replaceChildren();
  const header = rounds.createTHead().insertRow();
  for (const label of ['Round', ...series.map(([name]) => name)]) {
    const cell = document.createElement('th');
    cell.scope = 'col';
    cell.textContent = label;
    header.append(cell);
  }
  const body = rounds.createTBody();
  series[0]?.[1].forEach((entry, index) => {
    const row = body.insertRow();
    row.insertCell().textContent = entry.round;
    for (const [, values] of series) row.insertCell().textContent = percent.format(values[index][metric.value]);
  });
  drawChart();
}

source.addEventListener('change', render);
metric.addEventListener('change', render);
new ResizeObserver(drawChart).observe(chart);

fetch('fedhome2_student/results.json')
  .then(response => {
    if (!response.ok) throw new Error('Simulation results unavailable');
    return response.json();
  })
  .then(result => { simulation = result.histories; })
  .catch(() => { simulation = null; })
  .finally(render);
