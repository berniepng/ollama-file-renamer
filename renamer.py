import os
import sys
import json
import requests
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

console = Console()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma4:e2b"  # change to gemma3:27b for better reasoning

SYSTEM_PROMPT = """You are a file renaming assistant. 
The user will describe how they want files renamed.
You will receive a list of filenames and a natural language instruction.

Respond ONLY with a valid JSON array like this:
[
  {"old": "original filename.txt", "new": "renamed_filename.txt"},
  ...
]

Rules:
- Only include files that actually need renaming
- Preserve file extensions unless explicitly told to change them
- Never invent files not in the list
- Output ONLY the JSON array, no explanation, no markdown
"""

def get_rename_plan(prompt: str, filenames: list[str]) -> list[dict]:
    file_list = "\n".join(f"- {f}" for f in filenames)
    user_message = f"""Files in directory:
{file_list}

Instruction: {prompt}"""

    payload = {
        "model": MODEL,
        "prompt": user_message,
        "system": SYSTEM_PROMPT,
        "stream": False
    }

    console.print("[dim]Thinking...[/dim]")
    response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    response.raise_for_status()

    raw = response.json()["response"].strip()

    # Strip markdown code fences if model adds them anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())

def main():
    if len(sys.argv) < 2:
        console.print("[red]Usage:[/red] python renamer.py \"your rename instruction\" [/path/to/folder]")
        sys.exit(1)

    prompt = sys.argv[1]
    folder = sys.argv[2] if len(sys.argv) > 2 else "."
    folder = os.path.abspath(folder)

    if not os.path.isdir(folder):
        console.print(f"[red]Not a directory:[/red] {folder}")
        sys.exit(1)

    # Get files only (not subdirectories)
    filenames = [
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    ]

    if not filenames:
        console.print("[yellow]No files found in directory.[/yellow]")
        sys.exit(0)

    console.print(f"\n[bold]Folder:[/bold] {folder}")
    console.print(f"[bold]Files found:[/bold] {len(filenames)}")
    console.print(f"[bold]Instruction:[/bold] {prompt}\n")

    try:
        plan = get_rename_plan(prompt, filenames)
    except json.JSONDecodeError as e:
        console.print(f"[red]Model returned invalid JSON:[/red] {e}")
        sys.exit(1)
    except requests.RequestException as e:
        console.print(f"[red]Ollama connection error:[/red] {e}")
        sys.exit(1)

    if not plan:
        console.print("[yellow]Model returned no renames. Nothing to do.[/yellow]")
        sys.exit(0)

    # Show preview table
    table = Table(title="Rename Preview", show_lines=True)
    table.add_column("Original", style="cyan")
    table.add_column("Renamed To", style="green")

    for item in plan:
        table.add_row(item["old"], item["new"])

    console.print(table)

    # Validate — catch hallucinated filenames before they cause errors
    valid_plan = []
    for item in plan:
        if item["old"] not in filenames:
            console.print(f"[red]Skipping (not found):[/red] {item['old']}")
        elif item["old"] == item["new"]:
            console.print(f"[dim]Skipping (no change):[/dim] {item['old']}")
        else:
            valid_plan.append(item)

    if not valid_plan:
        console.print("[yellow]No valid renames after validation.[/yellow]")
        sys.exit(0)

    if not Confirm.ask(f"\nProceed with {len(valid_plan)} rename(s)?"):
        console.print("[dim]Cancelled.[/dim]")
        sys.exit(0)

    # Execute
    success, failed = 0, 0
    for item in valid_plan:
        src = os.path.join(folder, item["old"])
        dst = os.path.join(folder, item["new"])
        try:
            os.rename(src, dst)
            console.print(f"[green]✓[/green] {item['old']} → {item['new']}")
            success += 1
        except OSError as e:
            console.print(f"[red]✗[/red] {item['old']}: {e}")
            failed += 1

    console.print(f"\n[bold]Done.[/bold] {success} renamed, {failed} failed.")

if __name__ == "__main__":
    main()