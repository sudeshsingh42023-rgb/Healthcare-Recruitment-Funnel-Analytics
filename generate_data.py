"""Generate a SYNTHETIC healthcare-recruitment dataset (no real candidate data)."""
import numpy as np, pandas as pd

rng = np.random.default_rng(42)
N = 1200

CHANNELS = {"LinkedIn": 0.30, "Job Boards": 0.28, "Social Media": 0.15,
            "Talent Database": 0.15, "Referrals": 0.12}
# Assumed stage-conversion rates per channel (simulation parameters, not real data)
RATES = {  # screened, interviewed, submitted, placed
    "LinkedIn":        (0.55, 0.60, 0.65, 0.45),
    "Job Boards":      (0.45, 0.50, 0.60, 0.40),
    "Social Media":    (0.35, 0.45, 0.55, 0.35),
    "Talent Database": (0.60, 0.62, 0.68, 0.50),
    "Referrals":       (0.75, 0.75, 0.78, 0.62),
}
SPECIALTIES = {  # name: (weight, demand modifier on placement, mean days-to-fill)
    "ICU RN": (0.14, 1.10, 24), "Med-Surg RN": (0.18, 1.15, 18),
    "ER RN": (0.10, 1.00, 22), "OR RN": (0.08, 0.90, 30),
    "Travel Nurse": (0.12, 1.05, 21), "Physical Therapist": (0.09, 0.85, 33),
    "Respiratory Therapist": (0.08, 0.95, 27), "Radiology Tech": (0.08, 0.90, 31),
    "Lab Technologist": (0.07, 0.95, 26), "Pharmacy Tech": (0.06, 1.00, 20),
}
STATES = ["TX", "CA", "FL", "NY", "MA", "NH", "IL", "GA", "WA", "CO"]
STAGES = ["Sourced", "Screened", "Interviewed", "Submitted", "Placed"]

ch = rng.choice(list(CHANNELS), N, p=list(CHANNELS.values()))
sp_names = list(SPECIALTIES)
sp = rng.choice(sp_names, N, p=[SPECIALTIES[s][0] for s in sp_names])
rows = []
for i in range(N):
    r = RATES[ch[i]]
    mod = SPECIALTIES[sp[i]][1]
    stage = 1
    for k, p in enumerate(r):
        p = min(p * (mod if k == 3 else 1.0), 0.95)
        if rng.random() < p:
            stage += 1
        else:
            break
    ttf = None
    if stage == 5:
        ttf = max(5, int(rng.normal(SPECIALTIES[sp[i]][2], 6)))
    rows.append({
        "candidate_id": f"C{i+1:04d}",
        "source_channel": ch[i],
        "specialty": sp[i],
        "state": rng.choice(STATES),
        "sourced_date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=int(rng.integers(0, 270))),
        "stage_reached": STAGES[stage - 1],
        "days_to_fill": ttf,
    })
df = pd.DataFrame(rows)
df.to_csv("data/candidates_synthetic.csv", index=False)
print(f"Wrote {len(df)} synthetic records -> data/candidates_synthetic.csv")
