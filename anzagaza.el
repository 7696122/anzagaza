;;; anzagaza.el --- 버스 한적한 시간대 추천 -*- lexical-binding: t -*-

;;; Commentary:
;; 421번 보광동주민센터 → 매봉역 혼잡도 조회

;;; Code:

(defvar anzagaza-data
  '((morning . ((6 . 142) (7 . 994) (8 . 1303) (9 . 1219) (10 . 1190)))
    (evening . ((17 . 640) (18 . 798) (19 . 698) (20 . 490) (21 . 507))))
  "시간대별 승하차 인원 데이터.")

(defun anzagaza ()
  "버스 혼잡도 추천 시간 표시."
  (interactive)
  (let ((buf (get-buffer-create "*앉아가자*")))
    (with-current-buffer buf
      (erase-buffer)
      (insert "🚌 앉아가자 - 421번 보광동주민센터\n\n")
      (insert "━━━ 출근 추천: 06시대 ━━━\n")
      (insert "(08시 대비 1/9 혼잡도)\n\n")
      (insert "시간 | 승차\n")
      (insert "─────┼─────\n")
      (dolist (d (alist-get 'morning anzagaza-data))
        (insert (format " %02d시 | %4d %s\n"
                        (car d) (cdr d)
                        (if (< (cdr d) 500) "⭐" "🔴"))))
      (insert "\n━━━ 퇴근 추천: 20시 이후 ━━━\n")
      (insert "(18시 대비 60% 혼잡도)\n\n")
      (insert "시간 | 하차\n")
      (insert "─────┼─────\n")
      (dolist (d (alist-get 'evening anzagaza-data))
        (insert (format " %02d시 | %4d %s\n"
                        (car d) (cdr d)
                        (if (< (cdr d) 600) "⭐" "🔴")))))
    (pop-to-buffer buf)))

(provide 'anzagaza)
;;; anzagaza.el ends here
