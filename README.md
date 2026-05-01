# 🗂️ AI File Renamer

A local, privacy-first CLI tool that lets you rename files using plain English — powered by [Ollama](https://ollama.com) and any LLM you have running locally.

No cloud. No API keys. No data leaving your machine.

---

## What It Does

Instead of remembering bash commands or regex syntax, you just describe what you want:

```bash
python renamer.py "replace all spaces and dashes with underscores"
python renamer.py "lowercase everything and replace spaces with hyphens"
python renamer.py "remove the word 'final' and 'v2' from all filenames"
python renamer.py "add a prefix of 2025 to all PDF files"
```

The tool reads your folder, sends the file list + your instruction to a local LLM, shows you a preview of what will change, asks for confirmation, then executes.

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running locally
- At least one model pulled in Ollama

---

## Installation

**1. Clone the repo**

```bash
git clone https://github.com/YOUR_USERNAME/ai-file-renamer.git
cd ai-file-renamer
```

**2. Create a virtual environment and install dependencies**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install requests rich
```

**3. Make sure Ollama is running**

```bash
ollama serve
```

---

## Usage

```bash
python renamer.py "your instruction" [/path/to/folder]
```

If you don't specify a folder, it defaults to the current directory.

**Examples:**

```bash
# Run in current folder
python renamer.py "replace spaces and dashes with underscores"

# Target a specific folder
python renamer.py "replace spaces and dashes with underscores" ~/Downloads/project

# More complex instructions
python renamer.py "lowercase all filenames"
python renamer.py "remove the word draft from all filenames"
python renamer.py "replace all spaces with hyphens and lowercase everything"
```

The tool will always show you a **preview table** before making any changes and ask for your confirmation. Nothing is renamed without a `y` from you.

---

## Changing the Model

Open `renamer.py` and update this one line:

```python
MODEL = "gemma4:e2b"  # ← change this to any model you have in Ollama
```

To see what models you have available:

```bash
ollama list
```

Then just swap in the model name. For example:

```python
MODEL = "llama3.2"
MODEL = "mistral"
MODEL = "qwen2.5:14b"
MODEL = "deepseek-r1:8b"
MODEL = "gemma3:27b"
```

### Model Recommendations

| Model | Speed | JSON Reliability | Notes |
|---|---|---|---|
| `gemma4:e2b` | Fast | Good | Lightweight, works well for simple renames |
| `gemma3:27b` | Medium | Very good | Better for complex or ambiguous instructions |
| `qwen2.5:14b` | Medium | Very good | Strong structured output |
| `llama3.2` | Fast | Moderate | May occasionally add extra text |
| `mistral` | Fast | Moderate | Good general option |

> **Note:** Smaller models (1–3B parameters) may occasionally return malformed JSON. If you see parse errors, try a larger model or see the Troubleshooting section below.

---

## Making It a Global Command (Optional)

If you want to call it from anywhere without activating the virtual environment:

```bash
chmod +x renamer.py
sudo ln -s $(pwd)/renamer.py /usr/local/bin/rename-ai
```

Then from any directory:

```bash
rename-ai "clean up these filenames" ~/Desktop/messy-folder
```

---

## How It Works

1. Reads all files in the target directory (not subdirectories)
2. Sends the file list + your instruction to the local LLM via Ollama's API
3. Receives a JSON rename plan from the model
4. Validates the plan (removes hallucinated filenames, skips unchanged files)
5. Shows you a preview table
6. Asks for confirmation before touching anything
7. Executes and reports results

The tool talks to Ollama at `http://localhost:11434` — the default local address. No internet connection required.

---

## Troubleshooting

**`Connection error` or `Ollama not found`**

Make sure Ollama is running:
```bash
ollama serve
```

**`Model returned invalid JSON`**

The LLM didn't follow the structured output format. Try:
- Using a larger or more capable model
- Adding more specific language to your prompt
- Running the command again (LLM outputs can vary)

**File not renamed despite appearing in preview**

The file may have been modified or moved between preview and execution. Check the error message printed next to the `✗` symbol.

**`Model not found` error**

Run `ollama list` to confirm the model name, then update the `MODEL` variable in `renamer.py`.

---

## Limitations

- Processes files in a single directory only (no recursive folder traversal yet)
- Very large folders (500+ files) may hit context limits depending on your model
- Model response time varies — typically 5–20 seconds on local hardware
- LLM output is non-deterministic; always review the preview before confirming

---

## Contributing

Pull requests welcome. Useful additions would include:

- `--dry-run` flag (preview only, no execution)
- `--undo` flag using a saved rename log
- Recursive folder support with `--recursive`
- Support for Ollama running on a remote host

---

## License

MIT — do whatever you want with it.

---

Built by [Bernie Png](https://berniepng.com) · Powered by [Ollama](https://ollama.com)
