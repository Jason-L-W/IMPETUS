# IMPETUS Rollercoaster



Generate rollercoaster tracks for NoLimits 2.

---

## Quickstart

### Manual Install - Windows (Terminal)
These are instructions on how to get this working on the school PC.

```powershell
# Open Terminal
winget install --id Git.Git -e --source winget
winget install Python.Python.3.13
# Close and reopen Terminal after this
git clone https://github.com/Jason-L-W/IMPETUS.git
cd IMPETUS
pip install -r requirements.txt
python GUI.py
```

*Note*:
- If you receive a **winget** error, then your out of luck, change to a new PC. (Need to go to **System Environment Variables** and add it.)
- If you recieve a **PATH** error, then your out of luck, change to a new PC. (Need to go to **System Environment Variables** and add it.)
- If you recieve a **Python** error, then go to **App Execution Aliases** and turn of **App Installer** for **python.exe**. Then reopen Powershell to update it and try again.

---

### How To Remove The Folder
If you are in the IMPETUS folder:
```powershell
cd ..
Remove-Item -Recurse -Force IMPETUS
```

If you are not in the IMPETUS:
```powershell
# Check file location of IMPETUS folder with *ls*
# On the school PC, you should see it as soon as *ls* is typed in. If it is do the following:
Remove-Item -Recurse -Force IMPETUS
```

### How to Update The Folder
```powershell
# Make sure you are in the IMPETUS folder
git pull
```

### To Access The Photo's
```powershell
# Replace *image* with the actual name
.\image.png
```

---