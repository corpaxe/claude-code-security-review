"""
Constants and configuration values for ClaudeCode.
"""

import os

# Model family overrides for LiteLLM proxy compatibility
# These environment variables are used by Claude Code CLI internally to determine which models
# to use for different operations (validation, thinking, optimization, etc.)
# When set, they override Claude Code's default model choices, enabling LiteLLM proxies
# to map model families to custom backend names
# Note: These are primarily for the Claude CLI subprocess, not the Python wrapper logic
DEFAULT_HAIKU_MODEL = os.environ.get('ANTHROPIC_DEFAULT_HAIKU_MODEL') or 'claude-3-5-haiku-20241022'
DEFAULT_SONNET_MODEL = os.environ.get('ANTHROPIC_DEFAULT_SONNET_MODEL') or 'claude-sonnet-4-5-20250514'
DEFAULT_OPUS_MODEL = os.environ.get('ANTHROPIC_DEFAULT_OPUS_MODEL') or 'claude-opus-4-1-20250805'

# API Configuration
# Main analysis model - defaults to Opus model family
# Can be overridden via CLAUDE_MODEL environment variable (set by claude-model input)
DEFAULT_CLAUDE_MODEL = os.environ.get('CLAUDE_MODEL') or DEFAULT_OPUS_MODEL
DEFAULT_TIMEOUT_SECONDS = 180  # 3 minutes
DEFAULT_MAX_RETRIES = 3
RATE_LIMIT_BACKOFF_MAX = 30  # Maximum backoff time for rate limits

# Token Limits
PROMPT_TOKEN_LIMIT = 16384  # 16k tokens max for claude-opus-4

# Exit Codes
EXIT_SUCCESS = 0
EXIT_GENERAL_ERROR = 1
EXIT_CONFIGURATION_ERROR = 2

# Subprocess Configuration
SUBPROCESS_TIMEOUT = 1200  # 20 minutes for Claude Code execution

