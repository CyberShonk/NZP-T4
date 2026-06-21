# Security policy

Imported map packages are untrusted data.

## Report privately

Report archive traversal, decompression-bomb, parser memory-safety, arbitrary-code execution, path disclosure, or unsafe file-write issues privately to the repository owner before public disclosure.

Do not include a proprietary map package or stock game file in a report. Provide a minimal independently created reproducer whenever possible.

## Current safety boundary

The v0.1.0 inspector:

- does not execute imported content;
- does not extract archive entries;
- validates archive metadata before hashing entries;
- blocks unsafe paths, symlinks, encrypted entries, duplicate normalized paths, and configured quota violations.

It is an early implementation and has not received an external security audit.
