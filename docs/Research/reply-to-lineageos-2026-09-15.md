# What to send back to LineageOS, and why it matters

## The message

> Thanks — following up because you told me to go look, and I did.
>
> You were right. `custom_unlock_cmd` is a template override, not a documentation field. The
> templates render `fastboot oem unlock` in the else branch, so it's only set when the command
> differs. My "103 of 737 devices are missing unlock data" was nonsense — I was counting
> deviations from a default and calling it missing documentation. 737 of 737 declare
> `install_method`, and that plus the optional override fully determines the unlock step. I've
> corrected my own notes.
>
> One thing I found while checking, which you may or may not care about. These 8 set
> `custom_unlock_cmd` while declaring `install_method: amlogic_update`, and
> `recovery_install_amlogic_update.md` doesn't read the field, so the value is never rendered:
>
> `m5`, `m5_tab`, `odroidc4`, `odroidc4_tab`, `radxa0`, `radxa0_tab`, `radxa02`, `radxa02_tab`
>
> All 8 set the same value, and they're 4 boards each with a `_tab` twin, so it looks like one
> copy-paste that propagated. `fastboot_nexus`, `fastboot_nubia` and `fastboot_lenovo` do read
> the field, so 95 of the 103 are live. (`fastboot_oppo` reads it too, but no device sets it.)
>
> Is that worth an issue, a PR, or nothing? Happy with any of the three answers.

That is the whole message. Do not add to it.

## Why each part is there

**"You told me to go look, and I did."** He gave a curt instruction and it was the right one.
Most people who get that answer never come back. Coming back with the result is the entire
reason this message will be read.

**Admitting the number was wrong, in plain terms.** This costs nothing and buys the only thing
that matters here, which is being someone worth answering. It is also true, and the alternative
is presenting a corrected number as though it had always been right.

**The 8 dead fields, named, with the pattern pointed out, and no ask attached.** Naming them is
what turns this from a report into a gift. Without names he has to go and find them, which is
work; with names it is a one-minute check and a ready-made patch. That is the whole value of the
message — it costs him nothing.

Saying they are 4 boards with `_tab` twins, all carrying the same value, does two things. It
shows the work was actually done rather than grepped, and it hands him the likely cause: one
copy-paste that propagated. A maintainer reading that knows immediately whether it matters.

The `fastboot_oppo` parenthesis is there because it is true and because leaving it out would
make the count look tidier than it is. The template reads the field and no device sets it, which
is an unused branch rather than dead data. Different thing, smaller, and worth one clause.

**One question, phrased as a choice rather than a task.** "Issue, PR, or nothing" lets him
answer in one word, which is how he answers. "Nothing" is offered explicitly so that saying no
is easy. A question that is easy to refuse gets answered more often than one that is not.

## Why not the other things

**Do not re-pitch the tool.** He was asked whether it would be useful to LineageOS and said no.
That was a fair answer: they run a maintainer per device and their users are relatively expert,
so a pre-flight verdict solves a problem they do not have. Arguing with a no is how a live
contact becomes a dead one.

**Do not send a list of new questions.** The last message had four. This one has one.

**Do not make it longer.** He writes in fragments. A long message to a curt answerer reads as
not having noticed who you are talking to. Short is the respectful register here, not the lazy
one.

**Do not mention the grant.** It is irrelevant to him and it converts a technical exchange into
a request for a favour.

## What this is actually worth, and it is more than an endorsement

If the answer is "PR", a one-line merged contribution to LineageOS is worth considerably more in
box 11 than a letter of support. A reviewer can click it. It is dated, public, attributable, and
it is evidence of ecosystem engagement rather than a claim of it. A letter of support is someone
saying a project seems worthwhile; a merged patch is the project having accepted something.

That possibility exists because of a "no". Worth remembering the next time one arrives.

## If there is no reply

Nothing is lost and nothing more is owed. The finding stays in our notes, the correction stands
on its own, and the proposal reports honestly that LineageOS were asked, answered no to
usefulness, and pointed us at the source that corrected our own error. That is a true and
creditable account of an exchange with a project that owes us nothing.
