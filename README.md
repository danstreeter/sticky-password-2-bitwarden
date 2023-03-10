# Sticky Password 2 BitWarden

Scripts to convert Sticky Password export files to BitWarden import files

## To Do's

### Get 'App Accounts' from text export `sp_export.txt`

These are not exported within the XML so need to be extracted from the text output, however the text output does not differentiate between 'App Accounts' and 'Web Accounts' and they all appear together. Therefore, the text file has to be parsed after the XML one checking all pre-found XML account entries and ignoring if already present, leaving just the App Accounts remaining to be found in the text file.
