Got it! Here’s the **cleaned-up** version of the README, following good practices by omitting `.py` extensions and keeping things concise yet informative.

---

# PyGrits

A lightweight version control system implemented in Python, designed for learning about the internals of version control systems like Git.

## Features

- Initialize new repositories  
- Stage files for versioning  
- Create commits with messages  
- View commit history  
- Show file changes (diffs)  
- Restore files from past commits  
- Colored output for better readability  

## Installation

- Clone the Repo and Install Dependencies

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

## Usage

### Initialize a Repository

```bash
pygrits init
```

### Add Files

```bash
pygrits add filename.txt
pygrits add file1.txt file2.txt
```

### Create a Commit

```bash
pygrits commit -m "Your commit message"
```

### View History and Differences

```bash
pygrits log
pygrits show <commit-hash>
```

### Restore Files

```bash
pygrits restore file.txt                  # Restore a file from staging
pygrits restore --source abc123 file.txt  # Restore a file from a specific commit
pygrits restore file1.txt file2.txt       # Restore multiple files
pygrits restore --staged file.txt         # Restore staged version
pygrits restore --hard                    # Discard all changes (restore to HEAD)
```

## Project Structure

```mint
pygrits/
├── pygrits/
│   ├── core/          # Core logic: repository, staging, commits
│   ├── utils/         # Utility functions: hashing, file handling, logging
│   ├── cli/           # Command-line interface
├── tests/             # Unit tests
├── setup.py           # Installation script
└── README.md          # Project documentation
```

## Technical Details

### Storage Format

- `.pygrits/objects/` - Stores file contents and commits  
- `.pygrits/HEAD` - Points to the current commit  
- `.pygrits/index` - Tracks staged changes  

### Commit Structure

```json
{
    "parent": "parent_commit_hash",
    "timestamp": "2024-02-20T10:30:00",
    "message": "Commit message",
    "files": {
        "file.txt": {
            "hash": "content_hash",
            "timestamp": "2024-02-20T10:30:00",
            "size": 1234
        }
    }
}
```

## Notes

- Single branch support only  
- No remote repository functionality  
- No merge conflicts handling
- No stash functionality  
- Simple conflict resolution  