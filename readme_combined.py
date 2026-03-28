import os

def combine_markdown_files(root_folder, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        first_file = True

        for dirpath, _, filenames in os.walk(root_folder):
            for filename in sorted(filenames):
                if filename.endswith('.md'):
                    full_path = os.path.join(dirpath, filename)
                    
                    # Relative path
                    relative_path = os.path.relpath(full_path, root_folder)
                    
                    with open(full_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                    
                    # Separator between files
                    if not first_file:
                        outfile.write("\n---\n\n")
                    else:
                        first_file = False

                    # Write as a heading (you can change ## to # or ###)
                    outfile.write(f"## {relative_path}\n\n")
                    outfile.write(content)
                    outfile.write("\n")

if __name__ == "__main__":
    root_folder = "READMEs"
    output_file = "combined.md"
    
    combine_markdown_files(root_folder, output_file)
    print(f"Combined markdown saved to {output_file}")