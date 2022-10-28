from gpiozero import Button, LED
import time

button = Button(2)
green = LED(3)
red = LED(4)

while True:
        if button.is_pressed:
                red.off()
                green.on()
        else:
                green.off()
                red.on()

