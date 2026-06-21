# context-aware-wordlist

A context-aware wordlist generator for web application penetration testing. Instead of throwing generic paths at a target, it analyzes the actual HTML content and URL of a page to generate endpoints tailored specifically to that application — its domain, tech stack, naming conventions, and implied business logic.

Powered by Google Gemini.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- A [Google Gemini API key](https://aistudio.google.com/apikey)

## Installation

```bash
git clone https://github.com/your-username/context-aware-wordlist
cd context-aware-wordlist
uv sync
```

## Configuration

Create a `config.yaml` file in the root of the project:

```yaml
api_key: "YOUR_GEMINI_API_KEY"
model_name: "gemini-3.5-flash"
```

| Field | Description |
|---|---|
| `api_key` | Your Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey) |
| `model_name` | Gemini model to use, e.g. `gemini-3.5-flash`, `gemini-2.5-pro` |

> **Note:** `config.yaml` contains your API key — make sure it's in `.gitignore`.

## Usage

### Inline HTML content

```bash
uv run main.py <url> <html_content>
```

### HTML content from a file

Use the `-f` flag to treat the second argument as a path to an HTML file:

```bash
uv run main.py <url> <path_to_file> -f
```

### Examples

```bash
# Inline content
uv run main.py "https://example.com" "<html><body>...</body></html>"

# From a file
uv run main.py "https://example.com" page.html -f
```

A common workflow is to save the page HTML with `curl` and then pass it to the generator:

```bash
curl -s https://example.com -o page.html
uv run main.py "https://example.com" page.html -f
```

## How it works

The tool sends the page URL and HTML content to Gemini with a system prompt instructing it to act as a penetration tester. The model analyzes the page to understand the application's domain, tech stack, and business logic, then generates a list of endpoints that are contextually relevant to that specific app — not just the usual suspects from a generic wordlist.

The response is validated against a Pydantic schema and returned as a list of relative paths (each starting with `/`).
