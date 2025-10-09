#!/usr/bin/env python3
import os
import sys

"""
   Usage:
       Input: kdict1.txt
              dict (in model)
       Output: dict (a new and appended one)

   Tae-Jin Yoon
   McMaster University
   (c) Dec. 2011
"""
def read_file(origdict: str, newdict: str, outdict: str) -> None:
    """
    Merge two dictionary files (one term per line) into a new sorted dictionary without duplicates.
    - origdict: existing dictionary (e.g., ../model/dict)
    - newdict:  new entries to append (e.g., kdict1.txt)
    - outdict:  output path (e.g., ./dict)
    """
    # Read lines from both files, normalize whitespace, skip empties
    def load_lines(path: str) -> list[str]:
        lines: list[str] = []
        with open(path, 'r', encoding='utf-8') as f:
            for raw in f:
                s = ' '.join(raw.strip().split())
                if s:
                    lines.append(s)
        return lines

    orig_lines = load_lines(origdict)
    new_lines = load_lines(newdict)

    # Merge and sort uniquely
    merged = sorted(set(orig_lines) | set(new_lines))

    # Write output (overwrite if exists)
    with open(outdict, 'w', encoding='utf-8') as fout:
        for line in merged:
            fout.write(line + '\n')


if __name__ == "__main__":
    # Check whether there is a new dictionary that needs to be appended to the
    # original dict in the model directory. If present, create a merged dict in this folder.
    out_path = "dict"
    src_model_dict = "../model/dict"
    src_new_dict = "kdict1.txt"

    if not os.path.exists(src_new_dict):
        print("kdict1.txt is needed to process")
        sys.exit(1)

    if not os.path.exists(src_model_dict):
        print(f"Model dictionary not found: {src_model_dict}")
        sys.exit(1)

    # Remove previous output to avoid confusion
    if os.path.exists(out_path):
        os.remove(out_path)

    read_file(origdict=src_model_dict, newdict=src_new_dict, outdict=out_path)
    print(f"Merged dictionary written to: {out_path}")
