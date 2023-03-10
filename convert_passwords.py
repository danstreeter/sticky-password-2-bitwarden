# System Imports

# Framework / Library Imports

# Application Imports

# Local Imports
from extractors import Extractors
from utils import bitwarden_csv_row, write_out_csv

get_xml_passwords_from = "./exports/default.xml"
get_txt_passwords_from = "./exports/sp_export.txt"
get_txt_memos_from = "./exports/sp_export.txt"


if "get_xml_passwords_from" in locals():
    ## Get the Web Accounts from the XML file (As only the Windows exported XML file includes comments)
    web_accounts = Extractors.extract_from_xml("./exports/default.xml")
    web_passwords = []
    for account in web_accounts:
        web_passwords.append(
            bitwarden_csv_row(
                accountName=account["name"],
                accountFolder="SPW Web Accounts",
                accountLink=account["link"],
                accountLogin={
                    "Name": account["login"],
                    "Password": account["password"],
                },
                accountComments=account.get("comments", ""),
                accountNameSuffix=None,
            )
        )
    write_out_csv("BWImport-Passwords.csv", web_passwords)

if "get_txt_passwords_from" in locals():
    ## Get the app passwords from the text file
    app_accounts = Extractors.extract_from_text("./exports/sp_export.txt")[
        "app_accounts"
    ]
    app_passwords = []
    for account in app_accounts:
        app_passwords.append(
            bitwarden_csv_row(
                accountName=account["name"],
                accountFolder="SPW App Accounts",
                accountLink=account["link"],
                accountLogin={
                    "Name": account["login"],
                    "Password": account["password"],
                },
                accountComments=account.get("comments", ""),
                accountNameSuffix=None,
            )
        )
    write_out_csv("BWImport-AppPasswords.csv", app_passwords)

if "get_txt_memos_from" in locals():
    ## Get the Secure Memos out of the text file
    secure_memos = Extractors.extract_memos_from_text("./exports/sp_export.txt")
    memos = []
    for memo in secure_memos:
        memos.append(
            bitwarden_csv_row(
                accountName=memo["name"],
                accountFolder="SPW Secure Note",
                accountLink="",
                accountLogin={"Name": "", "Password": ""},
                accountComments=memo["content"],
                accountNameSuffix=None,
            )
        )
    write_out_csv("BWImport-SecureNotes.csv", memos)
