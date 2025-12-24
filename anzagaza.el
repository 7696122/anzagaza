;;; anzagaza.el --- 버스 한적한 시간대 추천 -*- lexical-binding: t -*-

;;; Commentary:
;; 421번 보광동주민센터 → 매봉역 혼잡도 조회

;;; Code:

(require 'url)

(defvar anzagaza-api-url "http://openapi.seoul.go.kr:8088/sample/json/CardBusTimeNew/1/5/202411/421/"
  "서울시 버스 승하차 API URL.")

(defvar anzagaza-data
  '((morning . ((6 . 142) (7 . 994) (8 . 1303) (9 . 1219) (10 . 1190)))
    (evening . ((17 . 640) (18 . 798) (19 . 698) (20 . 490) (21 . 507))))
  "시간대별 승하차 인원 데이터 (캐시).")

(defvar anzagaza-mode-line ""
  "모드라인 표시 문자열.")

(defvar anzagaza-alert-timer nil
  "알림 타이머.")

;;; 1. 알림 기능
(defun anzagaza-alert ()
  "추천 시간에 알림 표시."
  (let ((hour (string-to-number (format-time-string "%H"))))
    (cond
     ((= hour 5) (message "🚌 앉아가자: 06시대 출근 추천! (한적)"))
     ((= hour 19) (message "🚌 앉아가자: 20시 이후 퇴근 추천! (한적)")))))

(defun anzagaza-enable-alert ()
  "매시 정각 알림 활성화."
  (interactive)
  (when anzagaza-alert-timer (cancel-timer anzagaza-alert-timer))
  (setq anzagaza-alert-timer
        (run-at-time "00:00" 3600 #'anzagaza-alert))
  (message "앉아가자 알림 활성화"))

(defun anzagaza-disable-alert ()
  "알림 비활성화."
  (interactive)
  (when anzagaza-alert-timer
    (cancel-timer anzagaza-alert-timer)
    (setq anzagaza-alert-timer nil))
  (message "앉아가자 알림 비활성화"))

;;; 2. 모드라인
(defun anzagaza-get-status ()
  "현재 혼잡도 상태 반환."
  (let* ((hour (string-to-number (format-time-string "%H")))
         (data (if (< hour 12)
                   (alist-get 'morning anzagaza-data)
                 (alist-get 'evening anzagaza-data)))
         (count (alist-get hour data)))
    (if count
        (if (< count 600) "⭐한적" "🔴혼잡")
      "")))

(defun anzagaza-update-mode-line ()
  "모드라인 업데이트."
  (setq anzagaza-mode-line
        (let ((status (anzagaza-get-status)))
          (if (string-empty-p status) ""
            (format " [🚌%s]" status)))))

(define-minor-mode anzagaza-mode-line-mode
  "모드라인에 버스 혼잡도 표시."
  :global t
  :lighter ""
  (if anzagaza-mode-line-mode
      (progn
        (add-to-list 'mode-line-misc-info '(:eval anzagaza-mode-line))
        (run-at-time nil 60 #'anzagaza-update-mode-line)
        (anzagaza-update-mode-line))
    (setq mode-line-misc-info
          (delete '(:eval anzagaza-mode-line) mode-line-misc-info))))

;;; 3. Org 연동
(defun anzagaza-org-insert ()
  "Org 일정에 추천 시간 추가."
  (interactive)
  (let ((date (org-read-date nil nil nil "날짜 선택: ")))
    (insert (format "* 출근 [%s 06:00]\n" date))
    (insert "  - 421번 보광동주민센터 06시대 추천 (한적)\n")
    (insert (format "* 퇴근 [%s 20:00]\n" date))
    (insert "  - 421번 보광동주민센터 20시 이후 추천 (한적)\n")))

;;; 메인 함수
(defun anzagaza-fetch-data ()
  "API에서 실시간 데이터 가져오기."
  (interactive)
  (url-retrieve anzagaza-api-url #'anzagaza--parse-response nil t))

(defun anzagaza--parse-response (_status)
  "API 응답 파싱."
  (goto-char url-http-end-of-headers)
  (let* ((json-object-type 'alist)
         (data (json-read))
         (rows (alist-get 'row (alist-get 'CardBusTimeNew data))))
    (dolist (row rows)
      (when (string-match "보광동주민센터" (alist-get 'SBWY_STNS_NM row))
        (message "보광동주민센터 06시 승차: %.0f명"
                 (alist-get 'HR_6_GET_ON_TNOPE row))))))

(defun anzagaza ()
  "버스 혼잡도 추천 시간 표시."
  (interactive)
  (let ((buf (get-buffer-create "*앉아가자*"))
        (hour (string-to-number (format-time-string "%H"))))
    (with-current-buffer buf
      (erase-buffer)
      (insert "🚌 앉아가자 - 421번 보광동주민센터\n")
      (insert (format "현재 시간: %s\n\n" (format-time-string "%H:%M")))
      (if (< hour 12)
          (progn
            (insert "━━━ 출근 추천: 06시대 ━━━\n")
            (insert "(08시 대비 1/9 혼잡도)\n\n")
            (insert "시간 | 승차\n")
            (insert "─────┼─────\n")
            (dolist (d (alist-get 'morning anzagaza-data))
              (insert (format " %02d시 | %4d %s%s\n"
                              (car d) (cdr d)
                              (if (< (cdr d) 500) "⭐" "🔴")
                              (if (= (car d) hour) " ← 현재" "")))))
        (progn
          (insert "━━━ 퇴근 추천: 20시 이후 ━━━\n")
          (insert "(18시 대비 60% 혼잡도)\n\n")
          (insert "시간 | 하차\n")
          (insert "─────┼─────\n")
          (dolist (d (alist-get 'evening anzagaza-data))
            (insert (format " %02d시 | %4d %s%s\n"
                            (car d) (cdr d)
                            (if (< (cdr d) 600) "⭐" "🔴")
                            (if (= (car d) hour) " ← 현재" ""))))))
      (insert "\n[r] 새로고침  [q] 닫기")
      (local-set-key "r" #'anzagaza)
      (local-set-key "q" #'quit-window))
    (pop-to-buffer buf)))

(provide 'anzagaza)
;;; anzagaza.el ends here
