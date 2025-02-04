import os

def main():
    # Name of the output file
    output_file = 'merged_code.txt'
    
    # Get the absolute path of this script to exclude it
    script_path = os.path.abspath(__file__)
    
    # Open the output file for writing
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Walk through the current directory and its subdirectories
        for root, dirs, files in os.walk('.'):
            for file in files:
                # Process only .py files
                if file.endswith('.py'):
                    file_path = os.path.abspath(os.path.join(root, file))
                    
                    # Skip this script file itself
                    if file_path == script_path:
                        continue
                    
                    # Write a header to indicate the start of a new file's contents
                    outfile.write(f'# ===== Start of file: {file_path} =====\n\n')
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(content)
                    except Exception as e:
                        outfile.write(f'# Error reading file {file_path}: {e}\n')
                    
                    # Write a footer to indicate the end of this file's contents
                    outfile.write(f'\n# ===== End of file: {file_path} =====\n\n')

if __name__ == '__main__':
    main()
