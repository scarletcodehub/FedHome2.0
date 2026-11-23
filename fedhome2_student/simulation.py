"""FedHome 2.0 classroom demonstration.

Five synthetic smart homes collaboratively train a tiny binary classifier.
Compare unpoisoned FedAvg, poisoned FedAvg, and poisoned coordinate median.
This is a simulation, NOT a reproduction of the FedHome paper's experiments.
"""
from pathlib import Path
import json
import numpy as np

SEED = 42
N_HOMES = 5
ROUNDS = 25
LOCAL_STEPS = 8
LEARNING_RATE = 0.20
OUTPUT = Path(__file__).with_name('results.json')


def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -35, 35)))


def generate_data():
    rng = np.random.default_rng(SEED)
    # Non-identical traffic conditions and attack prevalence across households.
    homes = []
    for i in range(N_HOMES):
        x = rng.normal(size=(280, 4))
        x[:, 0] += (i - 2) * 0.25
        x[:, 2] += (i % 3 - 1) * 0.30
        logit = 1.5*x[:, 0] - 1.0*x[:, 1] + 1.3*x[:, 2] - 0.7*x[:, 3] + (i-2)*0.24
        y = (rng.random(len(x)) < sigmoid(logit)).astype(float)
        homes.append((np.c_[x, np.ones(len(x))], y))
    x = rng.normal(size=(2500, 4))
    logit = 1.5*x[:, 0] - 1.0*x[:, 1] + 1.3*x[:, 2] - 0.7*x[:, 3]
    y = (rng.random(len(x)) < sigmoid(logit)).astype(int)
    return homes, np.c_[x, np.ones(len(x))], y


def train_local(w, x, y):
    out = w.copy()
    for _ in range(LOCAL_STEPS):
        gradient = x.T @ (sigmoid(x @ out) - y) / len(y)
        out -= LEARNING_RATE * gradient
    return out


def metrics(w, x, y):
    prediction = (sigmoid(x @ w) >= .5).astype(int)
    tp = int(((prediction == 1) & (y == 1)).sum())
    fp = int(((prediction == 1) & (y == 0)).sum())
    fn = int(((prediction == 0) & (y == 1)).sum())
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    return {'accuracy': round(float((prediction == y).mean()), 4),
            'precision': round(precision, 4), 'recall': round(recall, 4),
            'f1': round(f1, 4)}


def run():
    homes, test_x, test_y = generate_data()
    histories = {}
    for name, poisoned, aggregator in [
        ('Clean FedAvg', False, 'average'),
        ('Poisoned FedAvg', True, 'average'),
        ('Poisoned Median', True, 'median'),
    ]:
        global_w = np.zeros(test_x.shape[1])
        records = []
        for round_no in range(1, ROUNDS + 1):
            weights = [train_local(global_w, x, y) for x, y in homes]
            if poisoned:
                # Home 5 sends a deliberately harmful model update in every round.
                # Its deviation is large enough to strongly distort standard FedAvg.
                weights[-1] = global_w - 12 * (weights[-1] - global_w) - np.array([8., -8., 8., -8., 0.])
            if aggregator == 'average':
                global_w = np.average(weights, axis=0, weights=[len(y) for _, y in homes])
            else:
                # Element-wise median resists one outlier with five participating homes.
                global_w = np.median(np.stack(weights), axis=0)
            records.append({'round': round_no, **metrics(global_w, test_x, test_y)})
        histories[name] = records

    result = {'metadata': {
        'homes': N_HOMES, 'malicious_home': 'Home 5', 'rounds': ROUNDS,
        'dataset': 'Synthetic binary normal-vs-attack traffic (not a real intrusion dataset)',
        'note': 'Model update poisoning is simulated, and all metrics are from held-out synthetic data.'
    }, 'histories': histories}
    OUTPUT.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print('Saved:', OUTPUT)
    for name, rows in histories.items():
        print(f"{name:20s} accuracy={rows[-1]['accuracy']:.1%} | F1={rows[-1]['f1']:.1%}")


if __name__ == '__main__':
    run()
