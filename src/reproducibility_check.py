#!/usr/bin/env python3
import argparse, hashlib, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def main():
    p=argparse.ArgumentParser(); p.add_argument("--scale",choices=["starter","full"],default="starter")
    a=p.parse_args()
    with tempfile.TemporaryDirectory() as d:
        d=Path(d); hashes=[]
        for run in range(2):
            tmp=d/f"run{run}"; tmp.mkdir()
            subprocess.run([sys.executable,str(ROOT/"src"/"generate_data.py"),"--scale",a.scale],
                           check=True,stdout=subprocess.DEVNULL)
            snapshot=tmp/"data"; shutil.copytree(ROOT/"data",snapshot)
            hashes.append({x.name:digest(x) for x in sorted(snapshot.glob("*.csv"))})
        identical=hashes[0]==hashes[1]
        print({"scale":a.scale,"identical":identical,"files_compared":len(hashes[0])})
        if not identical: raise SystemExit(1)
if __name__=="__main__": main()
