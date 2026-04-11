# Failed Patch Quarantine

This directory holds patches that failed to install and were rolled back.
Each failed patch is moved here with a timestamp suffix so there is no
ambiguity between the failed version and any future replacement.

## Structure

```
failed/
├── SYS-NNNN_description_<timestamp>/    ← extracted patch directory
│   ├── install.sh
│   ├── apply_patch.py
│   ├── FAILURE_REPORT.md                 ← auto-generated diagnosis
│   └── result.json                       ← PatchBase result manifest
└── archive/
    └── SYS-NNNN_description_<timestamp>.zip
```

## The rule

Patch numbers are **monotonic and burned on failure**, with ONE exception:
a pre-flight failure (where the patch aborts before any destructive work
has been done, with zero side effects) does NOT burn the number. The same
patch number can be reused in that case.

Every other failure mode — mid-install crash, rollback triggered, partial
state left on disk — burns the number permanently. The next attempt uses
`current + 1`, never a retry at the same number.

## History

Created by SYS-0060. The quarantine hook that populates it is deployed
by SYS-0061+.
