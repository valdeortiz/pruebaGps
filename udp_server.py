import asyncio

from gps import check_gps
# Get a reference to the event loop as we plan to use
# low-level APIs
loop = asyncio.get_event_loop()

class UdpServer:
    def connection_made(self, transport):
        
        self.time_set = False
        self.coords = {
            "lon": 0.0,
            "lat": 0.0,
            "gps_time": 0,
            "parada": ""
        }

        # coroutine for counts pending verifications
        
        loop.create_task(check_gps(self.coords))

    
if __name__ == '__main__':
    listen = loop.create_datagram_endpoint(
        lambda: UdpServer(),
        local_addr=('0.0.0.0', 12100))
    transport, protocol = loop.run_until_complete(listen)

    try:
        # Serve for 24 hour.
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    transport.close()
    loop.close()
