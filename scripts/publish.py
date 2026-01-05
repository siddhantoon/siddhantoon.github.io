#!/usr/bin/env python3
"""
Blog publishing system for converting Obsidian notes and Jupyter notebooks to Quarto posts.
"""
import argparse
import sys
from pathlib import Path

def obsidian_command(args):
    """Convert Obsidian note to Quarto post."""
    from obsidian_converter import convert_obsidian_note

    note_path = Path(args.note_path)
    if not note_path.exists():
        print(f"Error: Note file not found: {note_path}")
        sys.exit(1)

    try:
        convert_obsidian_note(note_path, args.slug)
        print(f"Successfully converted Obsidian note to posts/{args.slug}/")
    except FileExistsError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error converting note: {e}")
        sys.exit(1)

def notebook_command(args):
    """Convert Jupyter notebook to Quarto post."""
    from notebook_converter import convert_notebook

    notebook_path = Path(args.notebook_path)
    if not notebook_path.exists():
        print(f"Error: Notebook file not found: {notebook_path}")
        sys.exit(1)

    try:
        convert_notebook(notebook_path, args.slug)
        print(f"Successfully converted notebook to posts/{args.slug}/")
    except FileExistsError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error converting notebook: {e}")
        sys.exit(1)

def deploy_command(args):
    """Deploy blog to GitHub Pages."""
    import subprocess

    try:
        print("Publishing to GitHub Pages...")
        subprocess.run(["quarto", "publish", "gh-pages"], check=True)
        print("Successfully published to GitHub Pages!")
    except subprocess.CalledProcessError as e:
        print(f"Error publishing: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'quarto' command not found. Make sure Quarto is installed.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Publish blogs from Obsidian notes or Jupyter notebooks to Quarto"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Obsidian subcommand
    obsidian_parser = subparsers.add_parser(
        "obsidian",
        help="Convert Obsidian note to Quarto post"
    )
    obsidian_parser.add_argument("note_path", help="Path to the Obsidian note")
    obsidian_parser.add_argument("--slug", required=True, help="URL slug for the post")
    obsidian_parser.set_defaults(func=obsidian_command)

    # Notebook subcommand
    notebook_parser = subparsers.add_parser(
        "notebook",
        help="Convert Jupyter notebook to Quarto post"
    )
    notebook_parser.add_argument("notebook_path", help="Path to the Jupyter notebook")
    notebook_parser.add_argument("--slug", required=True, help="URL slug for the post")
    notebook_parser.set_defaults(func=notebook_command)

    # Deploy subcommand
    deploy_parser = subparsers.add_parser(
        "deploy",
        help="Publish blog to GitHub Pages"
    )
    deploy_parser.set_defaults(func=deploy_command)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute the command
    args.func(args)

if __name__ == "__main__":
    main()
