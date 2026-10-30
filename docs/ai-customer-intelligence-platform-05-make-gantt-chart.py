"""Builds the Gantt chart PNG from the project schedule CSV."""
import pandas as pd, matplotlib.pyplot as plt, matplotlib.dates as mdates
from datetime import timedelta
df = pd.read_csv("ai-customer-intelligence-platform-05-project-schedule.csv", parse_dates=["start", "end"])
df = df.iloc[::-1].reset_index(drop=True)
colors = {"Done": "#16a34a", "In review": "#ca8a04", "Not started": "#94a3b8"}
fig, ax = plt.subplots(figsize=(15, 11))
for i, r in df.iterrows():
    if r.milestone == "Y":
        ax.scatter(r.end + timedelta(hours=20), i, marker="D", s=110, color="#dc2626" if r.critical == "Y" else "#475569", zorder=3)
    else:
        ax.barh(i, (r.end - r.start).days + 0.85, left=r.start + timedelta(hours=2), height=0.6,
                color=colors[r.status], edgecolor="#dc2626" if r.critical == "Y" else "none", linewidth=2)
ax.set_yticks(range(len(df)))
ax.set_yticklabels([f"{r.id}  {r.task}" for r in df.itertuples()], fontsize=9)
for lbl, r in zip(ax.get_yticklabels(), df.itertuples()):
    if r.milestone == "Y": lbl.set_fontweight("bold")
ax.xaxis.set_major_locator(mdates.DayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%a\n%d %b"))
ax.tick_params(axis="x", labelsize=8)
for d in pd.date_range(df.start.min(), df.end.max() + timedelta(days=1)):
    if d.weekday() >= 5: ax.axvspan(d, d + timedelta(days=1), color="#f1f5f9", zorder=0)
# phase separators
prev = None
for i, r in df.iterrows():
    if prev is not None and r.phase != prev: ax.axhline(i - 0.5, color="#cbd5e1", lw=0.8)
    prev = r.phase
ax.axvline(pd.Timestamp("2026-10-30") + timedelta(hours=23), color="#0284c7", ls="--", lw=1)
ax.text(pd.Timestamp("2026-10-31"), len(df) - 0.3, " today", color="#0284c7", fontsize=8)
ax.set_xlim(df.start.min() - timedelta(days=0.5), df.end.max() + timedelta(days=1.5))
ax.set_title("AI Customer Intelligence Platform — MVP Schedule (29 Oct – 18 Nov 2026)", fontsize=13, loc="left")
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
ax.legend(handles=[Patch(color=colors["Done"], label="Done"), Patch(color=colors["Not started"], label="Not started"),
                   Patch(facecolor="white", edgecolor="#dc2626", lw=2, label="Critical path"),
                   Line2D([], [], marker="D", ls="", color="#dc2626", label="Milestone (critical)"),
                   Line2D([], [], marker="D", ls="", color="#475569", label="Milestone")], loc="lower left", fontsize=8)
ax.grid(axis="x", color="#e2e8f0", lw=0.6); ax.set_axisbelow(True)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig("ai-customer-intelligence-platform-05-gantt-chart.png", dpi=150)
