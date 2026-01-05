"""
Convert Obsidian notes to Quarto blog posts.
"""
import re
import shutil
import yaml
from pathlib import Path
from datetime import datetime

def load_config():
    """Load configuration from config.yaml."""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def extract_title(content, filename):
    """Extract title from content or filename."""
    # Try to find first H1 heading
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()

    # Fall back to filename
    return filename.replace('-', ' ').replace('_', ' ').title()

def find_image_references(content):
    """Find all image references in the markdown content."""
    images = []

    # Pattern 1: Obsidian format ![[image.png]]
    obsidian_pattern = r'!\[\[([^\]]+\.(png|jpg|jpeg|gif|svg|webp))\]\]'
    images.extend(re.findall(obsidian_pattern, content, re.IGNORECASE))

    # Pattern 2: Standard markdown ![alt](path/image.png)
    markdown_pattern = r'!\[([^\]]*)\]\(([^\)]+\.(png|jpg|jpeg|gif|svg|webp))\)'
    markdown_matches = re.findall(markdown_pattern, content, re.IGNORECASE)
    images.extend([(match[1], match[2]) for match in markdown_matches])

    # Return unique image filenames (just the filename with extension)
    return list(set([img[0] for img in images]))

def convert_image_references(content, image_mapping):
    """Convert Obsidian image references to standard markdown."""
    # Convert ![[image.png]] to ![](image.png)
    for old_ref, new_ref in image_mapping.items():
        # Obsidian format
        content = content.replace(f'![[{old_ref}]]', f'![]({new_ref})')

        # Standard markdown with path - replace with just filename
        content = re.sub(
            rf'!\[([^\]]*)\]\([^\)]*{re.escape(old_ref)}\)',
            rf'![\1]({new_ref})',
            content
        )

    return content

def convert_obsidian_note(note_path, slug):
    """
    Convert an Obsidian note to a Quarto post.

    Args:
        note_path: Path to the Obsidian note
        slug: URL slug for the post

    Raises:
        FileExistsError: If the post directory already exists
    """
    config = load_config()
    note_path = Path(note_path)

    # Determine project root (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    posts_dir = project_root / "posts"
    post_dir = posts_dir / slug

    # Check if post already exists
    if post_dir.exists():
        raise FileExistsError(f"Post directory already exists: {post_dir}")

    # Read the note content
    with open(note_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title
    title = extract_title(content, note_path.stem)

    # Find all image references
    image_refs = find_image_references(content)

    # Create post directory
    post_dir.mkdir(parents=True, exist_ok=False)

    # Copy images and build mapping
    image_mapping = {}
    vault_path = Path(config['vault_path'])
    attachments_folder = config['attachments_folder']

    for image_ref in image_refs:
        # Extract just the filename from the reference
        image_filename = Path(image_ref).name

        # Try to find the image in various locations
        possible_paths = [
            vault_path / attachments_folder / image_filename,
            note_path.parent / attachments_folder / image_filename,
            note_path.parent / image_filename,
        ]

        source_image = None
        for possible_path in possible_paths:
            if possible_path.exists():
                source_image = possible_path
                break

        if source_image:
            # Copy to post directory
            dest_image = post_dir / image_filename
            shutil.copy2(source_image, dest_image)
            image_mapping[image_ref] = image_filename
        else:
            print(f"Warning: Image not found: {image_filename}")

    # Convert image references in content
    content = convert_image_references(content, image_mapping)

    # Generate front matter
    today = datetime.now().strftime("%Y-%m-%d")
    front_matter = {
        'title': title,
        'date': today
    }

    # Create final content with front matter
    final_content = f"---\n{yaml.dump(front_matter, default_flow_style=False)}---\n\n{content}"

    # Write to index.qmd
    output_file = post_dir / "index.qmd"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
