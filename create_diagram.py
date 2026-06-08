"""
create_diagram.py — Generates the LangGraph workflow diagram as docs/workflow.png
Run once: python create_diagram.py
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(11, 14))
ax.set_xlim(0, 11)
ax.set_ylim(0, 14)
ax.axis("off")
fig.patch.set_facecolor("#f8f9fa")

C_USER  = "#4A90D9"
C_AGENT = "#5BA85A"
C_COND  = "#E8A838"
C_TOOL  = "#D9534F"
C_MEM   = "#7B68EE"
C_END   = "#555555"
C_ARROW = "#444444"
C_TEXT  = "white"


def box(ax, x, y, w, h, label, sublabel=None, color="#555", fontsize=11):
    rect = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.08",
        linewidth=1.5, edgecolor="white",
        facecolor=color, zorder=3
    )
    ax.add_patch(rect)
    if sublabel:
        ax.text(x, y + 0.2, label, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color=C_TEXT, zorder=4)
        ax.text(x, y - 0.22, sublabel, ha="center", va="center",
                fontsize=8, color=C_TEXT, alpha=0.85, zorder=4)
    else:
        ax.text(x, y, label, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color=C_TEXT, zorder=4)


def straight_arrow(ax, x1, y1, x2, y2, label=None, color=C_ARROW, lw=1.8,
                   label_dx=0.15, label_dy=0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=lw, mutation_scale=18), zorder=2)
    if label:
        mx = (x1 + x2) / 2 + label_dx
        my = (y1 + y2) / 2 + label_dy
        ax.text(mx, my, label, fontsize=8.5, color=color, va="center", zorder=5)


# ── Title ─────────────────────────────────────────────────────────────────────
ax.text(5.5, 13.5, "Job Search Assistant — LangGraph Workflow",
        ha="center", va="center", fontsize=13, fontweight="bold", color="#222")

# ── Main column x-centre ──────────────────────────────────────────────────────
CX = 5.5   # centre x for the main stack
BW = 4.6   # box width for main nodes

# ── Node positions (y values, top → bottom) ───────────────────────────────────
Y_UI    = 12.4
Y_AGENT = 10.8
Y_COND  =  9.1
Y_TOOL  =  7.4
Y_MEM   =  3.2
Y_END   =  1.5

# Tool boxes y and x
Y_TOOLS = 5.6
TX = [2.0, 5.5, 9.0]   # x centres for the three tool boxes
TW = 2.8                # tool box width

# ── Draw main nodes ───────────────────────────────────────────────────────────
box(ax, CX, Y_UI,    BW, 0.85, "User  ➜  Gradio Chat UI",
    sublabel="app.py  |  unique thread_id per session", color=C_USER)

box(ax, CX, Y_AGENT, BW, 0.90, "agent_node  (LLM)",
    sublabel="Reads state + system prompt  →  decides next action", color=C_AGENT)

box(ax, CX, Y_COND,  BW, 0.85, "should_continue()",
    sublabel="Does last message have tool_calls?", color=C_COND)

box(ax, CX, Y_TOOL,  BW, 0.90, "ToolNode  (built-in LangGraph)",
    sublabel="Runs the chosen tool  →  appends result to State", color=C_TOOL)

box(ax, CX, Y_MEM,   BW, 0.90, "MemorySaver  (checkpointing)",
    sublabel="Persists full State per thread_id across turns", color=C_MEM)

box(ax, CX, Y_END,   2.6, 0.70, "END  —  reply to user", color=C_END)

# ── Draw tool boxes ───────────────────────────────────────────────────────────
box(ax, TX[0], Y_TOOLS, TW, 0.80, "web_search_tool",
    sublabel="Tavily API", color=C_TOOL, fontsize=9)
box(ax, TX[1], Y_TOOLS, TW, 0.80, "salary_tool",
    sublabel="Remotive API", color=C_TOOL, fontsize=9)
box(ax, TX[2], Y_TOOLS, TW, 0.80, "summarize_tool",
    sublabel="Custom Python", color=C_TOOL, fontsize=9)

# ── Straight vertical arrows (main spine) ─────────────────────────────────────
straight_arrow(ax, CX, Y_UI    - 0.43, CX, Y_AGENT + 0.46)
straight_arrow(ax, CX, Y_AGENT - 0.46, CX, Y_COND  + 0.43)
straight_arrow(ax, CX, Y_COND  - 0.43, CX, Y_TOOL  + 0.46,
               label="YES — tool call found", label_dx=0.18)

# ── ToolNode → three tool boxes (fan-out via horizontal bus) ─────────────────
y_fan = 6.45   # junction y between ToolNode bottom (6.95) and tool tops (6.00)
# vertical stub from ToolNode down to bus
ax.plot([CX, CX], [Y_TOOL - 0.45, y_fan], color=C_ARROW, lw=1.8, zorder=2)
# horizontal bus line spanning all three tool columns
ax.plot([TX[0], TX[2]], [y_fan, y_fan], color=C_ARROW, lw=1.8, zorder=2)
# arrows from bus down into each tool box top
for tx in TX:
    straight_arrow(ax, tx, y_fan, tx, Y_TOOLS + 0.40)

# ── Tool boxes → MemorySaver (fan-in via horizontal bus) ──────────────────────
y_collect = 4.35   # junction y between tool bottoms (5.20) and MemorySaver top (3.65)
# vertical lines from each tool bottom down to collection bus
for tx in TX:
    ax.plot([tx, tx], [Y_TOOLS - 0.40, y_collect], color=C_ARROW, lw=1.8, zorder=2)
# horizontal collection bus spanning all three tool columns
ax.plot([TX[0], TX[2]], [y_collect, y_collect], color=C_ARROW, lw=1.8, zorder=2)
# single arrow from bus centre into MemorySaver top
straight_arrow(ax, CX, y_collect, CX, Y_MEM + 0.45)

# ── MemorySaver → END ─────────────────────────────────────────────────────────
straight_arrow(ax, CX, Y_MEM - 0.46, CX, Y_END + 0.35)

# ── Loop-back: MemorySaver → agent_node (left side) ──────────────────────────
lx = 0.55   # x of the left rail
# vertical rail
ax.plot([lx, lx], [Y_MEM, Y_AGENT], color=C_AGENT, lw=1.8, zorder=2)
# horizontal stubs
ax.plot([lx, CX - BW / 2], [Y_MEM,   Y_MEM],   color=C_AGENT, lw=1.8, zorder=2)
ax.plot([lx, CX - BW / 2], [Y_AGENT, Y_AGENT],  color=C_AGENT, lw=1.8, zorder=2)
# arrowhead into agent_node
ax.annotate("", xy=(CX - BW / 2, Y_AGENT),
            xytext=(CX - BW / 2 - 0.01, Y_AGENT),
            arrowprops=dict(arrowstyle="-|>", color=C_AGENT,
                            lw=1.8, mutation_scale=18), zorder=2)
ax.text(lx - 0.08, (Y_MEM + Y_AGENT) / 2,
        "loop back\nwith result",
        fontsize=8, color=C_AGENT, ha="right", va="center")

# ── NO path: should_continue → END (right side, clears all boxes) ─────────────
rx = 10.6   # x of the right rail
# horizontal stub out from should_continue
ax.plot([CX + BW / 2, rx], [Y_COND, Y_COND], color=C_ARROW, lw=1.8, zorder=2)
# vertical rail down to END level
ax.plot([rx, rx], [Y_COND, Y_END], color=C_ARROW, lw=1.8, zorder=2)
# horizontal stub into END box
ax.annotate("", xy=(CX + 2.6 / 2, Y_END),
            xytext=(rx, Y_END),
            arrowprops=dict(arrowstyle="-|>", color=C_ARROW,
                            lw=1.8, mutation_scale=18), zorder=2)
ax.text(rx + 0.08, (Y_COND + Y_END) / 2,
        "NO — done",
        fontsize=8.5, color=C_ARROW, ha="left", va="center", rotation=90)

# ── Legend ────────────────────────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(color=C_USER,  label="User / Gradio UI"),
    mpatches.Patch(color=C_AGENT, label="Agent Node (LLM)"),
    mpatches.Patch(color=C_COND,  label="Conditional Routing"),
    mpatches.Patch(color=C_TOOL,  label="ToolNode / Tools"),
    mpatches.Patch(color=C_MEM,   label="MemorySaver"),
]
ax.legend(handles=legend_items, loc="lower left",
          fontsize=8.5, framealpha=0.9, edgecolor="#ccc",
          bbox_to_anchor=(0.0, 0.0))

# ── Save ──────────────────────────────────────────────────────────────────────
os.makedirs("docs", exist_ok=True)
out = os.path.join("docs", "workflow.png")
plt.tight_layout()
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Diagram saved to {out}")
