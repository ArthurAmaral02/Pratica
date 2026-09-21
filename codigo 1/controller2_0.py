import rpyc
import time

HOSTS = {
    "h1": "10.0.0.1",
    "h2": "10.0.0.2",
    "h3": "10.0.0.3"
}

print("==============================")
print("   SISTEMA DISTRIBUÍDO")
print("==============================")

print("\nHosts disponíveis:")
for nome in HOSTS:
    print("-", nome)

origem = input("\nEscolha o host de origem: ").strip().lower()
destino = input("Escolha o host de destino: ").strip().lower()

if origem not in HOSTS or destino not in HOSTS:
    print("Host inválido.")
    exit()

if origem == destino:
    print("Origem e destino não podem ser iguais.")
    exit()

ip_origem = HOSTS[origem]
ip_destino = HOSTS[destino]

print("\nConectando ao agente de", origem, "...")

try:
    conn = rpyc.connect(ip_origem, 18861)

    print("Conectado!")
    print("Status:", conn.root.status())

    print("\nExecutando operação remota...")
    print("Origem:", origem)
    print("Destino:", destino)

    inicio = time.time()

    resultado = conn.root.ping(ip_destino)

    fim = time.time()

    tempo = (fim - inicio) * 1000

    print("\n========== RESULTADO ==========")
    print(resultado)

    print("Tempo total da chamada RPyC: %.2f ms" % tempo)

    conn.close()

except Exception as e:
    print("\nERRO:", e)