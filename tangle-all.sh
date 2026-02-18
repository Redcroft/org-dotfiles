#!/bin/sh
# File: tangle-all.sh
# Description: Script to tangle all README.org files in the dotfiles repository (POSIX compliant)

set -eu

# Get the directory where this script is located (should be dotfiles root)
SCRIPT_PATH="$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")"
DOTFILES_ROOT="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
cd "$DOTFILES_ROOT"

echo "=== Tangling all README.org files in $DOTFILES_ROOT ==="

# Find all README.org files and tangle them
find "$DOTFILES_ROOT" -name "README.org" -type f | while read -r org_file; do
    echo "Tangling: $org_file"
    emacs --batch --eval "(require 'org)" \
	  --eval "(require 'ob-shell)" \
	  --eval "(setq org-confirm-babel-evaluate nil)" \
	  --eval "(org-babel-tangle-file \"$org_file\")"
done

echo "=== Tangling complete ==="
echo "Manually Add FREETYPE_PROPERTIES=\"cff:no-stem-darkening=0 autofitter:no-stem-darkening=0\" to /etc/environment"
