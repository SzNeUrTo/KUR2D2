from practicum import findDevices
from peri import PeriBoard
from time import sleep

devs = findDevices()

if len(devs) == 0:
    print "*** No MCU board found."
    exit(1)

b = PeriBoard(devs[0])
print "*** MCU board found"
print "*** Device manufacturer: %s" % b.getVendorName()
print "*** Device name: %s" % b.getDeviceName()

count = 0
while True:
    sleep(1)
    b.setLedValue(count)
    sw = b.getSwitch()
    light = b.getLight()

    if sw is True:
        state = "PRESSED"
    else:
        state = "RELEASED"

    print "LEDs set to %d | Switch state: %-8s | Light value: %d" % (
            count, state, light)

    count = (count + 1) % 8

