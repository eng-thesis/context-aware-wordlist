# context-aware-wordlist

A context-aware wordlist generator for web application penetration testing. Instead of throwing generic paths at a target, it analyzes the actual HTML content and URL of a page to generate endpoints tailored specifically to that application — its domain, tech stack, naming conventions, and implied business logic.

Powered by Google Gemini with Groq as fallback.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- A [Google Gemini API key](https://aistudio.google.com/apikey)
- A [Groq API key](https://console.groq.com/keys)

## Configuration

Create a `config.yaml` file in the root of the project:

```yaml
gemini:
  api_key: "YOUR_GEMINI_API_KEY"
  model_name: "gemini-2.5-flash-lite"

groq:
  api_key: "YOUR_GROQ_API_KEY"
  model_name: "openai/gpt-oss-120b"

broker_url: "amqp://guest:guest@rabbitmq:5672/"
```

| Field | Description |
|---|---|
| `gemini.api_key` | Your Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey) |
| `gemini.model_name` | Gemini model to use, e.g. `gemini-2.5-flash-lite`, `gemini-2.5-pro` |
| `groq.api_key` | Your Groq API key from [Groq Console](https://console.groq.com/keys) |
| `groq.model_name` | Groq model to use, e.g. `openai/gpt-oss-120b` |
| `broker_url` | RabbitMQ connection URL (only needed in worker mode) |

> **Note:** `config.yaml` contains your API keys — make sure it's in `.gitignore`.

## Usage

The tool has two modes: CLI for local use and worker for running as a containerized microservice.

### CLI mode

```bash
uv sync
uv run main.py <url> <html_content> [options]
```

#### Options

| Flag | Description |
|---|---|
| `-f` | Treat `html_content` as a path to an HTML file |
| `-n <int>` | Number of concurrent requests to send (default: 3) |
| `-o <path>` | Save output to a file instead of stdout |
| `-i <paths...>` | Input wordlists to merge with generated results |
| `-v <0-3>` | Verbosity level: 0=ERROR (default), 1=WARN, 2=INFO, 3=DEBUG |

#### Examples

```bash
# Inline HTML content
uv run main.py "https://example.com" "<html><body>...</body></html>"

# HTML from a file, save output
uv run main.py "https://example.com" page.html -f -o wordlist.txt

# Merge with existing wordlists, 5 concurrent requests
uv run main.py "https://example.com" page.html -f -n 5 -i base.txt custom.txt

# Full example with all options
uv run main.py "https://example.com" page.html -f -n 5 -o output/wordlist.txt -i base.txt -v 2
```

A common workflow is to save the page HTML with `curl` and then pass it to the generator:

```bash
curl -s https://example.com -o page.html
uv run main.py "https://example.com" page.html -f -o wordlist.txt
```

### Worker mode (Docker)

The worker listens on a RabbitMQ queue for jobs sent by an orchestrator and publishes results back.

#### Build

```bash
docker build -t context-aware-wordlist .
```

#### Run

`config.yaml` is mounted at runtime — it never gets baked into the image:

```bash
docker run --rm -v "$(pwd)/config.yaml:/app/config.yaml:ro" context-aware-wordlist

# Logging level can be set through LOG_LEVEL variable
docker run --rm -e LOG_LEVEL=DEBUG -v "$(pwd)/config.yaml:/app/config.yaml:ro" context-aware-wordlist
```

#### Message format

The worker consumes from exchange `orchestrator.tasks` (topic) with routing key `wordlist.generate` and publishes results to exchange `orchestrator.results` (direct) with routing key `task.completed`.

Incoming message:
```json
{
  "metadata": {
    "correlation_id": "uuid"
  },
  "payload": {
    "url": "https://example.com",
    "html_content": "<html>...</html>",
    "n": 3,
    "input_wordlist": ["/optional", "/existing", "/endpoints"]
  }
}
```

Result message:
```json
{
  "metadata": {
    "correlation_id": "uuid",
    "status": "success"
  },
  "payload": {
    "url": "https://example.com",
    "endpoints": ["/discovered", "/endpoints", "..."]
  }
}
```

On error, `status` is `"error"` and `payload` contains `error_message` instead.

## How it works

The tool sends the page URL and HTML content to Gemini (with automatic fallback to Groq on failure) with a system prompt instructing it to act as a penetration tester. The model analyzes the page to understand the application's domain, tech stack, and business logic, then generates a list of endpoints contextually relevant to that specific app — not just the usual suspects from a generic wordlist.

Multiple concurrent requests are sent in parallel and their results are deduplicated into a single set of endpoints. If input wordlists are provided, they are merged into the final output as well.

The response is validated against a Pydantic schema and each endpoint is a relative path starting with `/`.
