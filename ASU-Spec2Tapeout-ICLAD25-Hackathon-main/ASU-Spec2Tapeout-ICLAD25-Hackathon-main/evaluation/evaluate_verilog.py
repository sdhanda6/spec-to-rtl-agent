import subprocess
import argparse
from pathlib import Path

def compile_and_run(verilog_file: Path, problem_number: int, tb_path: Path = None, use_hidden: bool = False):
    script_dir = Path(__file__).resolve().parent

    if tb_path:
        testbench_path = tb_path.resolve()
    else:
        base_dir = "hidden" if use_hidden else "visible"
        testbench_dir = script_dir / base_dir / f"p{problem_number}"
        testbenches = list(testbench_dir.glob("*.v"))

        if not testbenches:
            print(f"Error: No .v testbench found in {testbench_dir}")
            return

        testbench_path = testbenches[0]

    output_exe = Path(f"p{problem_number}.out")
    compile_cmd = [
        "iverilog",
        "-Wall",         # Show all warnings
        "-g2012",        # Use SystemVerilog-2012 features
        "-o", str(output_exe),
        str(verilog_file),
        str(testbench_path)
    ]

    try:
        print(f"Compiling: {' '.join(compile_cmd)}")
        subprocess.run(compile_cmd, check=True)
    except subprocess.CalledProcessError:
        print("Compilation failed.")
        return

    try:
        print("Running simulation...")
        subprocess.run(["vvp", str(output_exe)], check=True)
    except subprocess.CalledProcessError:
        print("Simulation failed.")
    finally:
        if output_exe.exists():
            output_exe.unlink()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile and run a Verilog file with the corresponding testbench.")
    parser.add_argument("--verilog", type=Path, required=True, help="Path to the Verilog source file")
    parser.add_argument("--problem", type=int, required=True, help="Problem number to locate the testbench folder")
    parser.add_argument("--tb", type=Path, required=False, help="Optional path to a specific testbench file")
    parser.add_argument("--hidden", action="store_true", help="Use the hidden testbench directory instead of visible")

    args = parser.parse_args()
    compile_and_run(args.verilog.resolve(), args.problem, args.tb, args.hidden)

