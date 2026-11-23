"""Simple classroom Streamlit dashboard (either genuine simulation output or mock demo)."""
from pathlib import Path
import json
import pandas as pd
import streamlit as st

st.set_page_config(page_title='FedHome 2.0 Demo', page_icon='🏠', layout='wide')
st.title('🏠 FedHome 2.0 — Student Demo')
st.caption('Proof of concept: five simulated homes, one malicious participant, and trust-aware aggregation.')

mode = st.sidebar.radio('Data source', ['Simulation results', 'Hardcoded visual demo'])
results_path = Path(__file__).with_name('results.json')
if mode == 'Simulation results':
    if not results_path.exists():
        st.warning('Run `python simulation.py` first to generate results.json.')
        st.stop()
    result = json.loads(results_path.read_text(encoding='utf-8'))
    histories = result['histories']
else:
    # These fabricated values are visibly identified as mock/demo-only values.
    histories = {
        'Clean FedAvg': [{'round': r, 'accuracy': .81 + .002*r, 'f1': .80 + .002*r} for r in range(1, 26)],
        'Poisoned FedAvg': [{'round': r, 'accuracy': .60 - .001*r, 'f1': .57 - .001*r} for r in range(1, 26)],
        'Poisoned Median': [{'round': r, 'accuracy': .78 + .002*r, 'f1': .77 + .002*r} for r in range(1, 26)],
    }
    st.info('MOCK DATA — These are illustrative values, not measured experimental results.')

st.subheader('Connected smart homes')
cols = st.columns(5)
for i, col in enumerate(cols, start=1):
    with col:
        st.metric(f'🏠 Home {i}', '⚠️ Simulated attacker' if i == 5 else '✅ Normal')

st.subheader('Federated learning comparison')
latest = {name: rows[-1] for name, rows in histories.items()}
cols = st.columns(3)
for (name, val), col in zip(latest.items(), cols):
    with col:
        st.metric(name, f"{val['accuracy']:.1%}", help='Accuracy on held-out synthetic test samples')

records = []
for name, rows in histories.items():
    for row in rows:
        records.append({'Round': row['round'], 'Method': name,
                        'Accuracy': row['accuracy'], 'F1 score': row['f1']})
frame = pd.DataFrame(records)
metric = st.selectbox('Metric', ['Accuracy', 'F1 score'])
st.line_chart(frame.pivot(index='Round', columns='Method', values=metric))

st.subheader('Final comparison')
st.dataframe(pd.DataFrame([
    {'Method': name, 'Accuracy': f"{row['accuracy']:.1%}", 'F1': f"{row['f1']:.1%}"}
    for name, row in latest.items()
]), hide_index=True, use_container_width=True)
st.caption('For education only. This is not a deployed security product and does not detect live traffic.')
