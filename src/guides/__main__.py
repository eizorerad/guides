"""The terminal menu and the non-interactive reproduction command."""

import argparse
import json
import os
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import requests

from .data import ROOT, SETTINGS, prepare, validate_guides


def render(gene_name, sequences=None):
    if sequences is not None:
        sequences = validate_guides(sequences)
    _, _, gene = prepare(gene_name)
    mode = "dolcetto" if sequences is None else "custom"
    name = f"{gene['gene']}-{mode}"
    output = ROOT / "results" / name
    output.mkdir(parents=True, exist_ok=True)
    request = dict(gene=gene["gene"], sequences=sequences, mode=mode, name=name)
    request_path = output / "request.json"
    request_path.write_text(json.dumps(request, indent=2) + "\n")
    print(f"Building report for {gene['gene']} …", flush=True)
    env = dict(os.environ, GUIDES_REQUEST=str(request_path), QUARTO_PYTHON=sys.executable)
    run = subprocess.run(["quarto", "render", "report.qmd", "--output", f"{name}.html"],
                         cwd=ROOT / "reports", env=env, capture_output=True, text=True)
    (output / "render.log").write_text(run.stdout + run.stderr)
    if run.returncode:
        print(run.stderr, file=sys.stderr)
        run.check_returncode()
    report = ROOT / "reports" / f"{name}.html"
    print(f"\nReport: {report}\nFigure and tables: {output}\n")
    return report


def menu():
    while True:
        print("\nguides · human / GRCh38 / K562 / CRISPRi\n"
              "  1  Gene → guides from Dolcetto Set A\n"
              "  2  Gene + custom guides\n"
              "  0  Exit")
        choice = input("Choose [1]: ").strip() or "1"
        if choice == "0":
            return
        if choice not in {"1", "2"}:
            print("Enter 1, 2 or 0.")
            continue
        gene = input("Gene (symbol or Ensembl ID): ").strip()
        sequences = None
        if choice == "2":
            print("Enter spacers: 20 letters A/C/G/T, without PAM, one per line.\n"
                  "Finish with an empty line.")
            sequences = []
            while line := input().strip():
                sequences.append(line)
        try:
            render(gene, sequences)
        except (ValueError, OSError, requests.RequestException, subprocess.CalledProcessError) as error:
            print(f"Could not build report: {error}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        prog="guides",
        description="Map CRISPRi guides onto a human GRCh38 locus with K562 peak and cCRE annotations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  guides                                      Open the terminal menu
  guides help                                 Show this help (also --help or -h)
  guides --gene COTL1                          Report using Dolcetto Set A guides
  guides --gene COTL1 --guides GGTACGCGCCGAGGGCGCAC CGGCGGTGGCGACGGCTACG
  guides --gene COTL1 --guides-file spacers.txt  Read one spacer per line
  guides --gene COTL1 --json                    Return result paths as JSON

Spacers: 20 DNA bases (A/C/G/T), without PAM. All report commands run without
prompts. With --json, progress goes to stderr and stdout contains only JSON.
Exit codes: 0 success, 1 report/input failure, 2 invalid command, 130 interrupted.
Reports for the same gene and mode are replaced on rerun; run one at a time.""")
    parser.add_argument("--gene", help="Exact gene symbol or Ensembl ID")
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--guides", nargs="+", metavar="SPACER", help="Custom spacers, separated by spaces; requires --gene")
    inputs.add_argument("--guides-file", type=Path, metavar="FILE", help="One spacer per line; requires --gene")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--reproduce", action="store_true", help="Render the example specified in config/settings.toml")
    actions.add_argument("--download", action="store_true", help="Download raw inputs for --gene or the example")
    parser.add_argument("--json", action="store_true", help="Print report and results paths as JSON for scripts")
    argv = sys.argv[1:]
    args = parser.parse_args(["--help"] if argv == ["help"] else argv)
    if (args.guides_file or args.guides) and not args.gene:
        parser.error("custom guides require --gene")
    if args.download and (args.guides_file or args.guides or args.json):
        parser.error("--download cannot be combined with custom guides or --json")
    if args.json and not (args.gene or args.reproduce):
        parser.error("--json requires --gene or --reproduce")
    try:
        if args.download:
            prepare(args.gene or SETTINGS["demo_gene"])
        elif args.reproduce or args.gene:
            sequences = args.guides_file.read_text().splitlines() if args.guides_file else args.guides
            with redirect_stdout(sys.stderr if args.json else sys.stdout):
                report = render(args.gene or SETTINGS["demo_gene"], sequences)
            if args.json:
                print(json.dumps(dict(report=str(report), results=str(ROOT / "results" / report.stem))))
        else:
            if not sys.stdin.isatty():
                parser.error("use --gene or --reproduce for non-interactive runs; see guides help")
            menu()
    except (ValueError, OSError, requests.RequestException, subprocess.CalledProcessError) as error:
        parser.exit(1, f"guides: {error}\n")
    except EOFError:
        print("\nGoodbye.")
    except KeyboardInterrupt:
        parser.exit(130, "\nInterrupted.\n")


if __name__ == "__main__":
    main()
