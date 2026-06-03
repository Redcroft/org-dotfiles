#!/bin/sh
# File: tangle-all.sh
# Description: Script to tangle all README.org files in the dotfiles repository (POSIX compliant)

set -eu

# Get the directory where this script is located (should be dotfiles root)
SCRIPT_PATH="$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")"
DOTFILES_ROOT="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
cd "$DOTFILES_ROOT"

echo "=== Tangling all README.org files in $DOTFILES_ROOT ==="

# Find all README.org files and tangle them in parallel
# Use xargs -P to run multiple emacs instances at once
# nproc determines the number of available CPU cores
NUM_CORES=$(nproc 2>/dev/null || echo 4)

find "$DOTFILES_ROOT" -name "README.org" -type f -print0 | xargs -0 -I {} -P "$NUM_CORES" sh -c "
    TMP_LOG=\$(mktemp)
    if ! emacs --batch --eval \"(require 'org)\" \
          --eval \"(require 'ob-shell)\" \
          --eval \"(setq org-confirm-babel-evaluate nil)\" \
          --eval \"(org-babel-tangle-file \\\"{}\\\")\" > \"\$TMP_LOG\" 2>&1; then
        echo 'FAILED: {}'
        cat \"\$TMP_LOG\"
    fi
    rm -f \"\$TMP_LOG\"
"

echo "=== Tangling complete ==="
