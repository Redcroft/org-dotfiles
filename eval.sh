#!/bin/sh

echo "Tangling file: " "$@"

emacs -Q --batch --eval "
  (progn
    (require 'ob-tangle)
    (require 'ob-shell)
    (setq org-confirm-babel-evaluate nil)
    (dolist (file command-line-args-left)
      (with-current-buffer (find-file-noselect file)
        (org-babel-tangle))))" "$@"
