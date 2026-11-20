# File Integrity Monitor

A small python tool that checks if a file is changed or deleted. It calculates the hashes of the file, saves them, and compares them the next time you run it.

## Why I made this

While learning SOC work, I read that if an important file is changed by someone, its hash also changes. A File Integrity Monitor (FIM) uses this to find the change. I wanted to understand how this works, so I made a small one. It also saves the hashes in a file, so I can check them later on VirusTotal with my [IOC Enrichment Tool](https://github.com/sahil-darmal/ioc-enrichment-tool).

## What it does

1. Asks for a file path. If you press Enter, a file picker window opens
2. Calculates MD5, SHA-1 and SHA-256 hashes of the file (the file is read only one time)
3. If the file is new, it saves the hashes in `baseline.json` and marks it as **NEW**
4. If the file is already saved and the hash is same, it says the file has not changed
5. If the hash is different, it marks the file as **CHANGED** and shows the old and new hashes. Then it asks if you want to update the baseline
6. Every time you run it, it also checks all saved files. If any file is missing (deleted or moved), it marks it as **DELETED**
7. All NEW, CHANGED and DELETED records are saved in one file, `fim_iocs.txt`

## What you need

- Python 3
- No extra library is needed. It uses only the python built-in modules (hashlib, json, os, tkinter)

## How to run

```
python fim.py
```

Then type the full path of a file, or press Enter and select the file from the popup.

## Files it makes

Both files are made in the same folder where `fim.py` is.

- `baseline.json` : saved hashes, size and time of each file
- `fim_iocs.txt` : record of NEW, CHANGED and DELETED files

## Sample output

New file:

```
[2] File: C:\Users\you\Desktop\Test Folder\test.txt
    Hashes of the file :
    MD5     : d41d8cd98f00b204e9800998ecf8427e
    SHA-1   : da39a3ee5e6b4b0d3255bfef95601890afd80709
    SHA-256 : e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    Not in Database, hashes save in C:\Users\you\Desktop\Test Folder\baseline.json
[3] Recorded in C:\Users\you\Desktop\Test Folder\fim_iocs.txt as [NEW]
```

Changed file:

```
    [Changed!] This file is modified

    Old hashes (saved earlier):
      MD5     : d41d8cd98f00b204e9800998ecf8427e
      SHA-1   : da39a3ee5e6b4b0d3255bfef95601890afd80709
      SHA-256 : e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

    New hashes (now):
      MD5     : 02fb3ca6b276053ebd800907948944f2
      SHA-1   : 7720c68f3387aee42a77a372ee4468cf6cf39c58
      SHA-256 : df60d76cb0da7452a009c7cf3063b1b1dd80983dd8788f89a27f595db6cbffac

[3] Recorded in C:\Users\you\Desktop\Test Folder\fim_iocs.txt as [CHANGED]
    Update the baseline with the new hashes? (y/n):
```

Deleted file:

```
[!] These saved files are missing (deleted or moved):
    C:\Users\you\Desktop\Test Folder\test.txt
[3] Recorded in C:\Users\you\Desktop\Test Folder\fim_iocs.txt as [DELETED]
Remove them from the baseline? (y/n):
```

## How fim_iocs.txt looks

Lines that start with `#` are comments (file name, time, status and old hashes). The hash lines have a label so we know which one is MD5, SHA-1 or SHA-256.

```
# File: C:\Users\you\Desktop\Test Folder\test.txt  (2026-11-20 14:30:00)  [CHANGED]
# Old MD5: d41d8cd98f00b204e9800998ecf8427e
# Old SHA-1: da39a3ee5e6b4b0d3255bfef95601890afd80709
# Old SHA-256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
MD5: 02fb3ca6b276053ebd800907948944f2
SHA-1: 7720c68f3387aee42a77a372ee4468cf6cf39c58
SHA-256: df60d76cb0da7452a009c7cf3063b1b1dd80983dd8788f89a27f595db6cbffac
```

A hash is saved only one time. If the same hash is already in the file, it is not written again.

## Use with the IOC Enrichment Tool

`fim_iocs.txt` can be used by my [IOC Enrichment Tool](https://github.com/sahil-darmal/ioc-enrichment-tool). Keep `fim_iocs.txt` in the same folder as `ioc_check.py` and press Enter when it asks for an IP. It will check the SHA-256 hashes on VirusTotal.

## Limits

- It checks only one file in each run. Whole folder is not supported yet
- It does not run in the background. You have to run it yourself
- Files are saved by their full path. If you move a file to another folder, it will show as DELETED for the old path and NEW for the new path
- If a file is changed, it does not tell what is changed inside the file. It only tells that the hash is different
- The file picker needs tkinter. If it is not available, type the path

## What I want to add next

- Find renamed files. If the hash is same but the file name is different, show it as RENAMED instead of DELETED and NEW
- Check a whole folder in one run

## Note

I made this for learning. A changed hash only tells that the file is different. It does not mean the file is bad, so always check by yourself.
