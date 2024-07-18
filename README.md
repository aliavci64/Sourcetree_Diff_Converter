# Sourcetree_Diff_Converter
Export Sourcetree Commit Differences As HTML File

Thanks to this Python script, you can output the commit differences 
you can see on the Sourcetree application as an HTML file.

# Documentation for Writing Commit Differences to an HTML File Using a Python Script in Sourcetree

This documentation explains the setup and usage of a Python script created to identify the differences between two commits in Sourcetree and save them as an HTML file.

## Requirements

- Python 3.x
- PyInstaller
- Git

## Python Script

You can find the relevant Python script in the attached zip file. Detailed information about the libraries and functions used in the script is provided to assist users in developing, updating, or personalizing the script as needed.

## Converting the Python Script to an Executable File

First, you need to install PyInstaller. Run the following command in the command prompt:
```sh
pip install pyinstaller
```
Once PyInstaller is installed, navigate to the directory containing your Python script in the command prompt and run the following command: (It is recommended to compile the Python file on your system before the conversion process.)

```sh
pyinstaller --onefile your_script.py
```

Replace 'your_script.py' with the name of the Python file you want to convert to an executable. Once the conversion is complete, you will find your executable file in a folder named 'dist' within the relevant directory.

## Setup and Usage in Sourcetree

### 1. Add the Python Script to Sourcetree

To use this script in Sourcetree, you need to add the script to Sourcetree's custom actions section.

### 2. Creating a Custom Action in Sourcetree

#### 1. Open Sourcetree.
#### 2. Go to 'Tools' -> 'Options' -> 'Custom Actions' tab from the menu.
#### 3. Click on 'Add' and enter the following information:
  ##### Menu Caption: Enter a name for the custom action as desired by the user. (Example: Export Git Diff to HTML)
  ##### Script to Run: Enter the path to the .exe file to be run or click the button on the right to locate and select the     .exe file from your computer directory.
  ##### Parameters: '$SHA $REPO $WORKINGDIR'
    $SHA: Argument for obtaining the Commit IDs, should be left as '$SHA'.
    $REPO: Argument for obtaining your repo path, can be manually entered or left as '$REPO' to be automatically detected by the script.
    $WORKINGDIR: Argument for specifying where the outputs should be saved. If you want the outputs to be saved directly in the repo, enter '$REPO'. If an external folder is desired for the outputs, manually enter the file path.

### 3. Usage
1. Select up to two commits in Sourcetree.
2. Right-click and choose the custom action you created from the 'Custom Actions' menu.
3. The script will determine the differences if a single commit is selected, it will compare with the previous version; if two commits are selected, it will compare the differences between the two commits and save them as an HTML file in a folder named 'Differences'.

## Libraries and Functions

### os
**Where Used**: 'create_unique_output_dir' and functions like 'os.path.join', 'os.path.exists', 'os.makedirs'.

**Why Used**: The 'os' module is used for file and directory operations. It is especially used to create unique folders for output files, combine file paths, and check the existence of directories.

**Customization Notes**: If you want to personalize the name of the output file or the HTML document, or update the paths, the related changes should be made where the 'os' module is used.

### subprocess
**Where Used**: In the functions 'get_git_diff', 'get_changed_files', 'get_commit_diff'.

**Why Used**: The 'subprocess' module is used to run external commands and capture their output. In this project, it is used to run Git commands to get the differences and changed files between specified commits.

**Customization Notes**: It is **NOT RECOMMENDED** to personalize or change where the 'subprocess' module is used. If updates to the functions or arguments are necessary, the related changes should be made where the 'subprocess' module is used.
