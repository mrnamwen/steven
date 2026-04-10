#!/usr/bin/env python3
"""
SMT:Imagine Client Reimplementation - Progress Tracker
Generates a self-contained static HTML page showing decomp progress.

Usage:
    python3 tools/progress/generate.py
    python3 tools/progress/generate.py --output /path/to/output.html
    python3 tools/progress/generate.py --yaml /path/to/progress.yaml
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_YAML = SCRIPT_DIR / "progress.yaml"
DEFAULT_OUTPUT = SCRIPT_DIR / "progress.html"


def load_progress(yaml_path: Path) -> dict:
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)


def pct(done: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round((done / total) * 100, 2)


def format_number(n: int) -> str:
    return f"{n:,}"


def compute_totals(data: dict) -> dict:
    """Compute aggregate totals across all subsystems."""
    total_funcs = 0
    done_funcs = 0
    total_classes = 0
    done_classes = 0

    for key, sub in data["subsystems"].items():
        total_funcs += sub.get("total_functions", 0)
        done_funcs += sub.get("done_functions", 0)
        total_classes += sub.get("total_classes", 0)
        done_classes += sub.get("done_classes", 0)

    return {
        "total_functions": total_funcs,
        "done_functions": done_funcs,
        "pct_functions": pct(done_funcs, total_funcs),
        "total_classes": total_classes,
        "done_classes": done_classes,
        "pct_classes": pct(done_classes, total_classes),
    }


def status_label(status: str) -> str:
    labels = {
        "complete": "Done",
        "in_progress": "WIP",
        "not_started": "TODO",
    }
    return labels.get(status, status)


def status_css_class(status: str) -> str:
    return {
        "complete": "status-done",
        "in_progress": "status-wip",
        "not_started": "status-todo",
    }.get(status, "status-todo")


def generate_html(data: dict) -> str:
    totals = compute_totals(data)
    project = data["project"]
    history = data.get("history", [])
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Separate subsystems into categories for display
    # Primary game subsystems (excluding meta categories)
    primary_keys = [
        "gamebryo_engine",
        "network_layer",
        "recv_handlers",
        "send_handlers",
        "task_pipeline",
        "ui_windows",
        "ui_controls",
        "ui_widgets",
        "battle_system",
        "devil_system",
        "zone_map",
        "quest_system",
        "character_system",
        "camera_render",
        "other",
    ]
    meta_keys = ["unnamed_functions", "thunk_functions"]

    # Build subsystem rows
    subsystem_rows = ""
    for key in primary_keys:
        if key not in data["subsystems"]:
            continue
        sub = data["subsystems"][key]
        name = sub["display_name"]
        desc = sub.get("description", "")
        tf = sub.get("total_functions", 0)
        df = sub.get("done_functions", 0)
        tc = sub.get("total_classes", 0)
        dc = sub.get("done_classes", 0)
        pf = pct(df, tf)
        pc = pct(dc, tc)
        status = sub.get("status", "not_started")

        subsystem_rows += f"""
        <tr class="subsystem-row {status_css_class(status)}">
          <td class="sub-name">
            <span class="sub-title">{name}</span>
            <span class="sub-desc">{desc}</span>
          </td>
          <td class="sub-status"><span class="badge {status_css_class(status)}">{status_label(status)}</span></td>
          <td class="sub-classes">
            <div class="progress-cell">
              <div class="progress-bar-bg">
                <div class="progress-bar-fill classes-fill" style="width: {pc}%"></div>
              </div>
              <span class="progress-text">{format_number(dc)} / {format_number(tc)}</span>
              <span class="progress-pct">{pc}%</span>
            </div>
          </td>
          <td class="sub-funcs">
            <div class="progress-cell">
              <div class="progress-bar-bg">
                <div class="progress-bar-fill funcs-fill" style="width: {pf}%"></div>
              </div>
              <span class="progress-text">{format_number(df)} / {format_number(tf)}</span>
              <span class="progress-pct">{pf}%</span>
            </div>
          </td>
        </tr>"""

    # Meta rows (thunks, unnamed)
    meta_rows = ""
    for key in meta_keys:
        if key not in data["subsystems"]:
            continue
        sub = data["subsystems"][key]
        name = sub["display_name"]
        desc = sub.get("description", "")
        tf = sub.get("total_functions", 0)
        df = sub.get("done_functions", 0)
        pf = pct(df, tf)
        notes = sub.get("notes", "")

        meta_rows += f"""
        <tr class="subsystem-row meta-row">
          <td class="sub-name">
            <span class="sub-title">{name}</span>
            <span class="sub-desc">{desc}</span>
          </td>
          <td class="sub-status"><span class="badge status-meta">Meta</span></td>
          <td class="sub-classes">
            <span class="meta-note">{notes[:60]}{'...' if len(notes) > 60 else ''}</span>
          </td>
          <td class="sub-funcs">
            <div class="progress-cell">
              <div class="progress-bar-bg">
                <div class="progress-bar-fill funcs-fill" style="width: {pf}%"></div>
              </div>
              <span class="progress-text">{format_number(df)} / {format_number(tf)}</span>
              <span class="progress-pct">{pf}%</span>
            </div>
          </td>
        </tr>"""

    # History JSON for chart
    history_json = json.dumps(history)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SMT:Imagine Client - Decomp Progress</title>
<style>
* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  background: #0d1117;
  color: #c9d1d9;
  line-height: 1.5;
  min-height: 100vh;
}}

a {{ color: #58a6ff; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

.container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
}}

/* Header */
.header {{
  text-align: center;
  padding: 40px 0 32px;
  border-bottom: 1px solid #21262d;
  margin-bottom: 32px;
}}

.header h1 {{
  font-size: 28px;
  font-weight: 600;
  color: #f0f6fc;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}}

.header h1 .accent {{
  color: #7ee787;
}}

.header .subtitle {{
  font-size: 14px;
  color: #8b949e;
}}

.header .binary-info {{
  margin-top: 12px;
  font-size: 12px;
  color: #484f58;
  font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace;
}}

/* Overall Progress Cards */
.overview {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 32px;
}}

.overview-card {{
  background: #161b22;
  border: 1px solid #21262d;
  border-radius: 8px;
  padding: 24px;
}}

.overview-card .card-label {{
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #8b949e;
  margin-bottom: 12px;
}}

.overview-card .card-value {{
  font-size: 36px;
  font-weight: 700;
  color: #f0f6fc;
  margin-bottom: 4px;
}}

.overview-card .card-value .pct-accent {{
  color: #7ee787;
}}

.overview-card .card-detail {{
  font-size: 13px;
  color: #8b949e;
  margin-bottom: 16px;
}}

.big-progress-bg {{
  width: 100%;
  height: 12px;
  background: #21262d;
  border-radius: 6px;
  overflow: hidden;
}}

.big-progress-fill {{
  height: 100%;
  border-radius: 6px;
  transition: width 0.6s ease;
}}

.big-progress-fill.funcs {{
  background: linear-gradient(90deg, #238636, #7ee787);
}}

.big-progress-fill.classes {{
  background: linear-gradient(90deg, #1f6feb, #58a6ff);
}}

/* Stats row */
.stats-row {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 32px;
}}

.stat-card {{
  background: #161b22;
  border: 1px solid #21262d;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}}

.stat-card .stat-num {{
  font-size: 22px;
  font-weight: 700;
  color: #f0f6fc;
}}

.stat-card .stat-label {{
  font-size: 11px;
  color: #8b949e;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-top: 4px;
}}

/* Section headers */
.section-header {{
  font-size: 18px;
  font-weight: 600;
  color: #f0f6fc;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #21262d;
}}

/* Chart area */
.chart-section {{
  background: #161b22;
  border: 1px solid #21262d;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 32px;
}}

.chart-container {{
  width: 100%;
  height: 200px;
  position: relative;
}}

.chart-container svg {{
  width: 100%;
  height: 100%;
}}

.chart-empty {{
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #484f58;
  font-size: 14px;
}}

/* Subsystem Table */
.subsystem-table {{
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: #161b22;
  border: 1px solid #21262d;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 32px;
}}

.subsystem-table thead th {{
  background: #161b22;
  border-bottom: 1px solid #21262d;
  padding: 12px 16px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #8b949e;
  position: sticky;
  top: 0;
}}

.subsystem-table thead th:first-child {{
  width: 30%;
}}

.subsystem-table thead th:nth-child(2) {{
  width: 8%;
  text-align: center;
}}

.subsystem-table thead th:nth-child(3),
.subsystem-table thead th:nth-child(4) {{
  width: 31%;
}}

.subsystem-row td {{
  padding: 12px 16px;
  border-bottom: 1px solid #21262d;
  vertical-align: middle;
}}

.subsystem-row:last-child td {{
  border-bottom: none;
}}

.sub-name {{
  display: flex;
  flex-direction: column;
  gap: 2px;
}}

.sub-title {{
  font-size: 14px;
  font-weight: 600;
  color: #f0f6fc;
}}

.sub-desc {{
  font-size: 11px;
  color: #484f58;
  font-family: 'SF Mono', 'Fira Code', Consolas, monospace;
}}

.sub-status {{
  text-align: center;
}}

.badge {{
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}}

.badge.status-done {{
  background: rgba(35, 134, 54, 0.2);
  color: #7ee787;
  border: 1px solid rgba(35, 134, 54, 0.4);
}}

.badge.status-wip {{
  background: rgba(187, 128, 9, 0.2);
  color: #e3b341;
  border: 1px solid rgba(187, 128, 9, 0.4);
}}

.badge.status-todo {{
  background: rgba(110, 118, 129, 0.1);
  color: #8b949e;
  border: 1px solid rgba(110, 118, 129, 0.2);
}}

.badge.status-meta {{
  background: rgba(56, 58, 64, 0.3);
  color: #6e7681;
  border: 1px solid rgba(110, 118, 129, 0.15);
}}

.progress-cell {{
  display: flex;
  flex-direction: column;
  gap: 4px;
}}

.progress-bar-bg {{
  width: 100%;
  height: 8px;
  background: #21262d;
  border-radius: 4px;
  overflow: hidden;
}}

.progress-bar-fill {{
  height: 100%;
  border-radius: 4px;
  transition: width 0.4s ease;
  min-width: 0;
}}

.progress-bar-fill.classes-fill {{
  background: #58a6ff;
}}

.progress-bar-fill.funcs-fill {{
  background: #7ee787;
}}

.progress-text {{
  font-size: 12px;
  color: #8b949e;
  font-family: 'SF Mono', 'Fira Code', Consolas, monospace;
}}

.progress-pct {{
  font-size: 12px;
  font-weight: 600;
  color: #c9d1d9;
}}

.meta-row td {{
  opacity: 0.6;
}}

.meta-note {{
  font-size: 11px;
  color: #484f58;
  font-style: italic;
}}

/* Complete row highlight */
.subsystem-row.status-done {{
  background: rgba(35, 134, 54, 0.04);
}}

.subsystem-row.status-wip {{
  background: rgba(187, 128, 9, 0.03);
}}

/* Footer */
.footer {{
  text-align: center;
  padding: 24px 0;
  border-top: 1px solid #21262d;
  font-size: 12px;
  color: #484f58;
}}

/* Responsive */
@media (max-width: 768px) {{
  .overview {{
    grid-template-columns: 1fr;
  }}
  .stats-row {{
    grid-template-columns: repeat(2, 1fr);
  }}
  .subsystem-table {{
    font-size: 13px;
  }}
  .sub-desc {{
    display: none;
  }}
  .header h1 {{
    font-size: 22px;
  }}
}}
</style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <h1><span class="accent">SMT:Imagine</span> Client Reimplementation</h1>
    <div class="subtitle">Decompilation and reimplementation progress tracker</div>
    <div class="binary-info">{project['binary']} | {format_number(project['total_functions'])} functions | {format_number(project['total_classes'])} RTTI classes | {format_number(project['total_vfuncs'])} virtual methods</div>
  </div>

  <!-- Overall Progress -->
  <div class="overview">
    <div class="overview-card">
      <div class="card-label">Functions Reimplemented</div>
      <div class="card-value"><span class="pct-accent">{totals['pct_functions']}%</span></div>
      <div class="card-detail">{format_number(totals['done_functions'])} of {format_number(totals['total_functions'])} functions</div>
      <div class="big-progress-bg">
        <div class="big-progress-fill funcs" style="width: {totals['pct_functions']}%"></div>
      </div>
    </div>
    <div class="overview-card">
      <div class="card-label">Classes Covered</div>
      <div class="card-value"><span class="pct-accent">{totals['pct_classes']}%</span></div>
      <div class="card-detail">{format_number(totals['done_classes'])} of {format_number(totals['total_classes'])} RTTI classes</div>
      <div class="big-progress-bg">
        <div class="big-progress-fill classes" style="width: {totals['pct_classes']}%"></div>
      </div>
    </div>
  </div>

  <!-- Quick Stats -->
  <div class="stats-row">
    <div class="stat-card">
      <div class="stat-num">{format_number(project['total_functions'])}</div>
      <div class="stat-label">Total Functions</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">{format_number(totals['done_functions'])}</div>
      <div class="stat-label">Reimplemented</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">{format_number(project['total_classes'])}</div>
      <div class="stat-label">RTTI Classes</div>
    </div>
    <div class="stat-card">
      <div class="stat-num">{format_number(totals['done_classes'])}</div>
      <div class="stat-label">Classes Done</div>
    </div>
  </div>

  <!-- Timeline Chart -->
  <h2 class="section-header">Progress Over Time</h2>
  <div class="chart-section">
    <div class="chart-container" id="timeline-chart"></div>
  </div>

  <!-- Subsystem Breakdown -->
  <h2 class="section-header">Subsystem Breakdown</h2>
  <table class="subsystem-table">
    <thead>
      <tr>
        <th>Subsystem</th>
        <th>Status</th>
        <th>Classes</th>
        <th>Functions</th>
      </tr>
    </thead>
    <tbody>
      {subsystem_rows}
      {meta_rows}
    </tbody>
  </table>

  <!-- Footer -->
  <div class="footer">
    Generated {now} from progress.yaml | Data from Ghidra analysis of ImagineClientOrig.exe (RU v1.666)
  </div>

</div>

<script>
// Timeline chart rendering
(function() {{
  const history = {history_json};
  const container = document.getElementById('timeline-chart');
  const totalFunctions = {totals['total_functions']};
  const totalClasses = {totals['total_classes']};

  if (history.length < 2) {{
    // Not enough data points for a meaningful line chart; show a single-point summary
    container.innerHTML = `
      <div class="chart-empty">
        Timeline chart will appear after multiple progress updates are recorded in progress.yaml
      </div>
    `;

    if (history.length === 1) {{
      const entry = history[0];
      const funcPct = totalFunctions > 0 ? ((entry.total_functions_done / totalFunctions) * 100).toFixed(1) : '0.0';
      const classPct = totalClasses > 0 ? ((entry.total_classes_done / totalClasses) * 100).toFixed(1) : '0.0';
      container.innerHTML = `
        <svg viewBox="0 0 800 200" preserveAspectRatio="xMidYMid meet">
          <!-- Grid -->
          <line x1="60" y1="20" x2="60" y2="170" stroke="#21262d" stroke-width="1"/>
          <line x1="60" y1="170" x2="760" y2="170" stroke="#21262d" stroke-width="1"/>
          <line x1="60" y1="95" x2="760" y2="95" stroke="#21262d" stroke-width="0.5" stroke-dasharray="4"/>
          <line x1="60" y1="20" x2="760" y2="20" stroke="#21262d" stroke-width="0.5" stroke-dasharray="4"/>

          <!-- Y axis labels -->
          <text x="50" y="174" text-anchor="end" fill="#484f58" font-size="11">0%</text>
          <text x="50" y="99" text-anchor="end" fill="#484f58" font-size="11">50%</text>
          <text x="50" y="24" text-anchor="end" fill="#484f58" font-size="11">100%</text>

          <!-- Date label -->
          <text x="410" y="190" text-anchor="middle" fill="#484f58" font-size="11">${{entry.date}}</text>

          <!-- Data points -->
          <circle cx="410" cy="${{170 - (funcPct / 100 * 150)}}" r="5" fill="#7ee787"/>
          <circle cx="410" cy="${{170 - (classPct / 100 * 150)}}" r="5" fill="#58a6ff"/>

          <!-- Labels -->
          <text x="410" y="${{170 - (funcPct / 100 * 150) - 10}}" text-anchor="middle" fill="#7ee787" font-size="12" font-weight="600">${{funcPct}}% functions</text>
          <text x="410" y="${{170 - (classPct / 100 * 150) - 10}}" text-anchor="middle" fill="#58a6ff" font-size="12" font-weight="600">${{classPct}}% classes</text>

          <!-- Legend -->
          <circle cx="620" cy="30" r="4" fill="#7ee787"/>
          <text x="630" y="34" fill="#8b949e" font-size="11">Functions</text>
          <circle cx="700" cy="30" r="4" fill="#58a6ff"/>
          <text x="710" y="34" fill="#8b949e" font-size="11">Classes</text>
        </svg>
      `;
    }}
    return;
  }}

  // Multi-point line chart
  const padding = {{ top: 20, right: 40, bottom: 30, left: 60 }};
  const w = 800;
  const h = 200;
  const plotW = w - padding.left - padding.right;
  const plotH = h - padding.top - padding.bottom;

  let funcPoints = [];
  let classPoints = [];

  history.forEach((entry, i) => {{
    const x = padding.left + (i / (history.length - 1)) * plotW;
    const funcPct = totalFunctions > 0 ? (entry.total_functions_done / totalFunctions) * 100 : 0;
    const classPct = totalClasses > 0 ? (entry.total_classes_done / totalClasses) * 100 : 0;
    const funcY = padding.top + plotH - (funcPct / 100 * plotH);
    const classY = padding.top + plotH - (classPct / 100 * plotH);
    funcPoints.push({{ x, y: funcY, pct: funcPct.toFixed(1), date: entry.date }});
    classPoints.push({{ x, y: classY, pct: classPct.toFixed(1), date: entry.date }});
  }});

  const funcLine = funcPoints.map((p, i) => (i === 0 ? 'M' : 'L') + p.x + ',' + p.y).join(' ');
  const classLine = classPoints.map((p, i) => (i === 0 ? 'M' : 'L') + p.x + ',' + p.y).join(' ');

  // Grid lines
  let gridLines = '';
  for (let pct = 0; pct <= 100; pct += 25) {{
    const y = padding.top + plotH - (pct / 100 * plotH);
    gridLines += `<line x1="${{padding.left}}" y1="${{y}}" x2="${{w - padding.right}}" y2="${{y}}" stroke="#21262d" stroke-width="0.5" ${{pct > 0 && pct < 100 ? 'stroke-dasharray="4"' : ''}}/>`;
    gridLines += `<text x="${{padding.left - 8}}" y="${{y + 4}}" text-anchor="end" fill="#484f58" font-size="11">${{pct}}%</text>`;
  }}

  // Date labels
  let dateLabels = '';
  const labelStep = Math.max(1, Math.floor(history.length / 6));
  history.forEach((entry, i) => {{
    if (i % labelStep === 0 || i === history.length - 1) {{
      const x = padding.left + (i / (history.length - 1)) * plotW;
      dateLabels += `<text x="${{x}}" y="${{h - 2}}" text-anchor="middle" fill="#484f58" font-size="10">${{entry.date}}</text>`;
    }}
  }});

  // Dots
  const funcDots = funcPoints.map(p => `<circle cx="${{p.x}}" cy="${{p.y}}" r="3" fill="#7ee787"/>`).join('');
  const classDots = classPoints.map(p => `<circle cx="${{p.x}}" cy="${{p.y}}" r="3" fill="#58a6ff"/>`).join('');

  container.innerHTML = `
    <svg viewBox="0 0 ${{w}} ${{h}}" preserveAspectRatio="xMidYMid meet">
      ${{gridLines}}
      <line x1="${{padding.left}}" y1="${{padding.top}}" x2="${{padding.left}}" y2="${{padding.top + plotH}}" stroke="#21262d" stroke-width="1"/>
      <path d="${{funcLine}}" fill="none" stroke="#7ee787" stroke-width="2"/>
      <path d="${{classLine}}" fill="none" stroke="#58a6ff" stroke-width="2"/>
      ${{funcDots}}
      ${{classDots}}
      ${{dateLabels}}
      <!-- Legend -->
      <circle cx="${{w - padding.right - 120}}" cy="${{padding.top + 5}}" r="4" fill="#7ee787"/>
      <text x="${{w - padding.right - 112}}" y="${{padding.top + 9}}" fill="#8b949e" font-size="11">Functions</text>
      <circle cx="${{w - padding.right - 40}}" cy="${{padding.top + 5}}" r="4" fill="#58a6ff"/>
      <text x="${{w - padding.right - 32}}" y="${{padding.top + 9}}" fill="#8b949e" font-size="11">Classes</text>
    </svg>
  `;
}})();
</script>
</body>
</html>"""

    return html


def main():
    parser = argparse.ArgumentParser(
        description="Generate SMT:Imagine decomp progress HTML page"
    )
    parser.add_argument(
        "--yaml",
        type=Path,
        default=DEFAULT_YAML,
        help=f"Path to progress.yaml (default: {DEFAULT_YAML})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output HTML path (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    if not args.yaml.exists():
        print(f"ERROR: {args.yaml} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Loading progress data from {args.yaml}")
    data = load_progress(args.yaml)

    print("Computing totals...")
    totals = compute_totals(data)
    print(f"  Functions: {totals['done_functions']:,} / {totals['total_functions']:,} ({totals['pct_functions']}%)")
    print(f"  Classes:   {totals['done_classes']:,} / {totals['total_classes']:,} ({totals['pct_classes']}%)")

    print(f"Generating HTML...")
    html = generate_html(data)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        f.write(html)

    size_kb = os.path.getsize(args.output) / 1024
    print(f"Written to {args.output} ({size_kb:.1f} KB)")
    print("Done.")


if __name__ == "__main__":
    main()
