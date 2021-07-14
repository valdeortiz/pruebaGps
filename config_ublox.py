from serial import Serial, SerialException, SerialTimeoutException

from pyubx2 import UBXMessage, SET, UBX_MSGIDS
import pyubx2.exceptions as ube

class UBXSetter:
    """
    UBXSetter class.
    """

    def __init__(self, port, baudrate, timeout=5):
        """
        Constructor.
        """

        self._serial_object = None
        self._connected = False
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout

    def connect(self):
        """
        Open serial connection.
        """
        try:
            self._serial_object = Serial(
                self._port, self._baudrate, timeout=self._timeout
            )
            self._connected = True
        except (SerialException, SerialTimeoutException) as err:
            print("ERorr al iniciar el serial port y conectar")
            print(err)
            pass

    def disconnect(self):
        """
        Close serial connection.
        """

        if self._connected and self._serial_object:
            try:
                self._serial_object.close()
            except (SerialException, SerialTimeoutException) as err:
                pass
        self._connected = False

    def _send(self, data):
        """
        Send data to serial connection.
        """

        self._serial_object.write(data)

    def send_configuration(self, config):
        """
        Creates a series of CFG-MSG configuration messages and
        sends them to the receiver.
        """

        try:
            msgs = []

            # compile all the UBX-NAV config message types
            for key, val in UBX_MSGIDS.items():
                if val[0:3] == "NAV":
                    msgs.append(key)

            # send each UBX-NAV config message in turn
            for msgtype in msgs:
                payload = msgtype + config
                msg = UBXMessage("CFG", "CFG-MSG", SET, payload=payload)
                self._send(msg.serialize())
        except (ube.UBXMessageError, ube.UBXTypeError, ube.UBXParseError) as err:
            pass
