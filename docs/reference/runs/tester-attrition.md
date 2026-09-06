# Devices that could not be captured

*Referenced from `docs/reference/bench-hardware.md`. A device that will not power on, will
not enumerate, or cannot be identified is a RECORD, not a gap — the proposal makes a
feasibility claim about recruiting drawers, and the rate at which drawers yield nothing is
part of that claim.*

| Date | Device | What happened | Recorded as |
|---|---|---|---|
| 2026-08-29 | Fujifilm X-T30 | Will not power on after the battery was charged. Never reached USB. | Not captured. Owner-confirmed dead. |
| 2026-08-29 | Fujifilm X-T20 | Visibly taking charge (green light) on a cable proven good on other devices in the same session, and still `not_detected`. | `not_detected`, but see below. |

## The X-T20 is a schema gap, not just an entry

"Powered but invisible" is a different finding from "no cable" and from "dead device", and
the schema has no way to say it. The record says `not_detected`, which reads as *nothing
appeared*, and loses the fact that the device was drawing power on a known-good cable.

This is a live instance of the console's own question — *was there anything true about a
device that this tool gave you no way to say?* — found by the person who wrote the question.

**Proposed field**, not yet added: `not_detected_detail`, one of
`no_power` · `powered_no_enumeration` · `cable_suspect` · `unknown`.

## Why this file exists

Two reasons, and the second is the one that matters for the grant.

1. So an attrition rate can be quoted honestly rather than estimated.
2. So a volunteer who gets nothing from an evening does not conclude they failed. A drawer
   that yields two dead devices and one record is a normal outcome and the protocol should
   say so.
