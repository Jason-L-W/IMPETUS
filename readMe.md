# IMPETUS Rollercoaster

---

### How to get this working on the school PC:
Access the terminal through the Window's Search Bar &rarr; Type: terminal
1) Open up terminal
2) Download Git &rarr; Type: **winget install --id Git.Git -e --source winget**
3) Download Python &rarr; Type: **winget install Python.Python.3.13** &rarr; When prompted input: **y** &rarr; Then: **ENTER**
4) Close the terminal and reopen it
5) Clone Repo &rarr; Type: **git clone https://github.com/Jason-L-W/IMPETUS.git**
6) Go into the file &rarr; Type: **cd IMPETUS**
7) Download the requirements &rarr; Type: **pip install -r requirements.txt**
If step 7 doesn't work do the following:\
&rarr; Go to Window's Search\
&rarr; Type in App Execution Aliases\
&rarr; Turn off App Installer for python.exe/ptyhon3.exe\
&rarr; Close the terminal
&rarr; Continue from Step 6

8) Run the script &rarr; Type: **python GUI.py**

*Note*: If you receive a **winget** error, then your out of luck, change to a new PC.

---

### How to remove the folder
If you are in the IMPETUS folder:
1) Get out of the IMPETUS folder &rarr; Type: **cd ..** once
2) Remove the folder &rarr; Type: **Remove-Item -Recurse -Force IMPETUS**

If you are not in the IMPETUS:
1) Type in the terminal **ls** and check if you see a file name **IMPETUS**
    (On the school PC, you should see it)
2) Remove the folder &rarr; Type: **Remove-Item -Recurse -Force IMPETUS**

### How to update the folder:
1) Make sure you are already in the IMPETUS folder
2) Update Using &rarr; Type: **git pull**

### To access the photo's. Do the following:
Type in the terminal &rarr; .\image.png

---