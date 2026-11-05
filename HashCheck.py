#!/usr/bin/env python3
"""hashcheck: calculate a file's hash and compare it with an expected value.

Usage:
    python hashcheck.py file.zip
    python hashcheck.py file.zip 2cf24dba5fb0a30e26e8...
    python hashcheck.py file.zip --algo md5
    python hashcheck.py            (asks the questions one by one)

Exit code: 0 = match or just calculated, 1 = mismatch, 2 = error.
"""
import argparse
import hashlib
import sys

ALGORITHMS = ("md5", "sha1", "sha256", "sha512")
LENGTH_TO_ALGO = {32: "md5", 40: "sha1", 64: "sha256", 128: "sha512"}
CHUNK_SIZE = 1024 * 1024


def file_hash(path, algo="sha256"):
    """Return the hex digest of a file, reading it in chunks."""
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            h.update(chunk)
    return h.hexdigest()


def normalize(value):
    """Remove spaces and line breaks, make lowercase."""
    return "".join(value.split()).lower()


def guess_algo(expected):
    """Guess the algorithm from the length of the expected hash."""
    return LENGTH_TO_ALGO.get(len(expected))


def clean_path(text):
    """Remove quotes that appear when a path is pasted or dragged."""
    return text.strip().strip('"').strip("'")


def run(path, expected=None, algo=None):
    """Return (exit_code, list_of_lines_to_print)."""
    lines = []
    expected = normalize(expected) if expected else None

    if algo is None:
        algo = guess_algo(expected) if expected else "sha256"
        if algo is None:
            return 2, [
                "Error: the expected hash has an unusual length "
                f"({len(expected)} characters). Use --algo to choose the algorithm."
            ]

    try:
        digest = file_hash(path, algo)
    except FileNotFoundError:
        return 2, [f"Error: file not found: {path}"]
    except IsADirectoryError:
        return 2, [f"Error: this is a folder, not a file: {path}"]
    except PermissionError:
        return 2, [f"Error: no permission to read: {path}"]
    except OSError as e:
        return 2, [f"Error: could not read the file: {e}"]

    lines.append(f"Algorithm: {algo}")
    lines.append(f"Hash: {digest}")
    if expected is None:
        return 0, lines
    if digest == expected:
        lines.append("Result: MATCH. The file is the same as expected.")
        return 0, lines
    lines.append("Result: MISMATCH. The file is different from what was expected.")
    lines.append(f"Expected: {expected}")
    return 1, lines


def main(argv=None):
    parser = argparse.ArgumentParser(description="Calculate and check file hashes.")
    parser.add_argument("file", nargs="?", help="path to the file")
    parser.add_argument("expected", nargs="?", help="expected hash to compare with")
    parser.add_argument("--algo", choices=ALGORITHMS, help="hash algorithm")
    args = parser.parse_args(argv)

    path, expected = args.file, args.expected
    if path is None:
        path = clean_path(input("Path to the file: "))
        expected = input("Expected hash (press Enter to skip): ").strip() or None

    code, lines = run(clean_path(path), expected, args.algo)
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
