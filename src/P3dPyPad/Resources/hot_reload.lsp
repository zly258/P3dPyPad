;;; Plant 3D 2019 hot reload. APPLOAD once per session, then command: HR
;;; Requires DEV_PROXY already visible to the script map (one restart after first register).
(vl-load-com)

(setq *acp-last-ents* nil)
(setq *acp-rev* 0)

(defun acp-adapter-p (/ a)
  (vl-some
    '(lambda (a) (wcmatch (strcase a) "*PNP3DACPADAPTER.ARX"))
    (arx)
  )
)

(defun acp-ensure-adapter (/ full caught)
  (if (not (acp-adapter-p))
    (progn
      (setq caught (vl-catch-all-apply 'arxload (list "PnP3dACPAdapter.arx")))
      (if (vl-catch-all-error-p caught)
        (progn
          (setq full "C:/Program Files/Autodesk/AutoCAD 2019/PLNT3D/PnP3dACPAdapter.arx")
          (arxload full)
        )
      )
    )
  )
)

(defun acp-ents-after (start / e res)
  (setq res nil)
  ;; (entnext nil) is a type error. Omit the argument to get the first entity.
  (if start
    (setq e (entnext start))
    (setq e (entnext))
  )
  (while e
    (setq res (cons e res))
    (setq e (entnext e))
  )
  (reverse res)
)

(defun acp-erase-ents (ents / e)
  (foreach e ents
    (if (and e (entget e))
      (entdel e)
    )
  )
)

(defun c:HR (/ before rev-str new-ents)
  (acp-ensure-adapter)
  (acp-erase-ents *acp-last-ents*)
  (setq *acp-last-ents* nil)
  (setq *acp-rev* (1+ (if (numberp *acp-rev*) *acp-rev* 0)))
  (setq rev-str (itoa *acp-rev*))
  (setq before (entlast))
  (TESTACPSCRIPT
    "DEV_PROXY"
    "L" "600"
    "W" "200"
    "H" "300"
    "D1" "114.3"
    "D2" "60"
    "T" "12"
    "A" "90"
    "OF" "0"
    "REV" rev-str
  )
  (setq new-ents (acp-ents-after before))
  (setq *acp-last-ents* new-ents)
  (princ
    (strcat
      "\n[HR] DEV_PROXY REV=" rev-str
      "  edit dev_core.pyinc, save, run HR again."
      "  log: CustomScripts/dev_reload.log"
    )
  )
  (princ)
)

(princ "\n[HR] loaded. Command: HR")
(princ)
