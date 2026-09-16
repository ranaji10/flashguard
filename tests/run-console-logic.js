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
eval(lift("buildAndroidBlock"));

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

console.log("\n  buildAndroidBlock");
{
  // 1. Browser-only phone capture: all Android fields must be "unknown", never "not_applicable"
  const curPhone = { dev: { k: "android", phone: true } };
  const blockPhone = buildAndroidBlock(curPhone);
  const keys = Object.keys(blockPhone);
  is(keys.length >= 18, true, "browser-only phone: contains all android fields");
  const naKeys = keys.filter(k => blockPhone[k] === "not_applicable");
  is(naKeys.length, 0, "browser-only phone: zero fields are not_applicable");
  const nonUnknownKeys = keys.filter(k => blockPhone[k] !== "unknown");
  is(nonUnknownKeys.length, 0, "browser-only phone: all fields are unknown");

  // 2. Browser-only non-phone capture: all Android fields must be "not_applicable", never "unknown"
  const curCamera = { dev: { k: "camera", phone: false } };
  const blockCamera = buildAndroidBlock(curCamera);
  const cameraKeys = Object.keys(blockCamera);
  const unknownKeys = cameraKeys.filter(k => blockCamera[k] === "unknown");
  is(unknownKeys.length, 0, "browser-only non-phone: zero fields are unknown");
  const nonNaKeys = cameraKeys.filter(k => blockCamera[k] !== "not_applicable");
  is(nonNaKeys.length, 0, "browser-only non-phone: all fields are not_applicable");

  // 3. Derived phone capture with empty slot_suffix: NA_android empty string produces "unknown", not "not_applicable"
  const curDerived = {
    dev: { k: "android", phone: true },
    android: { product_model: "Pixel 4", slot_suffix: "", partition_scheme: "unknown" }
  };
  const blockDerived = buildAndroidBlock(curDerived);
  is(blockDerived.product_model, "Pixel 4", "derived phone: populated field passed through");
  is(blockDerived.slot_suffix, "unknown", "derived phone: empty slot_suffix becomes unknown, not not_applicable");
  const derivedNaKeys = Object.keys(blockDerived).filter(k => blockDerived[k] === "not_applicable");
  is(derivedNaKeys.length, 0, "derived phone: zero fields are not_applicable on phone");

  // 4. Raw getprop pending capture: emits android_raw and android_derivation: pending, NO derived fields
  const curRaw = {
    dev: { k: "android", phone: true },
    android_raw: "ro.product.model=Pixel 4"
  };
  const blockRaw = buildAndroidBlock(curRaw);
  is(blockRaw.android_raw, "ro.product.model=Pixel 4", "raw capture: android_raw present");
  is(blockRaw.android_derivation, "pending", "raw capture: android_derivation is pending");
  is(blockRaw.product_model, undefined, "raw capture: derived product_model omitted");
  is(blockRaw.partition_scheme, undefined, "raw capture: derived partition_scheme omitted");
  is(Object.keys(blockRaw).length, 2, "raw capture: exactly two keys emitted");
}

console.log("\n  host_platform, host_shell, capture_route & browser_enumeration schema agreement");
{
  const schemaPath = path.join(__dirname, "../data/schema.md");
  const schemaText = fs.readFileSync(schemaPath, "utf8");

  const platMatch = schemaText.match(/"host_platform":\s*"([^"]+)"/);
  if (!platMatch) throw new Error("data/schema.md missing host_platform definition");
  const allowedPlatforms = new Set(platMatch[1].split("|").map(s => s.trim()));

  const shellMatch = schemaText.match(/"host_shell":\s*"([^"]+)"/);
  if (!shellMatch) throw new Error("data/schema.md missing host_shell definition");
  const allowedShells = new Set(shellMatch[1].split("|").map(s => s.trim()));

  const routeMatch = schemaText.match(/"capture_route":\s*"([^"]+)"/);
  if (!routeMatch) throw new Error("data/schema.md missing capture_route definition");
  const allowedRoutes = new Set(routeMatch[1].split("|").map(s => s.trim()));

  const enumMatch = schemaText.match(/"browser_enumeration":\s*"([^"]+)"/);
  if (!enumMatch) throw new Error("data/schema.md missing browser_enumeration definition");
  const allowedEnums = new Set(enumMatch[1].split("|").map(s => s.trim()));

  // 1. Prove that undeclared values fail schema validation
  const plantedInvalidPlatform = "windows_powershell";
  is(allowedPlatforms.has(plantedInvalidPlatform), false, "planted undeclared platform windows_powershell is rejected by schema");

  const plantedInvalidShell = "bash";
  is(allowedShells.has(plantedInvalidShell), false, "planted undeclared shell bash is rejected by schema");

  const plantedInvalidRoute = "usb_direct";
  is(allowedRoutes.has(plantedInvalidRoute), false, "planted undeclared route usb_direct is rejected by schema");

  const plantedInvalidEnum = "failed";
  is(allowedEnums.has(plantedInvalidEnum), false, "planted undeclared browser_enumeration failed is rejected by schema");

  // 2. Extract all platform values used or referenced in START-HERE.html
  const dataPMatches = Array.from(html.matchAll(/data-p="([^"]+)"/g)).map(m => m[1]);
  const hostPlatAssigns = Array.from(html.matchAll(/host_platform\s*[:=]\s*"([^"]+)"/g)).map(m => m[1]);
  const scrRouteCalls = Array.from(html.matchAll(/scrRoutePlatform\("([^"]+)"\)/g)).map(m => m[1]);

  const allHtmlPlatforms = [...new Set([...dataPMatches, ...hostPlatAssigns, ...scrRouteCalls])];
  for (const plat of allHtmlPlatforms) {
    is(allowedPlatforms.has(plat), true, `START-HERE.html platform '${plat}' is declared in data/schema.md`);
  }

  // 3. Extract all shell values used or referenced in START-HERE.html
  const dataSMatches = Array.from(html.matchAll(/data-s="([^"]+)"/g)).map(m => m[1]);
  const hostShellAssigns = Array.from(html.matchAll(/host_shell\s*[:=]\s*"([^"]+)"/g)).map(m => m[1]);

  const allHtmlShells = [...new Set([...dataSMatches, ...hostShellAssigns])];
  for (const sh of allHtmlShells) {
    is(allowedShells.has(sh), true, `START-HERE.html shell '${sh}' is declared in data/schema.md`);
  }

  // 4. Extract all capture_route values in START-HERE.html
  const captureRouteAssigns = Array.from(html.matchAll(/capture_route\s*[:=]\s*"([^"]+)"/g)).map(m => m[1]);
  const allHtmlRoutes = [...new Set(captureRouteAssigns)];
  for (const route of allHtmlRoutes) {
    is(allowedRoutes.has(route), true, `START-HERE.html capture_route '${route}' is declared in data/schema.md`);
  }

  // 5. Extract all browser_enumeration values in START-HERE.html
  const browserEnumAssigns = Array.from(html.matchAll(/browser_enumeration\s*[:=]\s*"([^"]+)"/g)).map(m => m[1]);
  const allHtmlEnums = [...new Set(browserEnumAssigns)];
  for (const benum of allHtmlEnums) {
    is(allowedEnums.has(benum), true, `START-HERE.html browser_enumeration '${benum}' is declared in data/schema.md`);
  }

  // 6. Test buildRecord / saveRecord resolution across all capture routes & enumerations
  try {
    const uuid = () => "00000000-0000-0000-0000-000000000000";
    const slug = s => (s || "").toLowerCase().replace(/[^a-z0-9]+/g, "-");
    const NA = v => (v === undefined || v === null || v === "" ? "not_applicable" : v);
    eval(lift("buildRecord"));

    // PowerShell branch
    {
      const cur = { dev: { k: "phone", phone: true }, host_platform: "windows", host_shell: "powershell", capture_route: "adb_host", browser_enumeration: "not_attempted", android_raw: "ro.product.model=Pixel 4" };
      const S = { host_platform: "windows", host_shell: "powershell", tester: "test" };
      const rec = buildRecord(cur, S, true, "adb", "Pixel 4", "default", "", {}, "test.desc", 1, "test-agent");
      is(rec.host_platform, "windows", "powershell branch: host_platform is windows");
      is(rec.host_shell, "powershell", "powershell branch: host_shell is powershell");
      is(rec.capture_route, "adb_host", "powershell branch: capture_route is adb_host");
      is(rec.browser_enumeration, "not_attempted", "powershell branch: browser_enumeration is not_attempted");
      is(allowedPlatforms.has(rec.host_platform), true, "powershell branch: host_platform in schema enum");
      is(allowedShells.has(rec.host_shell), true, "powershell branch: host_shell in schema enum");
      is(allowedRoutes.has(rec.capture_route), true, "powershell branch: capture_route in schema enum");
      is(allowedEnums.has(rec.browser_enumeration), true, "powershell branch: browser_enumeration in schema enum");
    }

    // cmd branch
    {
      const cur = { dev: { k: "phone", phone: true }, host_platform: "windows", host_shell: "cmd", capture_route: "adb_host", browser_enumeration: "enumerated", android_raw: "ro.product.model=Pixel 4" };
      const S = { host_platform: "windows", host_shell: "cmd", tester: "test" };
      const rec = buildRecord(cur, S, true, "adb", "Pixel 4", "default", "", {}, "test.desc", 1, "test-agent");
      is(rec.host_platform, "windows", "cmd branch: host_platform is windows");
      is(rec.host_shell, "cmd", "cmd branch: host_shell is cmd");
      is(rec.capture_route, "adb_host", "cmd branch: capture_route is adb_host");
      is(rec.browser_enumeration, "enumerated", "cmd branch: browser_enumeration is enumerated");
      is(allowedPlatforms.has(rec.host_platform), true, "cmd branch: host_platform in schema enum");
      is(allowedShells.has(rec.host_shell), true, "cmd branch: host_shell in schema enum");
      is(allowedRoutes.has(rec.capture_route), true, "cmd branch: capture_route in schema enum");
      is(allowedEnums.has(rec.browser_enumeration), true, "cmd branch: browser_enumeration in schema enum");
    }

    // macOS branch with browser enumeration failure / tester_cancelled
    {
      const cur = { dev: { k: "phone", phone: true }, host_platform: "macos", host_shell: "not_applicable", capture_route: "adb_host", browser_enumeration: "tester_cancelled", android: { product_model: "Pixel 4" } };
      const S = { host_platform: "macos", host_shell: "not_applicable", tester: "test" };
      const rec = buildRecord(cur, S, true, "adb", "Pixel 4", "default", "", {}, "test.desc", 1, "test-agent");
      is(rec.host_platform, "macos", "macos branch: host_platform is macos");
      is(rec.host_shell, "not_applicable", "macos branch: host_shell is not_applicable");
      is(rec.capture_route, "adb_host", "macos branch: capture_route is adb_host");
      is(rec.browser_enumeration, "tester_cancelled", "macos branch: browser_enumeration is tester_cancelled");
      is(allowedPlatforms.has(rec.host_platform), true, "macos branch: host_platform in schema enum");
      is(allowedShells.has(rec.host_shell), true, "macos branch: host_shell in schema enum");
      is(allowedRoutes.has(rec.capture_route), true, "macos branch: capture_route in schema enum");
      is(allowedEnums.has(rec.browser_enumeration), true, "macos branch: browser_enumeration in schema enum");
    }

    // Live Linux USB branch
    {
      const cur = { dev: { k: "phone", phone: true }, host_platform: "ubuntu_live", host_shell: "not_applicable", capture_route: "linux_live", browser_enumeration: "not_listed", android: { product_model: "Pixel 4" } };
      const S = { host_platform: "ubuntu_live", host_shell: "not_applicable", tester: "test" };
      const rec = buildRecord(cur, S, true, "adb", "Pixel 4", "default", "", {}, "test.desc", 1, "test-agent");
      is(rec.host_platform, "ubuntu_live", "ubuntu_live branch: host_platform is ubuntu_live");
      is(rec.host_shell, "not_applicable", "ubuntu_live branch: host_shell is not_applicable");
      is(rec.capture_route, "linux_live", "ubuntu_live branch: capture_route is linux_live");
      is(rec.browser_enumeration, "not_listed", "ubuntu_live branch: browser_enumeration is not_listed");
      is(allowedPlatforms.has(rec.host_platform), true, "ubuntu_live branch: host_platform in schema enum");
      is(allowedShells.has(rec.host_shell), true, "ubuntu_live branch: host_shell in schema enum");
      is(allowedRoutes.has(rec.capture_route), true, "ubuntu_live branch: capture_route in schema enum");
      is(allowedEnums.has(rec.browser_enumeration), true, "ubuntu_live branch: browser_enumeration in schema enum");
    }
  } catch (e) {
    console.log("    FAIL  buildRecord evaluation:", e.message);
    fail++;
  }
}

console.log(`\n  ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
