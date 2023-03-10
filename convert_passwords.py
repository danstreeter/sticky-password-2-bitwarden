# System Imports
import csv
import sys

# Framework / Library Imports
from bs4 import BeautifulSoup

# Application Imports

# Local Imports

# The source file should be an XML file extracted from a WINDOWS installation of Sticky Password.
sourceXMLFilePath = "./exports/default.xml"
# The export file should be a TEXT file export from a MAC Sticky Password install (Possibly windows, not checked)
sourceTXTFilePath = "./exports/sp_export.txt"
outputFileName = "BWImport-Passwords.csv"

passwords = []
missing_passwords = []

# Used for storing passwords found in the XML to prevent defaults when dealing with the App Logins from the text file
passwordNamelist = []

with open(sourceXMLFilePath, "r", encoding="utf-16") as sourceFile:
    data = sourceFile.read()

bs = BeautifulSoup(data, "xml")
groupsRaw = bs.find_all("Group")

accountsRaw = bs.find_all("Account")

max = 100000
i = 0
for account in accountsRaw:
    i += 1
    if i > max:
        continue
    print(f"[{i}/{len(accountsRaw)}]")
    accountId = account["ID"]
    accountName = account["Name"]
    accountLink = account["Link"]
    accountComments = account.get("Comments", "")
    accountLoginLinksElem = account.findChildren("LoginLinks")
    if len(accountLoginLinksElem) != 1:
        print(f"{accountName} seemed to have not one LoginLinks element within it...")
        sys.exit(1)
    else:
        accountLoginLinks = accountLoginLinksElem[0].findChildren("Login")

    accountFolder = "SPW"
    # if accountFolderBs:
    #     accountFolder += f"/{accountFolderBs['Name']}"

    if len(accountLoginLinks) < 1:
        print(f"Found an account without any logins!")
        print(f"{accountName}")
        sys.exit(0)
    accountLoginI = 0
    accountNameSuffix = ""
    for login in accountLoginLinks:
        # Handle if we have more than one login link by suffixing the name with the username
        accountLogin = bs.find("Login", {"ID": login["SourceLoginID"]})
        accountLoginI += 1
        if len(accountLoginLinks) > 1:
            print(f"FOUND {len(accountLoginLinks)} in {accountName}")
            accountNameSuffix = f" | {accountLogin['Name']}"

        print(f"Name: {accountName}{accountNameSuffix}")
        print(f"Folders: {accountFolder}")
        print(f"Link: {accountLink}")
        print(f"Comments: {accountComments}")
        print(f"Login Links: {len(accountLoginLinks)}")
        print(f"Username: {accountLogin['Name']}")
        print(f"Password: {accountLogin.get('Password', '')}")
        if not accountLogin.get("Password", ""):
            missing_passwords.append(accountName)

        # Personal = folder & favourite
        # Organisation = collections & !favourite

        accountToTransfer = {
            "folder": accountFolder,
            "favorite": "",
            "type": "login",
            "name": accountName + accountNameSuffix,
            "notes": accountComments,
            "fields": "",
            "reprompt": "",
            "login_uri": accountLink,
            "login_username": accountLogin["Name"],
            "login_password": accountLogin.get("Password", ""),
            "login_totp": "",
        }
        passwords.append(accountToTransfer)

    print()

print(len(missing_passwords))
print(missing_passwords)

print("Done")

with open(outputFileName, "w", newline="") as csvfile:
    fieldnames = passwords[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for password in passwords:
        writer.writerow(password)

print(f"Output file written to: {outputFileName}")
