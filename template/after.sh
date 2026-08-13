#!/usr/bin/env bash

echo "Waiting for GitHub Copilot to open port ${port}..."
if ! wait_until_port_used "${host}:${port}" 60; then
  echo "GitHub Copilot did not open port ${port} within 60 seconds." >&2
  clean_up 1
fi
