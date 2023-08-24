import os
import subprocess

# Set the path to your Git repository
repo_path = r'D:\crm'

# Get a list of all files in the repository directory
all_files = os.listdir(repo_path)

print("Total files in repository:", len(all_files))

# Get a list of files that have already been committed
committed_files = []
commit_log = subprocess.check_output(['git', '-C', repo_path, 'log', '--name-only', '--pretty=format:""'], text=True)
for line in commit_log.splitlines():
    if line.strip() != "":
        committed_files.extend(line.split())

print("Files already committed:", committed_files)

# Iterate through the files to add and commit each file individually
for file in all_files:
    if file not in committed_files:
        file_path = os.path.join(repo_path, file)
    
        print("Processing file:", file)
    
        # Add the file to the Git index
        subprocess.run(['git', '-C', repo_path, 'add', file_path])
    
        print("File added to Git index.")
    
        # Commit the added file
        subprocess.run(['git', '-C', repo_path, 'commit', '-m', 'Add file: {}'.format(file)])
    
        print("File committed.")
    
print("All files added and committed!")
