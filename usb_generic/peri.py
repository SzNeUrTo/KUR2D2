from practicum import McuBoard

RQ_SET_LED    = 0
RQ_GET_SWITCH = 1
RQ_GET_LIGHT  = 2
RQ_CMD = 99

####################################
class PeriBoard(McuBoard):

    ################################
    def setLed(self, led_no, led_val):
        self.usbWrite(RQ_SET_LED, index=led_no, value=led_val)

    def setLedValue(self, value):
        self.usbWrite(RQ_SET_LED, index=value, value=0)
        
    ################################
    def getSwitch(self):
        return self.usbRead(1, length=1)[0] == 1
    ################################
    def getLight(self):
        return self.usbRead(2, length=2)[0] + self.usbRead(2, length=2)[1] * 256

    def sendCommand(self, cmd):
        self.setLedValue(cmd)
