// SPDX-License-Identifier: GPL-3.0-or-later
// Test pure logic lifted out of START-HERE.html by marker comments.
//
// The console is one offline HTML file with no build step and no module system,
// so its logic cannot be imported. Functions worth testing are wrapped in
//   /* TESTABLE:name */ ... /* END TESTABLE:name */
// and extracted here. This exists because "same device, different mode" -- the
// one path where the device is certainly the same physical object -- rebuilt its
// state from scratch and dropped the device identity. It produced two records
// for one Samsung A5 on 29 Aug, one of them marked "unidentified".
const fs = require("fs");
const path = require("path");
const html = fs.readFileSync(path.join(__dirname, "../bench-kit/START-HERE.html"), "utf8");

function lift(name) {
  const m = html.match(new RegExp(
    "/\\* TESTABLE:" + name + " \\*/([\\s\\S]*?)/\\* END TESTABLE:" + name + " \\*/"));
  if (!m) throw new Error("no TESTABLE block named " + name);
  return m[1];
}

let pass = 0, fail = 0;
function is(got, want, label) {
  if (got === want) { console.log(`    ok    ${label}`); pass++; }
  else { console.log(`    FAIL  ${label}\n            expected ${JSON.stringify(want)}\n            got      ${JSON.stringify(got)}`); fail++; }
}

eval(lift("sameDeviceAgain"));

console.log("\n  sameDeviceAgain");
{
  const cur = { dev: { k: "phone", phone: true }, localId: "samsung-galaxy-a5",
                idsrc: "tester_identified", mode: "file transfer (MTP)" };
  const rec = { reported_device: "samsung SM-A510F", device_local_id: "samsung-galaxy-a5",
                identity_source: "tester_identified" };
  const next = sameDeviceAgain(cur, rec);
  is(next.localId, "samsung-galaxy-a5", "keeps device_local_id across a mode change");
  is(next.idsrc, "tester_identified", "keeps identity_source across a mode change");
  is(next.repeat, true, "marks the capture as a repeat");
  is(next.mode, "", "clears the mode, which is the thing being changed");
  is(next.cap, null, "clears the previous scan");
  is(next.android, null, "clears the previous fingerprint");
  is(next.dev, cur.dev, "keeps the device category");
}
{
  // A device nobody could name stays unnamed on the second capture. It must not
  // silently upgrade to tester_identified just because a record now exists.
  const cur = { dev: { k: "other" }, localId: "unidentified-thing-k3x9", idsrc: "unidentified" };
  const rec = { reported_device: "unidentified thing", device_local_id: "unidentified-thing-k3x9",
                identity_source: "unidentified" };
  const next = sameDeviceAgain(cur, rec);
  is(next.idsrc, "unidentified", "does not upgrade an unidentified device to identified");
  is(next.localId, "unidentified-thing-k3x9", "keeps the unidentified device's id");
}

console.log(`\n  ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
