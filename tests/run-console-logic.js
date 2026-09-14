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
eval(lift("normaliseRawProps"));
eval(lift("isValidRawProps"));

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

console.log("\n  normaliseRawProps & isValidRawProps");
const { execSync } = require("child_process");
const propsDir = path.join(__dirname, "android");
const deriveScript = path.join(__dirname, "../bench-kit/scripts/derive.sh");

const propFiles = fs.readdirSync(propsDir).filter(f => f.endsWith(".props"));
for (const file of propFiles) {
  const fullPath = path.join(propsDir, file);
  const raw = fs.readFileSync(fullPath, "utf8");
  const canonical = raw.split("\n").filter(l => !l.startsWith("#!")).join("\n");
  const canonicalDerived = execSync(`bash "${deriveScript}"`, { input: canonical, encoding: "utf8" });

  // 1. Canonical text unchanged
  const normCanonical = normaliseRawProps(canonical);
  is(normCanonical, canonical, `${file}: canonical text unchanged`);

  // 2. CRLF text normalises to canonical
  const crlfText = canonical.replace(/\n/g, "\r\n");
  const normCrlf = normaliseRawProps(crlfText);
  is(normCrlf, canonical, `${file}: CRLF normalises to canonical`);

  // 3. Per-line leading and trailing whitespace normalises to canonical
  const whitespaceText = canonical.split("\n").map(l => "  " + l + "   ").join("\n");
  const normWs = normaliseRawProps(whitespaceText);
  is(normWs, canonical, `${file}: leading/trailing whitespace normalises to canonical`);

  // 4. Blank lines interleaved derive identically
  const blankLinesText = canonical.split("\n").map(l => l + "\n\n").join("\n");
  const normBlanks = normaliseRawProps(blankLinesText);
  const blanksDerived = execSync(`bash "${deriveScript}"`, { input: normBlanks, encoding: "utf8" });
  is(blanksDerived, canonicalDerived, `${file}: blank lines interleaved derive identically`);

  // 5. Bare values with no '=' are refused by guard
  const bareValues = canonical.split("\n").map(l => (l.includes("=") ? l.split("=").slice(1).join("=") : l)).join("\n");
  is(isValidRawProps(bareValues), false, `${file}: bare values with no '=' are refused by isValidRawProps`);

  // 6. Valid raw props are accepted by guard (unless empty)
  if (canonical.trim().length > 0) {
    is(isValidRawProps(canonical), true, `${file}: valid raw props accepted by isValidRawProps`);
  }
}

console.log(`\n  ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
