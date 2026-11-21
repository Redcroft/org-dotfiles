package tangle

import "core:fmt"
import "core:os"
import "core:strings"

main :: proc() {
    w := os.walker_create(".")
    defer os.walker_destroy(&w)

    for info in os.walker_walk(&w) {
	if _, walker_err := os.walker_error(&w); walker_err != nil {
	    fmt.eprintln("Unable to walk directory")
	    break
	}
	if info.type == .Regular {
	    if strings.to_lower(info.name) == "readme.org" {
		tangle_file(info.fullpath)
	    }
	}
    }
}

tangle_file :: proc(path: string) {
    tangle := fmt.tprintf(
	`(let ((tmp (make-temp-file
	(expand-file-name "tangle-" "~/.cache/")
	nil ".org")))
	(unwind-protect
	(progn
	(with-temp-buffer
        (insert-file-contents "%s")
        (goto-char (point-min))
        (while (search-forward "sudo" nil t)
        (replace-match "doas" t t))
        (write-region (point-min) (point-max) tmp nil 'silent))
        (let ((files (org-babel-tangle-file tmp)))
        (princ "Tangle completed for %s\n"))
	(when (file-exists-p tmp)
	(delete-file tmp)))))`, path, path
    )
    
    cmd:[]string = {
	"emacs", "-batch",
	"--eval", "(require 'org)",
	"--eval", "(require 'ob-shell)",
	"--eval", "(setq org-confirm-babel-evaluate nil)",
	"--eval", tangle
    }
    
    desc := os.Process_Desc {
		command = cmd[:],
    }
    state, stdout, stderr, err := os.process_exec({ command = cmd[:] }, allocator = context.temp_allocator)
    if err != nil {
        fmt.eprintfln("Failed to tangle %s", path)
    }
    fmt.print(string(stdout))
}
