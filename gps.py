import asyncio
from pyubx2 import UBXReader, VALCKSUM
from serial import Serial
import time
from io import BufferedReader
from config_ublox import UBXSetter

from subprocess import Popen, PIPE, CalledProcessError
import os
from datetime import datetime

async def check_gps(transport, coords = {}):
    PORT = f"/dev/ttyACM1"
    BAUDRATE = 115200
    TIMEOUT = 5

    # each of 6 config bytes corresponds to a receiver port
    # the UART and USB ports are bytes 2, 3 and 4
    ON = b"\x01\x01\x01\x01\x01\x00"
    OFF = b"\x00\x00\x00\x00\x00\x00"

    while True:
        try:
            print(f"######## UNX start configuration ########")
            ubs = UBXSetter(PORT, BAUDRATE, TIMEOUT)
            ubs.connect()
            ubs.send_configuration(ON)
            ubs.disconnect()
            print("UBX config finish")
        except Exception as e:
            print(f"UBX config error {e}")
            await asyncio.sleep(10)
            continue
        try:
            print(f"Starting Setting UP serial")
            stream = Serial(PORT, BAUDRATE, timeout=TIMEOUT)
            ubr = UBXReader(BufferedReader(stream), validate=VALCKSUM)
        except Exception as e:
            print(f"UBX error seting up serial {e}")
            await asyncio.sleep(10)
            continue
    
        while True:
            try:
                (raw, msg) = ubr.read()
                await asyncio.sleep(1)
                if raw:
                    msg = UBXReader.parse(raw)
                    print(f"msg identity: {msg.identity}")
                    if msg.identity == "NAV-POSLLH":
                        lat = (msg.lat / 10 ** 7)
                        lon = (msg.lon / 10 ** 7)
                        # parada = _in_geocerca(lat, lon)
                        coords["lat"] = lat
                        coords["lon"] = lon
                        coords["gps_time"] = int(time.time() * 1000)
                        # coords["parada"] = parada
                        print(f"gps info: {coords}")
                        day = datetime.now().day
                        if not os.path.exists('geocerca.txt'):
                            execute(f"echo {day}-{lat}-{lon} >> geocerca.txt")
                        else:
                            with open('geocerca.txt', 'r') as f:
                                var = f.readline().split('-')[0]
                                print(var, end='VAriable')
                                if var == day:
                                    execute(f"echo {day} - {lat} - {lon} >> geocerca.txt")
                                else:
                                    execute("rm geocerca.txt")
                        if(lat > -24.0 or lat < -26.0 or lon < -59 or lon > -57):
                            break
            except Exception as e:
                print(f"raw data parsing error : {e}")
                await asyncio.sleep(5)
                break
    


def execute(cmd):
    """Execute a unix command with subprocess"""
    p = Popen(
        cmd,
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE
    )
    out, err = p.communicate()
    if not err:
        return out.decode()
    return err.decode()