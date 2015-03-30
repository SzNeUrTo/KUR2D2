from practicum import McuBoard

class PeriBoard(McuBoard):
    def setMotor(self, direction, pwm):
        self.usbWrite(0, index=direction, value=pwm)