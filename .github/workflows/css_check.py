"""Check TypeScript files for CSS violations and embedded CSS."""
import argparse
import os
import re
import sys
from collections import namedtuple

# Define namedtuples for storing results
Violation = namedtuple('Violation', ['file_path', 'css_file', 'reason'])
CorrectImport = namedtuple('CorrectImport', ['file_path', 'css_file'])
EmbeddedViolation = namedtuple('EmbeddedViolation', ['file_path', 'css_codes'])
CSSCheckResult = namedtuple('CSSCheckResult', ['violations', 'correct_imports', 'embedded_violations'])

def check_embedded_css(content: str) -> list:
    """
    Check for embedded CSS in the content.

    Args:
        content: The content of the file to check.

    Returns:
        A list of embedded CSS violations found.
    """
    embedded_css_pattern = r"#([0-9a-fA-F]{3}){1,2}"  # Matches CSS color codes
    return re.findall(embedded_css_pattern, content)

def check_files(
    directory: str, exclude_files: list, exclude_directories: list, allowed_css_patterns: list
) -> CSSCheckResult:
    """
    Check TypeScript files for CSS violations and correct CSS imports.

    Args:
        directory: The directory to check.
        exclude_files: List of files to exclude from analysis.
        exclude_directories: List of directories to exclude from analysis.
        allowed_css_patterns: List of allowed CSS file patterns.

    Returns:
        A CSSCheckResult namedtuple containing lists of violations, correct CSS imports, and embedded CSS violations.
    """
    violations = []
    correct_css_imports = []
    embedded_css_violations = []

    # Normalize exclude paths
    exclude_files = set(os.path.abspath(file) for file in exclude_files)
    exclude_directories = set(os.path.abspath(dir) for dir in exclude_directories)

    for root, _, files in os.walk(directory):
        # Skip excluded directories
        if any(root.startswith(exclude_dir) for exclude_dir in exclude_directories):
            continue

        for file in files:
            file_path = os.path.abspath(os.path.join(root, file))

            # Skip excluded files
            if file_path in exclude_files:
                continue

            # Process TypeScript files
            if file.endswith((".ts", ".tsx")) and "test" not in root:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except (IOError, UnicodeDecodeError) as e:
                    print(f"Error reading file {file_path}: {e}")
                    continue

                # Check for CSS imports with an improved regex pattern
                css_imports = re.findall(r'import\s+.*?["\'](.+?\.css)["\']', content)
                for css_file in css_imports:
                    # Try to find the CSS file
                    css_file_path = os.path.join(os.path.dirname(file_path), css_file)
                    if not os.path.exists(css_file_path):
                        # If not found, try to find it relative to the src directory
                        src_dir = os.path.abspath(directory)
                        css_file_path = os.path.join(src_dir, css_file)

                    # Check if the CSS file exists
                    if not os.path.exists(css_file_path):
                        violations.append(Violation(file_path, css_file, "File not found"))
                    # Check if the CSS import matches the allowed patterns
                    elif any(css_file.endswith(pattern) for pattern in allowed_css_patterns):
                        correct_css_imports.append(CorrectImport(file_path, css_file))
                    else:
                        violations.append(Violation(file_path, css_file, "Invalid import"))

                # Check for embedded CSS
                embedded_css = check_embedded_css(content)
                if embedded_css:
                    embedded_css_violations.append(EmbeddedViolation(file_path, embedded_css))

    return CSSCheckResult(violations, correct_css_imports, embedded_css_violations)

def main():
    """Run the CSS check script."""
    parser = argparse.ArgumentParser(
        description="Check for CSS violations in TypeScript files."
    )
    parser.add_argument("--directory", required=True, help="Directory to check.")
    parser.add_argument(
        "--exclude_files",
        nargs="*",
        default=[],
        help="Specific files to exclude from analysis.",
    )
    parser.add_argument(
        "--exclude_directories",
        nargs="*",
        default=[],
        help="Directories to exclude from analysis.",
    )
    parser.add_argument(
        "--allowed_css_patterns",
        nargs="*",
        default=["app.module.css"],
        help="Allowed CSS file patterns.",
    )
    parser.add_argument(
        "--show_success",
        action="store_true",
        help="Show successful CSS imports.",
    )
    args = parser.parse_args()

    result = check_files(
        directory=args.directory,
        exclude_files=args.exclude_files,
        exclude_directories=args.exclude_directories,
        allowed_css_patterns=args.allowed_css_patterns,
    )

    output = []
    exit_code = 0
    if result.violations:
        output.append("CSS Import Violations:")
        for violation in result.violations:
            output.append(f"- {violation.file_path}: {violation.css_file} ({violation.reason})")
        exit_code = 1

    if result.embedded_violations:
        output.append("\nEmbedded CSS Violations:")
        for violation in result.embedded_violations:
            output.append(f"- {violation.file_path}: {', '.join(violation.css_codes)}")
        exit_code = 1   

    if output:
        print("\n".join(output))
        print("""
Please address the above CSS violations:
1. For invalid CSS imports, ensure you're using the correct import syntax and file paths.
2. For embedded CSS, move the CSS to appropriate stylesheet files and import them correctly.
3. Make sure to use only the allowed CSS patterns as specified in the script arguments.
4. Check that all imported CSS files exist in the specified locations.
""")
    if args.show_success and result.correct_imports:
        print("\nCorrect CSS Imports:")
        for import_ in result.correct_imports:
            print(f"- {import_.file_path}: {import_.css_file}")

    sys.exit(exit_code)

if __name__ == "__main__":
    main()

