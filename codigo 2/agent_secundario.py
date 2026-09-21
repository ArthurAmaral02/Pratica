import rpyc
import subprocess
from rpyc.utils.server import ThreadedServer


class ServicoSecundario(rpyc.Service):

    def exposed_status(self):
        return "OK"

    def exposed_ping(self, ip):
        """
        Executa ping para o IP solicitado
        a partir deste servidor secundário.
        """
        resultado = subprocess.check_output(
            ["ping", "-c", "5", ip],
            stderr=subprocess.STDOUT
        )

        return resultado.decode("utf-8")


server = ThreadedServer(
    ServicoSecundario,
    port=18861
)

print("Servidor secundario RPyC iniciado na porta 18861")
server.start()