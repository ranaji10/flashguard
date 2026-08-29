# Bench hardware: the facts, on disk

**Anything in this file must be read, not recalled.** It exists because an
assistant working from memory across a long session stated the wrong USB stick
name after being told the right one, and a wrong disk name in a `rm -rf` is how
you lose a bench run. Paths, disk names and machine names are cheap to check and
expensive to guess.

*Last confirmed by Ranaji: 29 August 2026.*

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
| Acer laptop | bench | boots the `UBUNTU` stick, runs the kit from the `BENCH` stick |

## Devices to hand

| Device | State | Notes |
|---|---|---|
| Nothing Phone | usable | USB debugging enabled 29 Aug, not yet captured with it on |
| Samsung A5 | usable | debugging was on for the whole 29 Aug run; the classifier was blind to it |
| Kobo e-reader | usable | mass storage; nothing to enable |
| Fuji X-T30 | **dead** | will not power on after charging the battery, 29 Aug |
| Fuji X-T20 | usable | never captured |
| USB flash drives | usable | negative-set devices |

A device that will not power on is a record, not a gap. See
`docs/tester-attrition.md` if that file exists, or note it in the matrix.

## Rules

- Confirm a mount path by listing it before using it in a command that writes or deletes.
- Never construct a `/Volumes/...` or `/run/media/...` path from memory.
- Both sticks were briefly named `BENCH`. If two volumes with one name are attached,
  macOS silently renames the second `BENCH 1`. Run `ls /Volumes` first, every time.
