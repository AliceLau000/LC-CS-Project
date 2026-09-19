is_calibrated = False
risk = 0
baseline_temp = 0
baseline_light = 0

def on_log_full():
    basic.show_icon(IconNames.NO)
datalogger.on_log_full(on_log_full)

def on_button_pressed_a():
    global is_calibrated
    datalogger.delete_log()
    is_calibrated = True
    basic.show_icon(IconNames.YES)
    basic.pause(500)
    basic.clear_screen()
input.on_button_pressed(Button.A, on_button_pressed_a)

def on_forever():
    global risk, baseline_temp, baseline_light
    if is_calibrated:
        datalogger.log(datalogger.create_cv("temp", input.temperature()),
            datalogger.create_cv("Light", input.light_level()))
        datalogger.mirror_to_serial(True)
        risk = 0
        baseline_temp = input.temperature()
        baseline_light = input.light_level()
        if baseline_temp >= 28:
            risk += 7
        elif baseline_temp >= 20:
            risk += 5
        elif baseline_temp >= 10:
            risk += 3
        else:
            risk += 1
        if baseline_light >= 200:
            risk += 4
        elif baseline_light >= 175:
            risk += 3
        elif baseline_light >= 100:
            risk += 2
        else:
            risk += 1
        if risk >= 9:
            basic.show_leds("""
                # . # . #
                # # # # #
                # # # # #
                # # # # #
                . # # # .
                """)
        elif risk >= 5:
            basic.show_icon(IconNames.SMALL_HEART)
        else:
            basic.show_icon(IconNames.HAPPY)
        basic.pause(2000)
basic.forever(on_forever)
