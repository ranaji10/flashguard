#!/usr/bin/env python3
"""Read and edit docs/tracker/open-items.html without loading the whole file.

The tracker is a 380 KB HTML page with a JSON block inside it. Every sweep used
to cost a full read of that page to change a handful of fields. These commands
operate on the embedded JSON in place, so an item is addressed by id.

  python3 tools/tracker.py notes                 ids and notes, only where a note exists
  python3 tools/tracker.py open                  id, status and title for everything not done
  python3 tools/tracker.py get <id>              one item in full
  python3 tools/tracker.py status <id> <status>  open | doing | done | dropped
  python3 tools/tracker.py append <id> <file>    append a file's text to the item body
  python3 tools/tracker.py clearnote <id>        clear the note once it has been answered
  python3 tools/tracker.py stats                 counts by status and by section
  python3 tools/tracker.py backup                dated copy in a sibling folder of the repo

backup is not a convenience. The tracker is gitignored on purpose, so git is not
its backup, and it exists on exactly one disk plus whatever was last published.
"""
import json, re, sys, os, shutil, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "docs", "tracker", "open-items.html")
BACKUPS = os.path.join(os.path.dirname(ROOT), "tracker-backups")
PAT = re.compile(r'(<script id="appdata" type="application/json">)(.*?)(</script>)', re.S)
STATUSES = ("open", "doing", "done", "dropped")


def load():
    html = open(PAGE, encoding="utf-8").read()
    m = PAT.search(html)
    if not m:
        sys.exit("appdata block not found in " + PAGE)
    return html, m, json.loads(m.group(2))


def save(html, m, data):
    body = json.dumps(data, indent=1, ensure_ascii=False)
    if "</script>" in body:
        sys.exit("refusing to write: item text contains </script>")
    out = html[:m.start(2)] + body + html[m.end(2):]
    json.loads(PAT.search(out).group(2))          # parses back, or nothing is written
    backup()
    open(PAGE, "w", encoding="utf-8").write(out)


def backup():
    os.makedirs(BACKUPS, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    dest = os.path.join(BACKUPS, "open-items-%s.html" % stamp)
    if os.path.exists(PAGE):
        shutil.copy2(PAGE, dest)
    return dest


def walk(data):
    for sec in data["sections"]:
        for item in sec.get("items", []):
            yield sec, item


def find(data, wanted):
    for sec, item in walk(data):
        if item["id"] == wanted:
            return sec, item
    sys.exit("no item with id " + wanted)


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd = argv[0]

    if cmd == "backup":
        print(backup())
        return

    html, m, data = load()

    if cmd == "notes":
        out = {i["id"]: i["note"] for _, i in walk(data) if (i.get("note") or "").strip()}
        print(json.dumps(out, indent=1, ensure_ascii=False))
    elif cmd == "open":
        for sec, i in walk(data):
            if i["status"] != "done":
                print("%-9s %-18s %-7s %s" % (sec["id"], i["id"], i["status"], i["t"]))
    elif cmd == "get":
        print(json.dumps(find(data, argv[1])[1], indent=1, ensure_ascii=False))
    elif cmd == "status":
        if argv[2] not in STATUSES:
            sys.exit("status must be one of " + ", ".join(STATUSES))
        _, item = find(data, argv[1])
        item["status"] = argv[2]
        item["touched"] = datetime.date.today().isoformat()
        save(html, m, data)
        print("%s -> %s" % (argv[1], argv[2]))
    elif cmd == "append":
        text = open(argv[2], encoding="utf-8").read().strip()
        _, item = find(data, argv[1])
        if text in item["d"]:
            sys.exit("that text is already in the body; nothing written")
        item["d"] = item["d"].rstrip() + " " + text
        item["touched"] = datetime.date.today().isoformat()
        save(html, m, data)
        print("appended %d chars to %s" % (len(text), argv[1]))
    elif cmd == "clearnote":
        _, item = find(data, argv[1])
        item["note"] = ""
        save(html, m, data)
        print("note cleared on " + argv[1])
    elif cmd == "stats":
        from collections import Counter
        by_status, by_section = Counter(), Counter()
        for sec, i in walk(data):
            by_status[i["status"]] += 1
            if i["status"] != "done":
                by_section[sec["id"]] += 1
        print("total", sum(by_status.values()))
        for k, v in by_status.most_common():
            print("  %-8s %d" % (k, v))
        print("not done, by section")
        for k, v in by_section.most_common():
            print("  %-10s %d" % (k, v))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
