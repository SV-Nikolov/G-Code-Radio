; G-Code Radio - 3D Printer Music Player
; Generated on 2025-12-07 00:51:58
; Title: Test
;
; SAFETY NOTICE:
; - This is a movement-only file (NO EXTRUSION)
; - NO heating commands (bed or hotend)
; - Movement limited to printer bounds
; - Safe for Moment S1 (2014) printer
;

; Reset all systems
G90                                    ; Set to absolute positioning
G28                                    ; Home all axes
G92 X100 Y100 Z100                     ; Set home position

; Disable motors after homing
M18                                    ; Disable steppers (optional)
G04 P1000                              ; Wait 1 second

; Start movement sequence
G1 X110.00 F1000
G1 Y105.00 F1000

; End of movement sequence
G28                                    ; Return home
M18                                    ; Disable steppers
; Song complete!
