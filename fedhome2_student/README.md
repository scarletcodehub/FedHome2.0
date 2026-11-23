# FedHome 2.0 — Student Demonstration

A self-contained proof of concept. Five *synthetic* smart homes train a simple logistic-regression classifier. Home 5 is malicious during model aggregation. The simulation compares:

- Clean FedAvg (all clients honest)
- Poisoned FedAvg (one malicious client)
- Poisoned coordinate-wise median (one malicious client)

The dashboard can show **real outputs from this simulation** or **clearly labeled hardcoded example numbers**. It is **not a reproduction of FedHome's reported accuracy**, does not implement real IoT MITM detection, and uses no real network traffic.

## Windows PowerShell / VS Code

```powershell
cd fedhome2_student
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python simulation.py
streamlit run dashboard.py
```

If PowerShell blocks activation, call `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and then `.\.venv\Scripts\python.exe simulation.py` and `.\.venv\Scripts\python.exe -m streamlit run dashboard.py` instead.

## Ubuntu / WSL

```bash
cd fedhome2_student
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python simulation.py
streamlit run dashboard.py
```

## What to say during the demo

1. Five homes have different synthetic traffic patterns, illustrating non-IID data.
2. In the clean case, the five models are combined using FedAvg.
3. When Home 5 poisons its update, FedAvg can be strongly influenced.
4. Median aggregation is less affected by an extreme outlier.
5. Compare held-out accuracy and F1 scores; the defense's effectiveness is **only demonstrated in this toy simulation**.

## Research caveats

- Coordinate median is an illustrative robust-aggregation baseline, not a complete trust verification algorithm.
- The main FedHome paper uses RF and XGBoost; this classroom demo uses a single compatible logistic regression model so model-parameter aggregation is well defined.
- Synthetic labels are not substitutes for realistic attacks. To validate this proposal, use real network traces, mixed attack types, more clients, diverse attacks, and repeat trials.
