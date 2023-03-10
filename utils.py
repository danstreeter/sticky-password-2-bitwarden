# System Imports
import csv

# Framework / Library Imports

# Application Imports

# Local Imports


def stripEnding(line: str) -> str:
    return line.rstrip("\n")


def accountKey(lineNo: int) -> str:
    return f"account_on_line_{lineNo}"


def bitwarden_csv_row(
    accountName,
    accountFolder,
    accountLink,
    accountLogin,
    accountType="login",
    accountComments="",
    accountNameSuffix=None,
):
    if accountNameSuffix is None:
        accountNameSuffix = ""
    return {
        "folder": accountFolder,
        "favorite": "",
        "type": accountType,
        "name": str(accountName) + accountNameSuffix,
        "notes": accountComments,
        "fields": "",
        "reprompt": "",
        "login_uri": accountLink,
        "login_username": accountLogin["Name"],
        "login_password": accountLogin.get("Password", ""),
        "login_totp": "",
    }


def write_out_csv(outputFileName: str, passwords):
    with open(outputFileName, "w", newline="") as csvfile:
        fieldnames = passwords[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for password in passwords:
            writer.writerow(password)

    print(f"Output file written to: {outputFileName}")
