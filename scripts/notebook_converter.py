"""
Convert Jupyter notebooks to Quarto blog posts.
"""
import json
import shutil
from pathlib import Path
from datetime import datetime

def extract_title_from_notebook(notebook_path):
    """Extract title from notebook filename or first markdown cell."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)

    # Try to find title in first markdown cell
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'markdown':
            source = ''.join(cell.get('source', []))
            # Look for H1 heading
            if source.strip().startswith('# '):
                return source.strip()[2:].split('\n')[0].strip()
            break

    # Fall back to filename
    return notebook_path.stem.replace('-', ' ').replace('_', ' ').title()

def add_front_matter_to_notebook(notebook_path, output_path, title, date):
    """Add YAML front matter as a raw cell at the beginning of the notebook."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)

    # Create front matter cell
    front_matter_cell = {
        "cell_type": "raw",
        "metadata": {},
        "source": [
            "---\n",
            f"title: \"{title}\"\n",
            f"date: \"{date}\"\n",
            "---\n"
        ]
    }

    # Insert at the beginning
    notebook['cells'].insert(0, front_matter_cell)

    # Write to output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2)

def convert_notebook(notebook_path, slug):
    """
    Convert a Jupyter notebook to a Quarto post.

    Args:
        notebook_path: Path to the Jupyter notebook
        slug: URL slug for the post

    Raises:
        FileExistsError: If the post directory already exists
    """
    notebook_path = Path(notebook_path)

    # Determine project root (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    posts_dir = project_root / "posts"
    post_dir = posts_dir / slug

    # Check if post already exists
    if post_dir.exists():
        raise FileExistsError(f"Post directory already exists: {post_dir}")

    # Create post directory
    post_dir.mkdir(parents=True, exist_ok=False)

    # Extract title
    title = extract_title_from_notebook(notebook_path)

    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")

    # Copy notebook and add front matter
    output_notebook = post_dir / "index.ipynb"
    add_front_matter_to_notebook(notebook_path, output_notebook, title, today)

    # TODO: Handle external images if needed in the future
    # For now, embedded images in notebook outputs will work automatically
