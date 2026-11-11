"""The terminal menu and the non-interactive reproduction command."""

import argparse
import json
import os
import subprocess
import sys
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
    parser = argparse.ArgumentParser(description="Map CRISPRi guides onto a GRCh38 locus with K562 peak annotations.")
    parser.add_argument("--gene", help="Exact gene symbol or Ensembl ID")
    parser.add_argument("--guides-file", type=Path, help="One 20-nt DNA spacer per line, without PAM")
    parser.add_argument("--reproduce", action="store_true", help="Render the example specified in config/settings.toml")
    parser.add_argument("--download", action="store_true", help="Download the example's raw inputs only")
    args = parser.parse_args()
    if args.guides_file and not args.gene:
        parser.error("--guides-file requires --gene")
    try:
        if args.download:
            prepare(args.gene or SETTINGS["demo_gene"])
        elif args.reproduce or args.gene:
            sequences = args.guides_file.read_text().splitlines() if args.guides_file else None
            render(args.gene or SETTINGS["demo_gene"], sequences)
        else:
            menu()
    except (ValueError, OSError, requests.RequestException, subprocess.CalledProcessError) as error:
        parser.exit(1, f"guides: {error}\n")
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")


if __name__ == "__main__":
    main()
