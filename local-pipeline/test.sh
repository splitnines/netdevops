#!/usr/bin/env bash

logger() {
    local prefix=${1:-cicd}
    ts=$(date '+%Y-%m-%d %H:%M:%S')
    printf '%s [%s-commit]:' "$ts" "$prefix"
}

echo "$(logger "post") testing..."
