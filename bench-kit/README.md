# Bench kit

Copy this whole folder to a USB stick formatted ExFAT or FAT so both macOS and Linux
can write to it. Name the stick `BENCH`.

    START-HERE.html      Open this first. Works offline, from file://, no network.
    STOP-LIST.txt        Print it. Tape it to the machine.
    protocol.md          The one-page version to send to testers.
    example-record.json  A filled-in record so people can see what "done" looks like.
    scripts/
      00-setup.sh        Install read-only tools, take the USB baseline
      01-detect.sh       Diff against baseline, read descriptors
      02-android.sh      Allowlisted Android fingerprint. Read-only.
      03-fastboot.sh     Named fastboot variables. Read-only.

Run scripts with `bash 00-setup.sh` rather than `./00-setup.sh`. A FAT-formatted stick
does not carry the executable bit.

**Nothing in this kit writes to any device.** The scripts query an explicit allowlist
of properties rather than dumping everything, because `adb devices` and
`fastboot getvar all` both print the device serial and this data is published openly.
Do not simplify them into a dump.
