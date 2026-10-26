import xml.etree.ElementTree as ET, subprocess, time, re, sys
def adb(*a): return subprocess.run(["adb","-s","localhost:5555",*a],capture_output=True,text=True).stdout
def dump():
    adb("shell","uiautomator","dump","/sdcard/ui.xml"); adb("pull","/sdcard/ui.xml","ui.xml")
    try: return ET.parse("ui.xml").getroot()
    except Exception: return None
def tap_text(root, vals):
    for n in root.iter("node"):
        t=(n.get("text") or "").strip(); d=(n.get("content-desc") or "").strip()
        if t in vals or d in vals:
            m=re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", n.get("bounds") or "")
            if m:
                x=(int(m.group(1))+int(m.group(3)))//2; y=(int(m.group(2))+int(m.group(4)))//2
                adb("shell","input","tap",str(x),str(y)); return True
    return False
r=dump()
if r is None: print("no ui"); sys.exit(1)
tap_text(r, {"CHECK","Make Play Integrity Request"})
time.sleep(20)
r=dump() or r
tap_text(r, {"Show JSON response","Raw JSON","COPY JSON"})
time.sleep(3)
r=dump() or r
for n in r.iter("node"):
    t=(n.get("text") or "").strip()
    if t.startswith("{") and "deviceIntegrity" in t:
        print(t); open("verdict.json","w").write(t); sys.exit(0)
print("NO JSON")
for n in r.iter("node"):
    t=(n.get("text") or "").strip()
    if t: print(t[:200])
sys.exit(2)
