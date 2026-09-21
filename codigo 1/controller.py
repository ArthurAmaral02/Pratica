import rpyc

print("==============================")
print("inicializando conex~ao")
print("==============================")

try:
    # Conecta ao agente que está rodando no h1
    
    x = input("digite o ip do host/cliente: ")
    if x == "10.0.0.1":
        print(x, " eh o h1")
        aux = "h1"
    elif x == "10.0.0.2":
        print(x, " eh o h2")
        aux = "h2"
    else:
        print(x, "eh o h3") 
        aux = "h3"



    conn = rpyc.connect(x, 18861)

    print("Conectado!")
    print("Status:", conn.root.status())

    z = input("digite o ip do host que deseja pingar: ")
    
    print("\nExecutando ping de", aux ,"para", z , "...")
    if z == "10.0.0.1":
        print(z, " eh o h1")
    elif z == "10.0.0.2":
        print(z, " eh o h2")
    else:
        print(z, "eh o h3") 


    # O agente do h1 executará o ping
    resultado = conn.root.ping(z)

    print("\n========== RESULTADO ==========")
    print(resultado)

    conn.close()

except Exception as e:
    print("ERRO:", e)
