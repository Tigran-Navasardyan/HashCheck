#!/usr/bin/env python3
"""Calculate file hashes and compare them with expected values.

Usage:
    python hashcheck.py file.zip
    python hashcheck.py file.zip EXPECTED_HASH
    python hashcheck.py file.zip --algo md5
    python hashcheck.py

Exit codes:
    0 = Success or hash match
    1 = Hash mismatch
    2 = Error
    130 = Cancelled by user
"""

import argparse
import hashlib
import os
import sys

HASH_LENGTHS = {
    "md5": 32,
    "sha1": 40,
    "sha256": 64,
    "sha512": 128,
}

ALGORITHMS = tuple(HASH_LENGTHS)

LENGTH_TO_ALGO = {length: algo for algo, length in HASH_LENGTHS.items()}

CHUNK_SIZE = 1024 * 1024
HEX_CHARACTERS = "0123456789abcdef"


def file_hash(path, algo="sha256"):
    """Calculate a file hash, reading the file in chunks."""
    h = hashlib.new(algo)

    with open(path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            h.update(chunk)

    return h.hexdigest()


def normalize(value):
    """Remove whitespace and convert to lowercase."""
    return "".join(value.split()).lower()


def guess_algo(expected):
    """Detect the algorithm from the hash length."""
    return LENGTH_TO_ALGO.get(len(expected))


def clean_path(text):
    """Remove surrounding quotes from a pasted file path."""
    text = text.strip()

    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"'):
        text = text[1:-1]

    return text


def validate_hash(expected, algo):
    """Return an error message if the hash is invalid, otherwise None."""
    required_length = HASH_LENGTHS[algo]

    if len(expected) != required_length:
        return (
            f"Error: {algo} hashes must contain "
            f"{required_length} characters. "
            f"Received {len(expected)}."
        )

    if any(char not in HEX_CHARACTERS for char in expected):
        return "Error: the expected hash contains invalid characters."

    return None


def run(path, expected=None, algo=None):
    """Return an exit code and a list of output lines."""
    if not path or not path.strip():
        return 2, ["Error: no file path was provided."]

    expected = normalize(expected) if expected else None

    if algo is not None and algo not in ALGORITHMS:
        return 2, [f"Error: unsupported algorithm: {algo}"]

    if algo is None:
        algo = guess_algo(expected) if expected else "sha256"

        if algo is None:
            return 2, [
                "Error: the expected hash has an unusual length "
                f"({len(expected)} characters). "
                "Use --algo to choose the algorithm."
            ]

    if expected:
        validation_error = validate_hash(expected, algo)

        if validation_error:
            return 2, [validation_error]

    if os.path.isdir(path):
        return 2, [f"Error: this is a folder, not a file: {path}"]

    try:
        digest = file_hash(path, algo)

    except FileNotFoundError:
        return 2, [f"Error: file not found: {path}"]

    except PermissionError:
        return 2, [f"Error: no permission to read: {path}"]

    except ValueError as e:
        return 2, [f"Error: hashing failed: {e}"]

    except OSError as e:
        return 2, [f"Error: could not read the file: {e}"]

    lines = [f"Algorithm: {algo}", f"Hash: {digest}"]

    if expected is None:
        return 0, lines

    if digest == expected:
        lines.append("Result: MATCH. The file is the same as expected.")
        return 0, lines

    lines.append("Result: MISMATCH. The file is different from what was expected.")
    lines.append(f"Expected: {expected}")

    return 1, lines


def main(argv=None):
    """Parse arguments and run HashCheck."""
    parser = argparse.ArgumentParser(
        description="Calculate and check file hashes."
    )
    parser.add_argument("file", nargs="?", help="Path to the file.")
    parser.add_argument("expected", nargs="?", help="Expected hash to compare with.")
    parser.add_argument("--algo", choices=ALGORITHMS, help="Hash algorithm.")

    args = parser.parse_args(argv)

    path = args.file
    expected = args.expected

    try:
        if path is None:
            path = input("Path to the file: ")
            expected = input("Expected hash (press Enter to skip): ")

        code, lines = run(clean_path(path), expected, args.algo)

        for line in lines:
            print(line)

        return code

    except KeyboardInterrupt:
        print("\nCancelled by user.")
        return 130

    except EOFError:
        print("\nError: input was interrupted or unavailable.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
