# Claude Code Security Reviewer

An AI-powered security review GitHub Action using Claude to analyze code changes for security vulnerabilities. This action provides intelligent, context-aware security analysis for pull requests using Anthropic's Claude Code tool for deep semantic security analysis. See our blog post [here](https://www.anthropic.com/news/automate-security-reviews-with-claude-code) for more details.

## Features

- **AI-Powered Analysis**: Uses Claude's advanced reasoning to detect security vulnerabilities with deep semantic understanding
- **Diff-Aware Scanning**: For PRs, only analyzes changed files
- **PR Comments**: Automatically comments on PRs with security findings
- **Contextual Understanding**: Goes beyond pattern matching to understand code semantics
- **Language Agnostic**: Works with any programming language
- **False Positive Filtering**: Advanced filtering to reduce noise and focus on real vulnerabilities

## Quick Start

Add this to your repository's `.github/workflows/security.yml`:

```yaml
name: Security Review

permissions:
  pull-requests: write  # Needed for leaving PR comments
  contents: read

on:
  pull_request:

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha || github.sha }}
          fetch-depth: 2

      - uses: anthropics/claude-code-security-review@main
        with:
          claude-api-key: ${{ secrets.CLAUDE_API_KEY }}
          comment-pr: true
```

**Customize the model (optional):**

```yaml
# Use Sonnet for faster/cheaper analysis (default is Opus)
- uses: anthropics/claude-code-security-review@main
  with:
    claude-api-key: ${{ secrets.CLAUDE_API_KEY }}
    claude-model: claude-sonnet-4-5-20250514
    comment-pr: true

# With LiteLLM proxy - use the proxy's Sonnet mapping
- uses: anthropics/claude-code-security-review@main
  with:
    claude-api-key: ${{ secrets.LITELLM_API_KEY }}
    claude-base-url: ${{ vars.LITELLM_BASE_URL }}
    claude-model: ${{ vars.ANTHROPIC_DEFAULT_SONNET_MODEL }}
    comment-pr: true
```

## Security Considerations

This action is not hardened against prompt injection attacks and should only be used to review trusted PRs. We recommend [configuring your repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository#controlling-changes-from-forks-to-workflows-in-public-repositories) to use the "Require approval for all external contributors" option to ensure workflows only run after a maintainer has reviewed the PR.

## Configuration Options

### Action Inputs

| Input | Description | Default | Required |
|-------|-------------|---------|----------|
| `claude-api-key` | Anthropic Claude API key for security analysis. <br>*Note*: This API key needs to be enabled for both the Claude API and Claude Code usage. | None | Yes |
| `claude-base-url` | Custom Anthropic API base URL (e.g., for LiteLLM proxy). Defaults to official Anthropic API endpoint. | None | No |
| `anthropic-default-haiku-model` | Override Claude Code's internal Haiku model. Used transparently by Claude Code CLI for operations requiring fast/cheap models. Critical for LiteLLM proxies with custom model mappings. | `claude-3-5-haiku-20241022` | No |
| `anthropic-default-sonnet-model` | Override Claude Code's internal Sonnet model. Used transparently by Claude Code CLI for balanced performance operations. Critical for LiteLLM proxies with custom model mappings. | `claude-sonnet-4-5-20250514` | No |
| `anthropic-default-opus-model` | Override Claude Code's internal Opus model. Used transparently by Claude Code CLI for complex reasoning operations. Critical for LiteLLM proxies with custom model mappings. | `claude-opus-4-1-20250805` | No |
| `comment-pr` | Whether to comment on PRs with findings | `true` | No |
| `upload-results` | Whether to upload results as artifacts | `true` | No |
| `exclude-directories` | Comma-separated list of directories to exclude from scanning | None | No |
| `claude-model` | Claude [model name](https://docs.anthropic.com/en/docs/about-claude/models/overview#model-names) to use for the main security analysis. Controls which model Claude Code CLI uses for scanning. Defaults to Opus 4.1 for maximum analysis depth. **Note**: This is different from the `anthropic-default-*-model` inputs, which control Claude Code's internal operations. | `claude-opus-4-1-20250805` | No |
| `claudecode-timeout` | Timeout for ClaudeCode analysis in minutes | `20` | No |
| `run-every-commit` | Run ClaudeCode on every commit (skips cache check). Warning: May increase false positives on PRs with many commits. | `false` | No |
| `false-positive-filtering-instructions` | Path to custom false positive filtering instructions text file | None | No |
| `custom-security-scan-instructions` | Path to custom security scan instructions text file to append to audit prompt | None | No |

### Using with LiteLLM Proxy

To use this action with a LiteLLM proxy or custom Anthropic-compatible endpoint:

```yaml
- uses: anthropics/claude-code-security-review@main
  with:
    claude-api-key: ${{ secrets.LITELLM_API_KEY }}
    claude-base-url: ${{ vars.LITELLM_BASE_URL }}
    comment-pr: true
```

#### Model Family Overrides

Claude Code CLI uses different models internally for various operations (validation, thinking tokens, cost optimization). When using a LiteLLM proxy, these internal model names need to be overridden to match your proxy's model mappings:

```yaml
- uses: anthropics/claude-code-security-review@main
  with:
    claude-api-key: ${{ secrets.LITELLM_API_KEY }}
    claude-base-url: ${{ vars.LITELLM_BASE_URL }}
    anthropic-default-haiku-model: ${{ vars.ANTHROPIC_DEFAULT_HAIKU_MODEL }}
    anthropic-default-sonnet-model: ${{ vars.ANTHROPIC_DEFAULT_SONNET_MODEL }}
    anthropic-default-opus-model: ${{ vars.ANTHROPIC_DEFAULT_OPUS_MODEL }}
    comment-pr: true
```

**How it works:**
- These environment variables are passed to the Claude Code CLI subprocess
- Claude Code reads them transparently and uses them for its internal operations
- Your LiteLLM proxy receives the overridden model names instead of Anthropic's defaults
- This allows you to route different model families to different backends or use custom model mappings

**Example LiteLLM proxy scenario:**
```yaml
vars:
  LITELLM_BASE_URL: 'https://proxy.company.com/v1'
  # Map Claude model families to your proxy's model names
  ANTHROPIC_DEFAULT_HAIKU_MODEL: 'company/fast-model'
  ANTHROPIC_DEFAULT_SONNET_MODEL: 'company/balanced-model'
  ANTHROPIC_DEFAULT_OPUS_MODEL: 'company/premium-model'
```

**Important**: When using a custom base URL, ensure:
- Your proxy endpoint is compatible with the Anthropic Messages API format
- The `claude-api-key` matches the authentication expected by your proxy
- Your proxy supports the Claude model specified in `claude-model`
- If using model family overrides, ensure the override model names exist in your proxy configuration and are properly mapped

### Action Outputs

| Output | Description |
|--------|-------------|
| `findings-count` | Total number of security findings |
| `results-file` | Path to the results JSON file |

### Understanding Model Configuration

This action supports two types of model configuration:

1. **Main Analysis Model** (`claude-model` input):
   - Controls which model performs the security analysis
   - Directly passed to Claude Code CLI via `--model` flag
   - Defaults to Opus 4.1 for maximum analysis depth
   - Can be set to Sonnet for balance, Haiku for speed, or even use `${{ vars.ANTHROPIC_DEFAULT_SONNET_MODEL }}` for proxy compatibility
   - Example: `claude-model: claude-sonnet-4-5-20250514`

2. **Claude Code Internal Models** (`anthropic-default-*-model` inputs):
   - Controls which models Claude Code uses for its internal operations
   - Only needed when using LiteLLM proxies with custom model mappings
   - Claude Code makes these model choices transparently during execution
   - Most users can ignore these unless using a proxy

**Example - Cost Optimization:**
```yaml
# Default is Opus. Use Sonnet for balanced cost/performance:
claude-model: claude-sonnet-4-5-20250514

# Claude Code still uses appropriate models internally (Haiku for validation, etc.)
# No need to set anthropic-default-*-model unless using a proxy
```

**Example - Using Proxy Model Variables:**
```yaml
# Use your LiteLLM proxy's Sonnet mapping for the main analysis:
claude-model: ${{ vars.ANTHROPIC_DEFAULT_SONNET_MODEL }}

# This ensures the main analysis model matches your proxy's Sonnet mapping
```

## How It Works

### Architecture

```
claudecode/
├── github_action_audit.py  # Main audit script for GitHub Actions
├── prompts.py              # Security audit prompt templates
├── findings_filter.py      # False positive filtering logic
├── claude_api_client.py    # Claude API client for false positive filtering
├── json_parser.py          # Robust JSON parsing utilities
├── requirements.txt        # Python dependencies
├── test_*.py               # Test suites
└── evals/                  # Eval tooling to test CC on arbitrary PRs
```

### Workflow

1. **PR Analysis**: When a pull request is opened, Claude analyzes the diff to understand what changed
2. **Contextual Review**: Claude examines the code changes in context, understanding the purpose and potential security implications
3. **Finding Generation**: Security issues are identified with detailed explanations, severity ratings, and remediation guidance
4. **False Positive Filtering**: Advanced filtering removes low-impact or false positive prone findings to reduce noise
5. **PR Comments**: Findings are posted as review comments on the specific lines of code

## Security Analysis Capabilities

### Types of Vulnerabilities Detected

- **Injection Attacks**: SQL injection, command injection, LDAP injection, XPath injection, NoSQL injection, XXE
- **Authentication & Authorization**: Broken authentication, privilege escalation, insecure direct object references, bypass logic, session flaws
- **Data Exposure**: Hardcoded secrets, sensitive data logging, information disclosure, PII handling violations
- **Cryptographic Issues**: Weak algorithms, improper key management, insecure random number generation
- **Input Validation**: Missing validation, improper sanitization, buffer overflows
- **Business Logic Flaws**: Race conditions, time-of-check-time-of-use (TOCTOU) issues
- **Configuration Security**: Insecure defaults, missing security headers, permissive CORS
- **Supply Chain**: Vulnerable dependencies, typosquatting risks
- **Code Execution**: RCE via deserialization, pickle injection, eval injection
- **Cross-Site Scripting (XSS)**: Reflected, stored, and DOM-based XSS

### False Positive Filtering

The tool automatically excludes a variety of low-impact and false positive prone findings to focus on high-impact vulnerabilities:
- Denial of Service vulnerabilities
- Rate limiting concerns
- Memory/CPU exhaustion issues
- Generic input validation without proven impact
- Open redirect vulnerabilities

The false positive filtering can also be tuned as needed for a given project's security goals.

### Benefits Over Traditional SAST

- **Contextual Understanding**: Understands code semantics and intent, not just patterns
- **Lower False Positives**: AI-powered analysis reduces noise by understanding when code is actually vulnerable
- **Detailed Explanations**: Provides clear explanations of why something is a vulnerability and how to fix it
- **Adaptive Learning**: Can be customized with organization-specific security requirements

## Installation & Setup

### GitHub Actions

Follow the Quick Start guide above. The action handles all dependencies automatically.

### Local Development

To run the security scanner locally against a specific PR, see the [evaluation framework documentation](claudecode/evals/README.md).

<a id="security-review-slash-command"></a>

## Claude Code Integration: /security-review Command 

By default, Claude Code ships a `/security-review` [slash command](https://docs.anthropic.com/en/docs/claude-code/slash-commands) that provides the same security analysis capabilities as the GitHub Action workflow, but integrated directly into your Claude Code development environment. To use this, simply run `/security-review` to perform a comprehensive security review of all pending changes.

### Customizing the Command

The default `/security-review` command is designed to work well in most cases, but it can also be customized based on your specific security needs. To do so: 

1. Copy the [`security-review.md`](https://github.com/anthropics/claude-code-security-review/blob/main/.claude/commands/security-review.md?plain=1) file from this repository to your project's `.claude/commands/` folder. 
2. Edit `security-review.md` to customize the security analysis. For example, you could add additional organization-specific directions to the false positive filtering instructions. 

## Custom Scanning Configuration

It is also possible to configure custom scanning and false positive filtering instructions, see the [`docs/`](docs/) folder for more details.  

## Testing

Run the test suite to validate functionality:

```bash
cd claude-code-security-review
# Run all tests
pytest claudecode -v
```

## Support

For issues or questions:
- Open an issue in this repository
- Check the [GitHub Actions logs](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/viewing-workflow-run-history) for debugging information

## License

MIT License - see [LICENSE](LICENSE) file for details.
