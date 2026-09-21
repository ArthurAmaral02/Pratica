import rpyc
import socket
import subprocess


class Agent(rpyc.Service):

    def exposed_status(self):
        return "OK"

    def exposed_hostname(self):
        return socket.gethostname()

    def exposed_ping(self, target):
        try:
            cmd = ["ping", "-c", "10", target]

            output = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT
            )

            return output.decode()

        except subprocess.CalledProcessError as e:
            return e.output.decode()


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer

    server = ThreadedServer(
        Agent,
        port=18861
    )

    print("RPyC Agent iniciado")
    server.start()
