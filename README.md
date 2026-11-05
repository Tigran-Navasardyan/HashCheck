# HashCheck

A lightweight command-line file hashing and integrity verification tool written in Python.

HashCheck calculates file hashes and allows users to compare them against expected checksum values.

## Features

- Calculate file hashes.
- Verify file integrity.
- Compare calculated hashes with expected values.
- Automatically detect the hash algorithm based on the expected hash length.
- Interactive mode.
- Efficient processing of large files using chunk-based reading.
- No external dependencies required.

## Supported Algorithms

| Algorithm | Hash Length |
|---|---|
| MD5 | 32 characters |
| SHA-1 | 40 characters |
| SHA-256 | 64 characters |
| SHA-512 | 128 characters |

## Requirements

- Python 3.8 or newer.
- No external packages required.

## Usage

Calculate a SHA-256 hash:

```bash
python hashcheck.py file.zip
```

Compare a file against an expected hash:

```bash
python hashcheck.py file.zip EXPECTED_HASH
```

Select a specific algorithm:

```bash
python hashcheck.py file.zip --algo sha512
```

Supported algorithms:

- md5
- sha1
- sha256
- sha512

Start interactive mode:

```bash
python hashcheck.py
```

## Exit Codes

| Code | Description |
|---|---|
| 0 | Hash calculated successfully or hashes match |
| 1 | Hash mismatch |
| 2 | An error occurred |

## Project Status

HashCheck is currently in its early alpha stage.

This is a hobby project. Feedback, suggestions, bug reports, and community contributions are welcome.

## Author

Tigran Navasardyan

## License

MIT License. See the LICENSE file for details.
