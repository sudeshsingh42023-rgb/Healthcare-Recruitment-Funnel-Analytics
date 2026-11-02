"""Recruitment funnel analytics: funnel, channel yield, time-to-fill, trend -> report.html"""
import base64, io
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

STAGES = ["Sourced", "Screened", "Interviewed", "Submitted", "Placed"]
df = pd.read_csv("data/candidates_synthetic.csv", parse_dates=["sourced_date"])
df["stage_idx"] = df["stage_reached"].map({s: i for i, s in enumerate(STAGES)})

# 1. Overall funnel
funnel = pd.Series({s: int((df["stage_idx"] >= i).sum()) for i, s in enumerate(STAGES)})
step_conv = (funnel / funnel.shift(1) * 100).round(1)

# 2. Channel yield
g = df.groupby("source_channel")
channel = pd.DataFrame({
    "sourced": g.size(),
    "submitted": g.apply(lambda x: (x.stage_idx >= 3).sum()),
    "placed": g.apply(lambda x: (x.stage_idx == 4).sum()),
})
channel["sourced_to_placed_%"] = (channel.placed / channel.sourced * 100).round(1)
channel["submit_to_place_%"] = (channel.placed / channel.submitted * 100).round(1)
channel = channel.sort_values("sourced_to_placed_%", ascending=False)

# 3. Time-to-fill & placement rate by specialty
placed = df[df.stage_idx == 4]
spec = df.groupby("specialty").agg(sourced=("candidate_id", "size"),
                                   placed=("stage_idx", lambda s: (s == 4).sum()))
spec["placement_rate_%"] = (spec.placed / spec.sourced * 100).round(1)
spec["median_days_to_fill"] = placed.groupby("specialty")["days_to_fill"].median()
spec = spec.sort_values("median_days_to_fill")

# 4. Monthly trend
monthly = df.set_index("sourced_date").resample("MS").size()

def fig_html(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=110, bbox_inches="tight"); plt.close(fig)
    return f'<img src="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}">'

f1, a = plt.subplots(figsize=(6, 3.4)); a.barh(funnel.index[::-1], funnel.values[::-1], color="#2a6f97")
for y, v in enumerate(funnel.values[::-1]): a.text(v + 8, y, str(v), va="center")
a.set_title("Recruitment funnel")
f2, a = plt.subplots(figsize=(6, 3.4)); a.bar(channel.index, channel["sourced_to_placed_%"], color="#52b788")
a.set_ylabel("Sourced → placed (%)"); a.set_title("Channel yield"); plt.xticks(rotation=20)
f3, a = plt.subplots(figsize=(6, 3.4)); a.barh(spec.index, spec.median_days_to_fill, color="#e76f51")
a.set_xlabel("Median days to fill"); a.set_title("Time-to-fill by specialty")
f4, a = plt.subplots(figsize=(6, 3.4)); a.plot(monthly.index, monthly.values, marker="o", color="#6d597a")
a.set_title("Candidates sourced per month"); plt.xticks(rotation=20)

best, worst = channel.index[0], channel.index[-1]
fast, slow = spec.index[0], spec.index[-1]
insights = [
    f"{best} gives the best sourced-to-placed yield ({channel.loc[best,'sourced_to_placed_%']}%), "
    f"while {worst} gives the lowest ({channel.loc[worst,'sourced_to_placed_%']}%).",
    f"Overall sourced-to-placed conversion is {funnel['Placed']/funnel['Sourced']*100:.1f}% "
    f"({funnel['Placed']} of {funnel['Sourced']}).",
    f"{fast} fills fastest ({spec.loc[fast,'median_days_to_fill']:.0f} days median); "
    f"{slow} is slowest ({spec.loc[slow,'median_days_to_fill']:.0f} days).",
]
html = f"""<html><head><meta charset='utf-8'><title>Recruitment Funnel Analytics</title>
<style>body{{font-family:Arial;max-width:1100px;margin:30px auto}}td,th{{padding:4px 10px;border:1px solid #ccc}}
table{{border-collapse:collapse}}.g{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}img{{max-width:100%}}</style></head><body>
<h1>Healthcare Recruitment Funnel Analytics</h1><p><i>Synthetic data (1,200 records) for demonstration.</i></p>
<h2>Key insights</h2><ul>{''.join(f'<li>{i}</li>' for i in insights)}</ul>
<div class='g'>{fig_html(f1)}{fig_html(f2)}{fig_html(f3)}{fig_html(f4)}</div>
<h2>Funnel step conversion (%)</h2>{step_conv.to_frame('step_conv_%').to_html()}
<h2>Channel performance</h2>{channel.to_html()}
<h2>Specialty performance</h2>{spec.to_html()}</body></html>"""
open("report.html", "w").write(html)
print("\n".join(insights)); print(channel); print(spec)
