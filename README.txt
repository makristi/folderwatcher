This program supports a few users who can watch the smae folder or different ones. 

Changes which are supported:
- add/rename/delete/move a folder/file
- file content change -> only for small text files (the requirements of project were like this. Ideally, use existing libraries for diff, support various types and conversions as well as big files)
- stores backup copy of files in ./localstorage with uuid name (needed for checking diff)

How to start the program:
1. Type in the console: python StartWatcher.py
2. Wait until the ptomp and enter the folder you ant to watch
3. The program will display on the console if any changes happened
