#!/usr/bin/env python3
"""
Concatenate markdown sections into a single slides.md file.
Supports both markdown sections and custom HTML slides.
"""

import os
from pathlib import Path
import re

def concat_sections():
    """Combine all section files into slides.md."""
    
    presentation_dir = Path(__file__).parent.parent
    sections_dir = presentation_dir / "sections"
    output_file = presentation_dir / "slides.md"
    
    # Get all section files in order
    section_files = []
    
    # First, get numbered markdown sections
    for file in sorted(sections_dir.glob("*.md")):
        if file.name[0].isdigit():
            section_files.append(file)
    
    print(f"Found {len(section_files)} section files to process")
    
    # Build the combined content
    combined_content = []
    combined_content.append("<!-- AUTO-GENERATED FILE - DO NOT EDIT DIRECTLY -->")
    combined_content.append("<!-- Edit files in sections/ directory instead -->")
    combined_content.append("")
    
    for i, section_file in enumerate(section_files):
        print(f"Processing {section_file.name}")
        
        # Read section content
        with open(section_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Add section separator (except for first section)
        if i > 0:
            combined_content.append("\n---\n")
        
        # Check for custom HTML include directive
        if "<!-- include-html:" in content:
            # Process custom HTML includes
            content = process_html_includes(content, sections_dir)
        
        combined_content.append(f"<!-- Section: {section_file.name} -->")
        combined_content.append(content)
    
    # Write combined file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(combined_content))
    
    print(f"✓ Combined {len(section_files)} sections into slides.md")
    print(f"✓ Output file: {output_file}")
    
    # Also create a file watcher version for VS Code task
    create_file_watcher()

def process_html_includes(content, sections_dir):
    """Replace HTML include directives with actual content."""
    
    # Pattern to find include directives
    pattern = r'<!-- include-html: (.*?) -->'
    
    def replace_include(match):
        html_file = match.group(1)
        html_path = sections_dir / "custom" / html_file
        
        if html_path.exists():
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Wrap in reveal.js section
            return f'</section>\n<section data-html>\n{html_content}\n</section>\n<section data-markdown>'
        else:
            return f'<!-- ERROR: {html_file} not found -->'
    
    return re.sub(pattern, replace_include, content)

def create_file_watcher():
    """Create a simple file watcher for VS Code task."""
    
    watcher_content = """#!/usr/bin/env python3
import time
import subprocess
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Warning: watchdog not installed. File watching disabled.")
    print("Install with: pip install watchdog")

if WATCHDOG_AVAILABLE:
    class SectionHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith('.md') or event.src_path.endswith('.html'):
                print(f"Change detected: {event.src_path}")
                subprocess.run([Path(__file__).parent / "concat-sections.py"])

    if __name__ == "__main__":
        observer = Observer()
        observer.schedule(SectionHandler(), path='sections', recursive=True)
        observer.start()
        print("Watching for changes in sections/...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
else:
    print("File watcher not available. Run concat-sections.py manually after changes.")
"""
    
    watcher_path = Path(__file__).parent / "watch-sections.py"
    with open(watcher_path, 'w') as f:
        f.write(watcher_content)
    os.chmod(watcher_path, 0o755)
    print("✓ Created file watcher script")

if __name__ == "__main__":
    concat_sections()
