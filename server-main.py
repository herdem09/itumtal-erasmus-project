import time

# region variables

communication_password="47T9e#$wV!5r@z&Y8p)2Jk_h+L/d=g?a-mX@#p35_q9-c7&8+Lg/d=g?a"
communication_password_input=""

temperature=24
brightness=True
right_password=2019
password_input=0
right_card="12das"
card_input=""
open_door=False
close_door=False
face_recognition=False

open_door_input=False

temperature_auto=True
brightness_auto=True

temperature_auto_input=True
brightness_auto_input=True

fan=False
window=False
heater=False

fan_input=False
window_input=False
heater_input=False

light=False
curtain=True

light_input=False
curtain_input=False

first_time= 0.0
now= time.time()
timer= now-first_time

# endregion

while True:

    # region timer

    now = time.time()
    timer = now - first_time

    # endregion

    # region check auto

    if brightness_auto_input==True:
        brightness_auto=True
        print("brightness_auto=True")
    else:
        brightness_auto=False
        print("brightness_auto=False")

    if temperature_auto_input==True:
        temperature_auto=True
        print("temperature_auto=True")
    else:
        temperature_auto=False
        print("temperature_auto=False")

    # endregion

    # region temperature

    if temperature_auto==True:
        if temperature<=21:
            heater=True
            window = False
            fan = False
            print("heater=True            window = False            fan = False")
        elif temperature<=24:
            heater=False
            window = False
            fan = False
            print("heater=False            window = False            fan = False")
        elif temperature<=29:
            heater = False
            window = True
            fan = False
            print("heater=False            window = True            fan = False")
        else:
            heater = False
            window = True
            fan = True
            print("heater=False            window = True            fan = True")
    else:
        if fan_input == True:
            fan = True
        else:
            fan = False

        if fan_input==True:
            fan=True
        else:
            Fan=False

        if heater_input==True:
            heater=True
        else:
            heater=False

    # endregion

    # region brightness

    if brightness_auto==True:
        if brightness == True:
            curtain = False
            light = False
            print("curtain = False            light = False")
        else:
            curtain=True
            light = True
            print("curtain = True            light = True")
    else:
        if light_input==True:
            light=True
        else:
            light=False
        if curtain_input==True:
            curtain=True
        else:
            curtain=False

    # endregion

    # region door

    if open_door_input==True:
        first_time=time.time()
        open_door=True
        open_door_input=False
        print("open_door=True")

    if timer>15:
        open_door=False
        print("open_door=False")

    if close_door==True:
        open_door=False
        close_door=False

    if card_input==right_card or password_input == right_password or face_recognition==True:
        first_time=time.time()
        open_door=True
        open_door_input=False
        print("open_door=True")

    # endregion//

