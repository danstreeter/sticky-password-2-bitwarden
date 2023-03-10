# System Imports
import csv
import hashlib
import sys

# Framework / Library Imports

# Application Imports

# Local Imports

# The export file should be a TEXT file export from a MAC Sticky Password install (Possibly windows, not checked)
sourceFilePath = "./exports/sp_export.txt"
outputFileName = "BWImport-SecureNotes.csv"

memos = {}


def stripEnding(line: str) -> str:
    return line.rstrip("\n")


with open(sourceFilePath) as sourceFile:
    lineNo = 0
    section = "unknown"
    item = f"item_line_{lineNo}"
    foundMemos = False
    for line in sourceFile.readlines():
        lineNo += 1
        line = stripEnding(line)

        # The next two startswith checks presume that the export file has 'My Secure Memos' before 'My Identities'
        if line.startswith("My Identities"):
            print("Got the end of the secure notes on line " + str(lineNo))
            break

        # Once the 'My Secure Memos' block is found, we enter into parsing over each item
        if line.startswith("My Secure Memos"):
            foundMemos = True
            print("Found the start of the memos on line " + str(lineNo))
        else:
            if foundMemos is True:
                # Start of a secure memo
                if line.startswith("Secure memo name"):
                    memoName = line.replace("Secure memo name: ", "")
                    memos[hashlib.md5(bytes(memoName.encode())).hexdigest()] = {
                        "name": memoName,
                        "content": "",
                    }
                # line of a secure memo
                else:
                    # Add to the content of the secure memo by its hash line by line
                    if "memoName" in locals():
                        memos[hashlib.md5(bytes(memoName.encode())).hexdigest()][
                            "content"
                        ] += (line + "\n")
            else:
                # Skip lines when we have not found our Memo block
                continue

secure_memos = []
for _, data in memos.items():
    memo = {
        "folder": "SPW",
        "favorite": "",
        "type": "note",
        "name": data["name"],
        "notes": data["content"],
        "fields": "",
        "reprompt": "",
        "login_uri": "",
        "login_username": "",
        "login_password": "",
        "login_totp": "",
    }
    secure_memos.append(memo)

print("Done")

with open(outputFileName, "w", newline="") as csvfile:
    fieldnames = secure_memos[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for memo in secure_memos:
        writer.writerow(memo)

print(f"Output file written to: {outputFileName}")
