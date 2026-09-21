import rpyc
import subprocess
import re

from rpyc.utils.server import ThreadedServer


SERVIDORES = {
    "h3": "10.0.2.3",
    "h4": "10.0.2.4",
    "h5": "10.0.2.5"
}


def medir_rtt(ip):
    """
    Mede o RTT médio de um servidor.
    """

    try:
        resultado = subprocess.check_output(
            ["ping", "-c", "3", ip],
            stderr=subprocess.STDOUT
        ).decode("utf-8")

        # Procura:
        # rtt min/avg/max/mdev = 240.000/241.000/...
        match = re.search(
            r"rtt min/avg/max/mdev = [^/]+/([^/]+)/",
            resultado
        )

        if match:
            return float(match.group(1))

    except Exception:
        pass

    return None


class ServicoPrincipal(rpyc.Service):

    def exposed_status(self):
        return "Servidor principal OK"

    def exposed_executar(self, ip_destino):

        print("\n==============================")
        print("Nova requisicao recebida")
        print("==============================")

        print("Destino solicitado:", ip_destino)

        melhor_servidor = None
        menor_rtt = None

        print("\nMedindo servidores secundarios...")

        for nome, ip in SERVIDORES.items():

            rtt = medir_rtt(ip)

            if rtt is None:
                print(nome, "-> indisponivel")
                continue

            print(nome, "->", rtt, "ms")

            if menor_rtt is None or rtt < menor_rtt:
                menor_rtt = rtt
                melhor_servidor = nome

        if melhor_servidor is None:
            return "Nenhum servidor secundario disponivel"

        ip_servidor = SERVIDORES[melhor_servidor]

        print("\nServidor escolhido:", melhor_servidor)
        print("RTT:", menor_rtt, "ms")

        try:

            conn = rpyc.connect(
                ip_servidor,
                18861
            )

            print(
                "Conectado ao",
                melhor_servidor
            )

            resultado = conn.root.ping(ip_destino)

            conn.close()

            return resultado

        except Exception as e:

            return (
                "Erro ao executar no servidor "
                + melhor_servidor
                + ": "
                + str(e)
            )


server = ThreadedServer(
    ServicoPrincipal,
    port=18861
)

print("Servidor principal H2 iniciado na porta 18861")

server.start()