import socket
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

HOST = '192.168.0.101'    # The remote host
PORT = 50008              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
round = 0
while True :
    sleep(0.045)
    light = b.getLight()
    state = b.getSwitch()
    s.sendall(str(light))
    print "Round %d ----> Switch state: %-8s | Light value: %d" % (round, state, light)
    round += 1
data = s.recv(1024)
s.close()
print 'Received', repr(data)