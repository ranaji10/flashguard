# Bench hardware: the facts, on disk

**Anything in this file must be read, not recalled.** It exists because an
assistant working from memory across a long session stated the wrong USB stick
name after being told the right one, and a wrong disk name in a `rm -rf` is how
you lose a bench run. Paths, disk names and machine names are cheap to check and
expensive to guess.

*Last confirmed by Ranaji: 30 August 2026.*

## USB sticks

| Label | Size | Filesystem | Contains | Mount on Ubuntu | Mount on macOS |
|---|---|---|---|---|---|
| `UBUNTU` | 32 GB | hybrid ISO | Ubuntu live installer, made with balenaEtcher | n/a, it is booted | usually not mounted |
| `BENCH` | 16 GB | exFAT | `bench-kit/`, the working kit | `/run/media/ubuntu/BENCH` | `/Volumes/BENCH` |

Note `/run/media/ubuntu/BENCH`, **not** `/media/$USER/BENCH`. That was the first
thing that failed on the 29 Aug run.

The reliable way to reach the kit on Ubuntu is Files → right-click the folder →
**Open in Terminal**, rather than typing a path.

## Machines

| Name | Role | Notes |
|---|---|---|
| MacBook | authoring | the `~/Repurpose` working folder and the git repo live here |
| Acer laptop | bench | **Dual-boots Ubuntu since 30 Aug 2026** — installed to disk, no longer dependent on the live stick. The `UBUNTU` stick is kept for making other machines bootable. |

## Devices to hand

| Device | State | Notes |
|---|---|---|
| Nothing Phone 1 | usable | captured 30 Aug with debugging on. First complete seven-field record in the matrix. |
| Samsung A5 (SM-A510F) | usable | debugging on for both runs. Exposes no partition and no bootloader property: the abstain case. |
| Old Samsung feature phone | usable | one handset, two USB modes: `0x6845` CDC modem, `0x675a` mass storage |
| Kobo e-reader | usable | mass storage; nothing to enable |
| Fuji X-T30 | **dead** | will not power on after charging the battery, 29 Aug |
| Fuji X30 | usable | captured 29 Aug, classified `ptp_camera`, now a fixture |
| Fuji X-T20 | **will not enumerate** | takes charge (green light) on a known-good cable, still `not_detected` |
| USB flash drives | usable | negative-set devices |

A device that will not power on is a record, not a gap. Log it in
`docs/reference/runs/tester-attrition.md`.

## Rules

- Confirm a mount path by listing it before using it in a command that writes or deletes.
- Never construct a `/Volumes/...` or `/run/media/...` path from memory.
- Both sticks were briefly named `BENCH`. If two volumes with one name are attached,
  macOS silently renames the second `BENCH 1`. Run `ls /Volumes` first, every time.

## What the bench machine no longer proves

Since 30 August the Acer dual-boots Ubuntu from disk. That is more convenient and it moves
the bench conditions FURTHER from an end user's, not closer: root, a near-empty USB baseline,
and a Linux userland that no volunteer will have. See
`docs/reasoning/delivery-platform.md`.
