# pulse_latch Spec-to-Tapeout Collateral

Generated files:
- `config.mk`: OpenROAD-flow-scripts style design config
- `constraint.sdc`: timing constraints
- `filelist.f` and `filelist.tcl`: RTL source lists
- `design_manifest.yaml`: machine-readable artifact summary

Suggested usage:
```powershell
python run_pipeline.py --spec <spec> --mode full --overwrite
```

If OpenROAD-flow-scripts is installed separately, point `OPENROAD_FLOW_ROOT` or `OPENROAD_FLOW_DIR` to it and run:
```powershell
make DESIGN_CONFIG=build/flow/pulse_latch/design/config.mk
```

Platform hint: `sky130hd`
Clock port: `clk`
Clock period: `10 ns`

Visible and hidden-case note: unsupported or ambiguous physical-design requirements should be treated as partial support, not tapeout-ready success.
