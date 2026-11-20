import hashlib
import os
import json
import sys
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASELINE_FILE = os.path.join(BASE_DIR, "baseline.json")
IOC_FILE = os.path.join(BASE_DIR, "fim_iocs.txt")
CHUNK = 65536

# Hash names shown in the output and in fim_iocs.txt
LABELS = {"md5": "MD5", "sha1": "SHA-1", "sha256": "SHA-256"}


# ---------- Step 1: get the file path ----------
def pick_file_popup():
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        return None

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(title="Select a file")
    root.destroy()
    return path or None

def get_path():
    p = input("Enter the file path (or press Enter to open the file picker) :").strip().strip('"')
    if not p:
        p = pick_file_popup()
    if not p:
        print("No file selected")
        sys.exit(1)

    # stop if the path is not a real file
    if not os.path.isfile(p):
        print("Not a valid file")
        sys.exit(1)

    return os.path.abspath(p)


# ---------- Step 2: calculate the hashes and save ----------
def compute_hashes(path):
    # Read file one time and compute all three hashes
    md5, sha1, sha256 = hashlib.md5(), hashlib.sha1(), hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK):
            md5.update(chunk)
            sha1.update(chunk)
            sha256.update(chunk)
    return {
        "md5" : md5.hexdigest(),
        "sha1" : sha1.hexdigest(),
        "sha256" : sha256.hexdigest(),
    }

def load_baseline():
    if os.path.exists(BASELINE_FILE):
        with open(BASELINE_FILE) as f:
            return json.load(f)
    return {}

def save_baseline(data):
    with open(BASELINE_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------- Step 3: save everything in fim_iocs.txt ----------
def read_saved_hashes():
    """Read the hash values already in fim_iocs.txt (ignore the label)."""
    saved = set()
    if os.path.exists(IOC_FILE):
        with open(IOC_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    saved.add(line.split(":")[-1].strip().lower())
    return saved

def write_entry(path, status, new=None, old=None):
    # status is NEW, CHANGED or DELETED
    # lines that start with # are comments (file name, time, status, old hashes)
    # hash lines are written as MD5: "hash" and only if they are not saved before
    saved = read_saved_hashes()
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(IOC_FILE, "a") as f:
        f.write(f"# File: {path}  ({time})  [{status}]\n")

        if old:
            for key, label in LABELS.items():
                f.write(f"# Old {label}: {old.get(key, 'not saved')}\n")

        if new:
            fresh = [key for key in LABELS if new[key].lower() not in saved]
            for key in fresh:
                f.write(f"{LABELS[key]}: {new[key]}\n")
            if not fresh:
                f.write("# These hashes are already saved above\n")

        f.write("\n")    # empty line after each entry, to keep it clean

    print(f"[3] Recorded in {IOC_FILE} as [{status}]")


def hash_and_save(path):
    hashes = compute_hashes(path)
    print(f"[2] File: {path}")
    print("    Hashes of the file :")
    for key, label in LABELS.items():
        print(f"    {label:<8}: {hashes[key]}")

    base = load_baseline()
    entry = {
        **hashes,
        "size" : os.path.getsize(path),
        "saved_at" : datetime.now().isoformat(timespec="seconds"),
    }

    if path not in base:
        base[path] = entry
        save_baseline(base)
        print(f"    Not in Database, hashes save in {BASELINE_FILE}")
        write_entry(path, "NEW", new=hashes)
    elif base[path]["sha256"] == hashes["sha256"]:
        print("    [Ok] The file has not changed")
        # Old baseline may not have MD5 and SHA-1, so add them
        if "md5" not in base[path] or "sha1" not in base[path]:
            base[path].update(md5=hashes["md5"], sha1=hashes["sha1"])
            save_baseline(base)
        print(f"[3] Nothing to add in {IOC_FILE}")
    else:
        print("    [Changed!] This file is modified")
        print()
        print("    Old hashes (saved earlier):")
        for key, label in LABELS.items():
            print(f"      {label:<8}: {base[path].get(key, 'not saved')}")
        print()
        print("    New hashes (now):")
        for key, label in LABELS.items():
            print(f"      {label:<8}: {hashes[key]}")
        print()
        # record the change BEFORE the baseline is updated, or the old hashes will be lost
        write_entry(path, "CHANGED", new=hashes, old=base[path])
        if input("    Update the baseline with the new hashes? (y/n): ").lower() == "y":
            base[path] = entry
            save_baseline(base)
            print("    Baseline updated")


# Check if the saved files still exist
def check_deleted_files():
    # look at all files saved in the baseline and find which ones no longer exist
    base = load_baseline()
    missing = [p for p in base if not os.path.exists(p)]
    if not missing:
        return

    print("[!] These saved files are missing (deleted or moved):")
    for p in missing:
        print(f"    {p}")
        write_entry(p, "DELETED")

    if input("Remove them from the baseline? (y/n): ").lower() == "y":
        for p in missing:
            del base[p]
        save_baseline(base)
        print("Removed from baseline.")


def main():
    check_deleted_files()
    path = get_path()
    hash_and_save(path)


if __name__ == "__main__":
    main()
