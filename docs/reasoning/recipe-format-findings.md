# Recipe format findings

**Scope.** On 6 September 2026, five OpenAndroidInstaller device configs were read
and five recipes were independently authored from their device facts. The upstream
files were not copied or transformed. The recipes are in `data/recipes/`; each keeps
the required `source.authored: independent` provenance.

The selection was intentional: Fairphone 4 (`FP4.yaml`) is A/B; Samsung Galaxy A5
2016 (`a5xelte.yaml`) is single-partition; Fairphone 3 (`FP3.yaml`) requires regular
and critical bootloader unlock; OnePlus Nord (`avicii.yaml`) names several additional
partitions; Sony Xperia 10 (`kirin.yaml`) is awkward because eligibility is checked
in a vendor service menu and unlocking needs a vendor code.

## FP4

**Carried over cleanly:** product code `FP4`, the A/B partition scheme, and the fact
that the flow includes a temporary custom recovery.

**Did not fit:** the recipe invents an asset ID and a `boot` partition write because
the current format needs an asset and `write-image` operation, while the config excerpt
describes a temporary recovery boot rather than naming a recipe asset. The unlock
flow, critical unlock, wipes, reboot, and re-enabling USB debugging were dropped.

**Safety finding:** this is deliberately `unsafe`. A recipe that omits the normal and
critical unlock steps describes a less dangerous procedure than the real one. If a
verifier accepted that understated recipe as `safe`, it would create a false safe.

**Upstream-only facts:** official unlock-code instructions, two distinct unlock
operations, user confirmations, destructive reset, and the temporary-versus-persistent
distinction.

**Format-only demands:** `variant`, asset identity, an operation order, and a
partition name for the recovery action. The config supplies a device code and A/B
flag, but no explicit field called `variant`.

## a5xelte

**Carried over cleanly:** device code `a5xelte`, the four supported device-code
aliases as the reason to treat identity carefully, and `is_ab_device: false` as
`partition_scheme: single`.

**Did not fit:** the recipe invents a recovery asset and a `recovery` write operation.
The config says to use Heimdall to flash recovery but does not provide the asset
identity in the portion represented by this format. The physical button sequence and
manual cable removal were dropped.

**Safety finding:** this is `cannot-verify`, not `safe`. The config does not show an
unlock prerequisite, but the recovery asset is not identified, so the recipe cannot
establish that the write is safe.

**Upstream-only facts:** Samsung-specific download mode, Heimdall, and the manual
button choreography.

**Format-only demands:** `variant`, an asset identity, and a declarative image write.
The config has no equivalent structured asset record.

## FP3

**Carried over cleanly:** product code `FP3`, A/B partitioning, and the existence of
a temporary recovery stage.

**Did not fit:** the recipe cannot represent the prerequisite that the normal and
critical bootloaders must both be unlocked. It therefore records only the recovery
write and puts the unlock fact in `verdict_reason`; that is documentation, not
machine-checkable input. The unlock code website, wipes, reboots, and USB-debugging
reset were dropped. The recovery asset and `boot` partition were invented to satisfy
the v0.1 shape.

**Safety finding:** this is deliberately `unsafe`. The omitted normal and critical
unlock steps are irreversible prerequisites; a safe verdict on this shortened recipe
would be a false safe for the actual procedure.

**Upstream-only facts:** prerequisite state transitions, two unlock scopes, user
confirmation, and a destructive reset between stages.

**Format-only demands:** explicit asset identity, variant, and partition write
semantics.

## avicii

**Carried over cleanly:** device code `avicii` and its `Nord` alias as an identity
concern, A/B partitioning, the `dtbo` and `vbmeta` additional partitions, and the
existence of a temporary recovery stage.

**Did not fit:** the recipe can represent the two named additional partitions, but
it invents their asset identities and treats the temporary recovery boot as a
`write-image` to `boot`. The slot-copy operation, repeated recovery boot, Android 12
requirement, and unlock reset were dropped.

**Safety finding:** this is deliberately `unsafe`. The real config requires bootloader
unlock before the additional-partition and recovery operations. Omitting that step
silently understates risk and must not permit a `safe` result.

**Upstream-only facts:** the `additional_steps` selection mechanism, a stateful
multi-step workflow, slot-to-slot copying, a recovery boot that is not a normal
image write, and the unlock reset.

**Format-only demands:** asset identity and one partition per operation. The config
names partitions but does not identify the image assets that populate them.

## kirin

**Carried over cleanly:** Sony Xperia 10 device code `kirin`, A/B partitioning, and
the recovery-stage intent.

**Did not fit:** the recipe invents the recovery asset and `boot` write. The device
menu eligibility check, vendor unlock code, optional already-unlocked branch, and
privacy-sensitive user instruction were dropped. The format has no place to say that
the unlock precondition is conditional on a hardware-reported eligibility value.

**Safety finding:** this is deliberately `unsafe`. The omitted eligibility and vendor
unlock steps are prerequisites for the real recovery procedure. A `safe` result for
this shortened recipe would be a false safe.

**Upstream-only facts:** vendor-specific eligibility evidence, a conditional branch,
an external unlock-code flow, and a recovery action described as a temporary boot.

**Format-only demands:** variant and asset identity, neither of which appears as a
structured field in this config.

## Finding

All five could be made syntactically valid only by lossy translation. The repeated
pattern is evidence against treating v0.1 as an import format: it can preserve device
identity and A/B versus single partition, but it cannot preserve prerequisites,
temporary boots, slot-copy relationships, conditional branches, user confirmations,
or the distinction between an image write and a temporary recovery boot.

This is a safety finding, not only a format-expressiveness finding. Four recipes omit
irreversible unlock steps present in the source configs, so the shortened recipes look
less dangerous than the real procedures. A verifier that judged one of those recipes
`safe` would create a false safe. The fifth recipe abstains because its asset is not
identified; it must not receive a safe verdict merely because no unlock step appears.

Evidence that would have contradicted this conclusion would be five configs whose
device facts included named assets, target partitions, unlock preconditions, and a
linear declarative operation list with no interactive or stateful steps. These five
configs do not provide that evidence.

## Proposed changes for decision

Do not change the format in this turn. Before implementation, v0.2 must prevent a
recipe from silently understating its own risk. At minimum, it should require an
explicit completeness declaration or source-step coverage, represent unlock and
other irreversible prerequisites as machine-checkable operations, and make omitted
or unidentified assets produce `cannot-verify` rather than disappear. A recipe that
claims to cover only a subset of a source workflow should be unable to receive
`safe` unless that boundary is explicit and independently justified.

The other proposed v0.2 changes remain: operation kinds for temporary boot and slot
copy; conditional/vendor checks; and asset provenance or an explicit
`asset_unidentified` form. The decision should also settle whether `variant` is a
verifier concept or merely a required placeholder, because the upstream configs
mostly expose supported device-code aliases instead.
