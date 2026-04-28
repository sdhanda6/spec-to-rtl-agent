from concurrent.futures import ProcessPoolExecutor
import json
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
os.environ.setdefault("MPLBACKEND", "Agg")
import subprocess
import shutil
from pathlib import Path
import matplotlib.pyplot as plt
import yaml

SPEC_DIR = Path("examples/specs")
REPORT_DIR = Path("build/reports")
BUILD_DIR = Path("build")
QOR_HTML_REPORT = Path("qor_report.html")
MISSING_QOR_VALUE = 1e9

# QoR fields to extract
QOR_FIELDS = [
    ("wns_ns", "WNS(ns)"),
    ("tns_ns", "TNS(ns)"),
    ("logical_area_um2", "LogicalArea(um2)"),
    ("physical_area_um2", "PhysicalArea(um2)"),
    ("power_mw", "Power(mW)"),
    ("congestion_overflow", "Congestion"),
]

# Possible YAML paths (robust parsing)
QOR_FIELD_PATHS = {
    "wns_ns": [
        ("qor_optimization","final_selected_metrics","wns_ns"),
        ("qor_summary","timing_wns_ns"),
        ("qor_summary","wns_ns"),
    ],
    "tns_ns": [
        ("qor_optimization","final_selected_metrics","tns_ns"),
        ("qor_summary","timing_tns_ns"),
        ("qor_summary","tns_ns"),
    ],
    "logical_area_um2": [
        ("qor_optimization","final_selected_metrics","logical_area_um2"),
        ("qor_summary","logical_area_um2"),
    ],
    "physical_area_um2": [
        ("qor_optimization","final_selected_metrics","physical_area_um2"),
        ("qor_summary","physical_area_um2"),
    ],
    "power_mw": [
        ("qor_optimization","final_selected_metrics","power_mw"),
        ("qor_summary","power_mw"),
    ],
    "congestion_overflow": [
        ("qor_optimization","final_selected_metrics","congestion_overflow"),
        ("qor_summary","congestion_overflow"),
    ],
}

def get_nested(data, path):
    for key in path:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return "-"
    return data

def get_qor_metric(data, key):
    paths = QOR_FIELD_PATHS.get(key, [])
    for path in paths:
        value = get_nested(data, path)
        if value != "-":
            return value
    return "-"

def format_qor_value(value, key=None):
    if value is None or value == "-":
        return "N/A"
    def format_numeric(number):
        if key == "power_mw" and number != 0.0:
            if abs(number) < 1e-6:
                return f"{number:.9g}"
            if f"{number:.4f}" == "0.0000":
                return f"{number:.9f}".rstrip("0").rstrip(".")
        return f"{number:.4f}"
    if isinstance(value, str):
        stripped = value.strip()
        if stripped in {"", "-", "None", "null", "N/A"}:
            return "N/A"
        try:
            return format_numeric(float(stripped))
        except ValueError:
            return stripped
    if isinstance(value, float):
        return format_numeric(value)
    if isinstance(value, int):
        return str(value)
    return str(value)

def normalize_qor_number(value, default):
    if value is None or value == "-":
        return default
    if isinstance(value, str):
        stripped = value.strip()
        if stripped in {"", "-", "None", "null", "N/A"}:
            return default
        try:
            return float(stripped)
        except ValueError:
            return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def is_missing_qor_number(value):
    return normalize_qor_number(value, None) is None

def get_area_value(raw_values):
    area_value = raw_values.get("logical_area_um2")
    if is_missing_qor_number(area_value):
        area_value = raw_values.get("physical_area_um2")
    return area_value

def build_design_metric(name, raw_values):
    area_value = get_area_value(raw_values)

    return {
        "name": name,
        "wns": normalize_qor_number(raw_values.get("wns_ns"), 0.0),
        "area": normalize_qor_number(area_value, MISSING_QOR_VALUE),
        "power": normalize_qor_number(raw_values.get("power_mw"), MISSING_QOR_VALUE),
    }

def compute_pareto(designs):
    pareto = []
    for design in designs:
        dominated = False
        for other in designs:
            if other is design:
                continue
            if (
                other["area"] < design["area"]
                and other["power"] < design["power"]
                and other["wns"] >= design["wns"]
            ):
                dominated = True
                break
        if not dominated:
            pareto.append(design)
    return pareto

def explain_design(d):
    if d["wns"] < 0:
        return "Timing violation"
    if d["area"] < 200:
        return "Area optimized"
    if d["area"] > 1000:
        return "Area heavy"
    if d["power"] < 0.05:
        return "Low power"
    return "High switching activity"

def format_analysis_number(value):
    if value != 0.0 and abs(value) < 1e-6:
        return f"{value:.9g}"
    if value != 0.0 and f"{value:.4f}" == "0.0000":
        return f"{value:.9f}".rstrip("0").rstrip(".")
    return f"{value:.4f}"

def print_pareto_designs(designs):
    print("\n\n========== PARETO OPTIMAL DESIGNS ==========")
    print(f"{'Design':25} | {'WNS(ns)':15} | {'Area(um2)':15} | {'Power(mW)':15}")
    print("-"*80)

    for design in compute_pareto(designs):
        print(
            f"{design['name']:25} | "
            f"{format_analysis_number(design['wns']):15} | "
            f"{format_analysis_number(design['area']):15} | "
            f"{format_analysis_number(design['power']):15}"
        )

    print("="*80)

def print_design_insights(designs):
    print("\n\n========== DESIGN INSIGHTS ==========")
    for design in designs:
        print(f"{design['name']:25} \u2192 {explain_design(design)}")

def write_qor_visualization(designs, output_path=QOR_HTML_REPORT):
    labels = [design["name"] for design in designs]
    areas = [design["area"] for design in designs]
    powers = [design["power"] for design in designs]

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>QoR Report</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 32px;
      color: #202124;
    }}
    h1 {{
      font-size: 24px;
      margin-bottom: 24px;
    }}
    .chart-wrap {{
      max-width: 1100px;
      height: 520px;
    }}
  </style>
</head>
<body>
  <h1>QoR Area and Power</h1>
  <div class="chart-wrap">
    <canvas id="qorChart"></canvas>
  </div>
  <script>
    const labels = {json.dumps(labels)};
    const areaData = {json.dumps(areas)};
    const powerData = {json.dumps(powers)};

    new Chart(document.getElementById("qorChart"), {{
      type: "bar",
      data: {{
        labels,
        datasets: [
          {{
            label: "Area (um2)",
            data: areaData,
            backgroundColor: "rgba(37, 99, 235, 0.65)",
            borderColor: "rgb(37, 99, 235)",
            borderWidth: 1,
            yAxisID: "yArea"
          }},
          {{
            label: "Power (mW)",
            data: powerData,
            backgroundColor: "rgba(234, 88, 12, 0.65)",
            borderColor: "rgb(234, 88, 12)",
            borderWidth: 1,
            yAxisID: "yPower"
          }}
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        interaction: {{
          mode: "index",
          intersect: false
        }},
        scales: {{
          x: {{
            title: {{
              display: true,
              text: "Design"
            }}
          }},
          yArea: {{
            beginAtZero: true,
            position: "left",
            title: {{
              display: true,
              text: "Area (um2)"
            }}
          }},
          yPower: {{
            beginAtZero: true,
            position: "right",
            grid: {{
              drawOnChartArea: false
            }},
            title: {{
              display: true,
              text: "Power (mW)"
            }}
          }}
        }}
      }}
    }});
  </script>
</body>
</html>
"""
    output_path.write_text(html, encoding="utf-8")
    print("QoR visualization saved as qor_report.html")

def add_plot_data(name, raw_values, names, areas, powers, wns_values):
    area_value = get_area_value(raw_values)
    power_value = raw_values.get("power_mw")
    wns_value = raw_values.get("wns_ns")

    if (
        is_missing_qor_number(area_value)
        or is_missing_qor_number(power_value)
        or is_missing_qor_number(wns_value)
    ):
        return

    names.append(name)
    areas.append(normalize_qor_number(area_value, 0.0))
    powers.append(normalize_qor_number(power_value, 0.0))
    wns_values.append(normalize_qor_number(wns_value, 0.0))

def write_ppt_ready_graphs(names, areas, powers, wns_values):
    os.makedirs('build/plots', exist_ok=True)

    plt.figure(figsize=(10,6))
    plt.bar(names, areas)
    plt.xticks(rotation=45, ha='right')
    plt.title('Area Comparison')
    plt.ylabel('Area (um2)')
    plt.tight_layout()
    plt.savefig('build/plots/area.png', dpi=300)
    plt.close()

    plt.figure(figsize=(10,6))
    plt.bar(names, powers, color='orange')
    plt.xticks(rotation=45, ha='right')
    plt.title('Power Comparison')
    plt.ylabel('Power (mW)')
    plt.tight_layout()
    plt.savefig('build/plots/power.png', dpi=300)
    plt.close()

    plt.figure(figsize=(8,6))
    plt.scatter(areas, powers)

    for i, name in enumerate(names):
        plt.annotate(name, (areas[i], powers[i]), fontsize=8)

    plt.xlabel('Area (um2)')
    plt.ylabel('Power (mW)')
    plt.title('Pareto Tradeoff: Area vs Power')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('build/plots/pareto.png', dpi=300)
    plt.close()

    print('\nPPT-ready graphs saved in: build/plots/')
    print(' - area.png')
    print(' - power.png')
    print(' - pareto.png')

def clean_before_batch():
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    flow_dir = Path.home() / "OpenROAD-flow-scripts" / "flow"
    for label in ["results", "logs"]:
        target = flow_dir / label
        if target.exists():
            for child in target.iterdir():
                try:
                    if child.is_dir() and not child.is_symlink():
                        shutil.rmtree(child)
                    else:
                        child.unlink()
                except OSError:
                    pass


def run_spec(spec):
    cmd = [
        "python3",
        "run_pipeline.py",
        "--spec", str(spec),
        "--mode", "full",
        "--overwrite",
        "--optimize-synth",
        "--optimize-qor",
        "--verify-post-synth",
        "--run-signoff"
    ]

    env = os.environ.copy()
    env["SPEC2RTL_SKIP_AUTO_CLEAN"] = "1"
    result = subprocess.run(cmd, env=env)
    return (spec.name, "PASS" if result.returncode == 0 else "FAIL")


def main():
    # ================= RUN PIPELINE =================
    clean_before_batch()
    spec_files = sorted([*SPEC_DIR.glob("*.yaml"), *SPEC_DIR.glob("*.txt")])

    print(f"\nFound {len(spec_files)} spec files.\n")

    for spec in spec_files:
        print("\n==============================")
        print(f"Running: {spec.name}")
        print("==============================")

    # max_workers should be min(4, os.cpu_count()) to avoid oversubscribing smaller hosts.
    max_workers = min(4, os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(run_spec, spec_files))

    # ================= SUMMARY =================
    print("\n\n========== FINAL SUMMARY ==========")
    print(f"{'Spec File':25} | Status")
    print("-"*40)

    for name, status in results:
        print(f"{name:25} | {status}")

    print("="*40)

    # ================= QoR TABLE =================
    print("\n\n========== QoR SUMMARY TABLE ==========")

    headers = [label for _, label in QOR_FIELDS]
    print(f"{'Design':25} | " + " | ".join([f"{h:15}" for h in headers]))
    print("-"*95)

    designs = []
    names = []
    areas = []
    powers = []
    wns_values = []

    for rpt in sorted(REPORT_DIR.glob("*_pipeline_report.yaml")):
        name = rpt.stem.replace("_pipeline_report", "")

        try:
            with open(rpt, "r") as f:
                data = yaml.safe_load(f)
        except:
            data = {}

        raw_values = {}
        values = []
        for key, _ in QOR_FIELDS:
            val = get_qor_metric(data, key)
            raw_values[key] = val
            values.append(format_qor_value(val, key))

        designs.append(build_design_metric(name, raw_values))
        add_plot_data(name, raw_values, names, areas, powers, wns_values)
        print(f"{name:25} | " + " | ".join([f"{v:15}" for v in values]))

    print("="*95)

    print_pareto_designs(designs)
    print_design_insights(designs)
    write_qor_visualization(designs)
    write_ppt_ready_graphs(names, areas, powers, wns_values)


if __name__ == "__main__":
    main()
