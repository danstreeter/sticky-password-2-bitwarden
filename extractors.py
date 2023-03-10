# System Imports
import hashlib
import sys

# Framework / Library Imports
from bs4 import BeautifulSoup

# Application Imports

# Local Imports
from utils import accountKey, stripEnding


class Extractors:
    @classmethod
    def extract_from_text(self, filename: str) -> dict:
        sourceFilePath = filename

        allowedStartStrings = (
            "My Web Accounts",
            "My Application Accounts",
            "Account name",
            "Link",
            "Logins",
            "Login",
            "Password",
            "Description",
        )

        passwords = {}

        with open(sourceFilePath) as sourceFile:
            lineNo = 0
            section = "unknown"
            item = f"item_line_{lineNo}"
            for line in sourceFile.readlines():
                lineNo += 1

                if line.startswith("My Web Accounts"):
                    section = "web_accounts"
                    continue

                if line.startswith("My Application Accounts"):
                    section = "app_accounts"
                    continue

                if section not in passwords:
                    passwords[section] = {}

                if len(line) == 1 and ord(line) == 10:
                    print("Blank Line Seperator")
                    continue

                if not line.startswith(allowedStartStrings):
                    print(f"Unknown line start found on line {lineNo}: {line[:10]}")
                    # sys.exit(0)
                    break

                accountNameSep = "Account name: "
                if line.startswith(accountNameSep):
                    print("New Account Entry")
                    item = accountKey(lineNo)
                    if item not in passwords[section]:
                        passwords[section][item] = {}

                    account_name = stripEnding(line.replace(accountNameSep, ""))
                    passwords[section][item]["name"] = account_name
                    passwords[section][item]["comments"] = ""

                linkSep = "Link: "
                if line.startswith(linkSep):
                    print("New Link")
                    link = stripEnding(line.replace(linkSep, ""))
                    passwords[section][item]["link"] = link

                loginSep = "Login: "
                if line.startswith(loginSep):
                    # Jump over an existing entry if login already exists
                    if "login" in passwords[section][item]:
                        print("Skipping over")
                        item = accountKey(lineNo)
                        if item not in passwords[section]:
                            passwords[section][item] = {
                                "name": account_name,
                                "link": link,
                            }
                    print("New Login")
                    passwords[section][item]["login"] = stripEnding(
                        line.replace(loginSep, "")
                    )

                passSep = "Password: "
                if line.startswith(passSep):
                    print("New Password")
                    passwords[section][item]["password"] = stripEnding(
                        line.replace(passSep, "")
                    )

                descSep = "Description: "
                if line.startswith(descSep):
                    print("New Description")
                    passwords[section][item]["description"] = stripEnding(
                        line.replace(descSep, "")
                    )

        for password_type in passwords:
            print(f"{len(passwords[password_type])} passwords found in {password_type}")

        nice_passwords = {}
        # Remove all the temporary keys
        for type in passwords:
            for _, item in passwords[type].items():
                if type not in nice_passwords:
                    nice_passwords[type] = []
                nice_passwords[type].append(item)

        # with open("passwords.json", "w") as outputFile:
        #     outputFile.write(json.dumps(passwords))

        print("Done")
        return nice_passwords

    @classmethod
    def extract_from_xml(self, sourceXMLFilePath: str) -> dict:
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
            passwordNamelist.append(accountName)
            accountLink = account["Link"]
            accountComments = account.get("Comments", "")
            accountLoginLinksElem = account.findChildren("LoginLinks")
            if len(accountLoginLinksElem) != 1:
                print(
                    f"{accountName} seemed to have not one LoginLinks element within it..."
                )
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

                # accountToTransfer = {
                #     "folder": accountFolder,
                #     "favorite": "",
                #     "type": "login",
                #     "name": accountName + accountNameSuffix,
                #     "notes": accountComments,
                #     "fields": "",
                #     "reprompt": "",
                #     "login_uri": accountLink,
                #     "login_username": accountLogin["Name"],
                #     "login_password": accountLogin.get("Password", ""),
                #     "login_totp": "",
                # }
                clean_output = {
                    "name": accountName + accountNameSuffix,
                    "link": accountLink,
                    "login": accountLogin["Name"],
                    "password": accountLogin.get("Password", ""),
                    "comments": accountComments,
                }
                passwords.append(clean_output)
                # name, link, login, password

            print()

        print(len(missing_passwords))
        print(missing_passwords)

        print("Done")
        return passwords

    @classmethod
    def extract_memos_from_text(self, sourceFilePath: str):
        memos = {}
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
                                memos[
                                    hashlib.md5(bytes(memoName.encode())).hexdigest()
                                ]["content"] += (line + "\n")
                    else:
                        # Skip lines when we have not found our Memo block
                        continue

        secure_memos = []
        for _, data in memos.items():
            # memo = {
            #     "folder": "SPW",
            #     "favorite": "",
            #     "type": "note",
            #     "name": data["name"],
            #     "notes": data["content"],
            #     "fields": "",
            #     "reprompt": "",
            #     "login_uri": "",
            #     "login_username": "",
            #     "login_password": "",
            #     "login_totp": "",
            # }
            memo = {
                "name": data["name"],
                "content": data["content"],
            }
            secure_memos.append(memo)

        print("Done")
        return secure_memos


##########
# Example:
# import json
# print(json.dumps(Extractors.extract_from_text("./exports/sp_export.txt"), indent=4))
# Extractors.extract_from_text("./exports/sp_export.txt")
