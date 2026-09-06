# The v0.1 safe case

**Decision: a defensible `safe` recipe cannot exist in format v0.1.**

The five real OpenAndroidInstaller translations are evidence of the boundary, not a
safe corpus case. Four omit irreversible bootloader-unlock steps and one has an
unidentified recovery asset. The v0.1 shape has no field for prerequisite state,
source-workflow completeness, temporary boot semantics, conditional eligibility, or
asset identity beyond a hand-written label. A careful verifier cannot establish that
an incomplete or unidentified procedure is safe. Returning `safe` anyway would turn
lossy translation into a false-safe path.

The existing contract says `safe` requires every operation's preconditions and every
asset match to be established, with no abstention. V0.1 cannot establish those facts
for a recipe translated from a real provisioning workflow because the relevant facts
are not representable. Therefore v0.1 can return `unsafe` for a positive contradiction
or `cannot-verify` for missing coverage, but it has no honest `safe` case.

## Minimum addition for v0.2

Add a required, machine-checkable completeness and prerequisite section. At minimum it
must state:

1. which source workflow or declared procedure boundary the recipe covers;
2. whether all irreversible prerequisites are included and their required starting
   state, including bootloader state; and
3. the identity and match evidence for every asset, including temporary boots.

The verifier may emit `safe` only when that declaration says the covered procedure is
complete, every prerequisite is observed as met by the fingerprint, every asset is
identified and matches, and every modeled operation passes. If the recipe is partial,
omits a prerequisite, or leaves an asset unidentified, the result must be
`cannot-verify` or `unsafe`, never `safe`.

This is the minimum semantic addition, not a proposed final schema. The exact v0.2
field names and operation kinds still need a design decision before the format changes.
No synthetic safe recipe is added: the current real corpus provides no evidence for one.
