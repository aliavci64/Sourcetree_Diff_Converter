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

First, you need to install **PyInstaller**. Run the following command in the command prompt:
```sh
pip install pyinstaller
```
Once PyInstaller is installed, navigate to the directory containing your Python script in the command prompt and run the following command: (It is recommended to compile the Python file on your system before the conversion process.)

```sh
pyinstaller --onefile your_script.py
```

Replace **'your_script.py'** with the name of the Python file you want to convert to an executable. Once the conversion is complete, you will find your executable file in a folder named **'dist'** within the relevant directory.

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
2. Right-click and choose the custom action you created from the **'Custom Actions'** menu.
3. The script will determine the differences if a single commit is selected, it will compare with the previous version; if two commits are selected, it will compare the differences between the two commits and save them as an HTML file in a folder named 'Differences'.

## Libraries, Functions and Variables

### Variable {number_of_previous_rows}
It is a global variable that specifies how many lines before printing the differences will start and how many lines will end. It is defined at the very beginning of the code file, under the libraries, and can be modified.

### os
**Where Used**: **'create_unique_output_dir'** and functions like **'os.path.join'**, **'os.path.exists'**, **'os.makedirs'**.

**Why Used**: The **'os'** module is used for file and directory operations. It is especially used to create unique folders for output files, combine file paths, and check the existence of directories.

**Customization Notes**: If you want to personalize the name of the output file or the HTML document, or update the paths, the related changes should be made where the **'os'** module is used.

### subprocess
**Where Used**: In the functions **'get_git_diff'**, **'get_changed_files'**, **'get_commit_diff'**.

**Why Used**: The **'subprocess'** module is used to run external commands and capture their output. In this project, it is used to run Git commands to get the differences and changed files between specified commits.

**Customization Notes**: It is **NOT RECOMMENDED** to personalize or change where the **'subprocess'** module is used. If updates to the functions or arguments are necessary, the related changes should be made where the 'subprocess' module is used.

### html
**Where Used**: In the function **'write_diff_to_html'**.

**Why Used**: The **'html'** module is used to write version control process outputs to an HTML file and format the texts for better visualization.

**Customization Notes**: To personalize titles, change font and format, or update the text added to the outputs considered **‘Added’** or **‘Deleted’**, the related changes should be made where the **'html'** module is used.

### re (Regular Expressions)
**Where Used**: In the function **'extract_function_names'**.

**Why Used**: The **'re'** module is used for pattern matching and extracting in texts. In this project, it is used to extract the names of the functions with differences from the Git diff output.

### sys
**Where Used**: In the main function block **(if __name__ == "__main__":)**.

**Why Used**: The **'sys'** module is used to get and process command-line arguments. In this project, it is used to get the parameters like commit IDs, repo path, and output directory from the user.
**Customization Notes**: If you want to change the order of the arguments or the arguments themselves, the related changes should be made where the **'sys'** module is used.

**IMPORTANT NOTE**: Any changes made in the **'sys'** module must also be updated in Sourcetree's custom action **'Parameters'** section. Otherwise, the program might produce errors or work unexpectedly.

## Functions Usage
**get_git_diff**: Used to get the differences between two commits. Returns the Git diff output for a specific file.

**get_file_content_at_commit**: Gets the content of files in the specified commit.

**extract_function_names**: Prints the names of functions. Used to print the names of functions with detected differences.

**write_diff_to_html**: Writes the obtained diff output to an HTML file. Colors the differences and adds relevant line numbers.

**get_changed_files**: Used to get the list of files changed between two commits.

**get_commit_diff**: Used to get the list of files changed in a specific commit.

**convert_path**: Used to convert Windows and Unix-style file paths. This function is used to prevent compilation errors arising from differences in file path definitions (“\” vs. “/”) between the command prompt and Git Bash terminal.

**create_unique_output_dir**: Checks if a directory exists and creates a unique directory name.

## Summary
These libraries and functions enable your project to interact with Git, analyze the differences, and write them to an HTML document. Each library is carefully selected to fulfill a specific function and supports the project's main objective of analyzing and reporting commit differences.
