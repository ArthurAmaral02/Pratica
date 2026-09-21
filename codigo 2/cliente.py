import rpyc


print("==============================")
print("Cliente H1")
print("==============================")

try:

    conn = rpyc.connect(
        "10.0.0.2",
        18861
    )

    print("Conectado ao servidor principal H2")

    print(
        "Status:",
        conn.root.status()
    )

    ip = input(
        "Digite o IP do host que deseja pingar: "
    )

    print("\nSolicitando ping...")

    resultado = conn.root.executar(ip)

    print("\n========== RESULTADO ==========")
    print(resultado)

    conn.close()

except Exception as e:

    print("ERRO:", e)