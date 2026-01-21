The heredoc is getting cut off. Let me give you a simpler approach - download the file directly:
bashcat > /opt/mythos/updates/patch_code.py << 'EOF'
#!/usr/bin/env python3
import re, sys
from pathlib import Path
from datetime import datetime

class CodePatcher:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(self.file_path, 'r') as f:
            self.original_content = f.read()
        self.lines = self.original_content.split('\n')
        self.modified = False
    
    def backup(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.file_path.with_suffix(f'.{timestamp}.backup')
        with open(backup_path, 'w') as f:
            f.write(self.original_content)
        print(f"Backup: {backup_path}")
        return backup_path
    
    def find_function(self, function_name):
        func_pattern = re.compile(rf'^(\s*)(?:async\s+)?def {re.escape(function_name)}\s*\(')
        start_line = None
        base_indent = None
        for i, line in enumerate(self.lines):
            match = func_pattern.match(line)
            if match:
                start_line = i
                base_indent = len(match.group(1))
                break
        if start_line is None:
            return None
        end_line = len(self.lines)
        for i in range(start_line + 1, len(self.lines)):
            line = self.lines[i]
            if not line.strip() or line.strip().startswith('#'):
                continue
            if line.startswith(' ' * base_indent) and not line.startswith(' ' * (base_indent + 1)):
                end_line = i
                break
        return (start_line, end_line, base_indent)
    
    def replace_function(self, function_name, new_code):
        location = self.find_function(function_name)
        if location is None:
            print(f"ERROR: Could not find function {function_name}")
            return False
        start_line, end_line, base_indent = location
        print(f"Found {function_name} at lines {start_line + 1}-{end_line}")
        new_lines = new_code.split('\n')
        new_lines = [(' ' * base_indent + line if line.strip() else line) for line in new_lines]
        self.lines = self.lines[:start_line] + new_lines + self.lines[end_line:]
        self.modified = True
        print(f"Replaced function {function_name}")
        return True
    
    def save(self):
        if not self.modified:
            print("No modifications made")
            return False
        new_content = '\n'.join(self.lines)
        with open(self.file_path, 'w') as f:
            f.write(new_content)
        print(f"Saved changes to {self.file_path}")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python patch_code.py replace-function <file> <function_name> <new_code_file>")
        sys.exit(1)
    command = sys.argv[1]
    file_path = sys.argv[2]
    function_name = sys.argv[3]
    new_code_file = sys.argv[4]
    with open(new_code_file, 'r') as f:
        new_code = f.read()
    patcher = CodePatcher(file_path)
    patcher.backup()
    if patcher.replace_function(function_name, new_code):
        patcher.save()
    else:
        sys.exit(1)