````md
# RPyC + Mininet — Rede Distribuída Controlada

Experimento utilizando Mininet, TCLink e RPyC para criar uma rede virtual com agentes distribuídos e condições controladas de latência, largura de banda e perda de pacotes.

---

## 1. Arquivos

A estrutura básica do projeto é:

```text
projeto/
├── topology.py
├── agent.py
├── controller.py
├── README.md
└── RELATORIO.md
````

---

## 2. Requisitos

Ambiente utilizado:

```text
Ubuntu 14.04.3 LTS
Python 3.4.3
Mininet
RPyC 3.3.0
```

Verifique o Python:

```bash
python3 --version
```

Verifique o RPyC:

```bash
python3 -c "import rpyc; print(rpyc.__version__)"
```

Resultado esperado:

```text
(3, 3, 0)
```

---

## 3. Instalar o RPyC

Caso o RPyC ainda não esteja instalado:

```bash
sudo apt-get install python3-pip
sudo pip3 install 'rpyc==3.3.0'
```

Teste:

```bash
python3 -c "import rpyc; print(rpyc.__version__)"
```

---

## 4. Topologia

A topologia utiliza três hosts e um switch.

```text
              +-------+
              |  s1   |
              +-------+
               / | \
              /  |  \
             /   |   \
            h1   h2   h3

        10.0.0.1  10.0.0.2  10.0.0.3
```

Configuração dos enlaces:

```text
h1 -- s1
10 Mbps
20 ms
1% loss

h2 -- s1
5 Mbps
50 ms
3% loss

h3 -- s1
2 Mbps
100 ms
5% loss
```

---

## 5. Executar a topologia

Execute:

```bash
sudo python topology.py
```

Quando o CLI do Mininet aparecer:

```text
mininet>
```

a rede estará disponível.

---

## 6. Testar conectividade

Execute:

```text
mininet> pingall
```

Para um teste mais longo, utilize:

```text
mininet> h1 ping -c 100 10.0.0.2
```

Ou:

```text
mininet> h1 ping -c 100 10.0.0.3
```

---

## 7. Verificar o RPyC nos hosts

O comando correto é `python3`.

Não utilizar:

```text
python agent.py
```

porque o comando `python` da VM utiliza Python 2.

Utilize:

```text
python3 agent.py
```

Teste o RPyC:

```text
mininet> h1 python3 -c "import rpyc; print(rpyc.__version__)"
mininet> h2 python3 -c "import rpyc; print(rpyc.__version__)"
mininet> h3 python3 -c "import rpyc; print(rpyc.__version__)"
```

Resultado esperado:

```text
(3, 3, 0)
```

---

## 8. Iniciar os agentes

Com o CLI do Mininet aberto:

```text
mininet> h1 python3 agent.py &
mininet> h2 python3 agent.py &
mininet> h3 python3 agent.py &
```

Os três agentes utilizam a porta:

```text
18861
```

---

## 9. Verificar os agentes

Verifique os processos:

```text
mininet> h1 ps aux | grep agent.py
```

Também é possível verificar a porta:

```text
mininet> h1 netstat -lnt | grep 18861
mininet> h2 netstat -lnt | grep 18861
mininet> h3 netstat -lnt | grep 18861
```

Deve aparecer:

```text
0.0.0.0:18861
```

com estado:

```text
LISTEN
```

---

## 10. Testar o controller

O controller deve ser executado dentro de um host Mininet porque os endereços:

```text
10.0.0.1
10.0.0.2
10.0.0.3
```

pertencem à rede virtual.

Execute:

```text
mininet> h1 python3 controller.py
```

O resultado esperado é semelhante a:

```text
========================
Host: h1
IP: 10.0.0.1
Status: OK
Hostname: sdnhubvm

========================
Host: h2
IP: 10.0.0.2
Status: OK
Hostname: sdnhubvm

========================
Host: h3
IP: 10.0.0.3
Status: OK
Hostname: sdnhubvm
```

---

## 11. Testar h1 -> h2 através do RPyC

O controller pode conectar ao agente do h1:

```python
conn = rpyc.connect("10.0.0.1", 18861)
```

e solicitar:

```python
resultado = conn.root.ping("10.0.0.2")
```

O fluxo será:

```text
Controller
     |
     | RPyC
     v
Agent h1
     |
     | ping
     v
    h2
```

Execute:

```text
mininet> h1 python3 controller.py
```

---

## 12. Resultado esperado

O resultado deverá conter informações semelhantes a:

```text
10 packets transmitted, 8 received, 20% packet loss
```

e:

```text
rtt min/avg/max/mdev =
141.166/182.961/291.685/50.599 ms
```

Os valores variam a cada execução.

Para o caminho:

```text
h1 -> s1 -> h2
```

a latência configurada é:

```text
20 ms + 50 ms = 70 ms
```

Como o ping mede ida e volta:

```text
70 ms * 2 = aproximadamente 140 ms
```

---

## 13. Teste h1 -> h3

Para testar o h3, solicite ao agente do h1:

```python
conn.root.ping("10.0.0.3")
```

O caminho será:

```text
h1 -> s1 -> h3
```

com:

```text
20 ms + 100 ms = 120 ms
```

e RTT aproximado:

```text
120 ms * 2 = 240 ms
```

---

## 14. Testes entre todos os hosts

Os caminhos que podem ser medidos são:

```text
h1 -> h2
h1 -> h3

h2 -> h1
h2 -> h3

h3 -> h1
h3 -> h2
```

Para cada caminho podem ser coletados:

```text
RTT mínimo
RTT médio
RTT máximo
desvio padrão
perda de pacotes
```

---

## 15. Parar os agentes

Quando terminar os testes:

```text
mininet> h1 pkill -f "python3 agent.py"
mininet> h2 pkill -f "python3 agent.py"
mininet> h3 pkill -f "python3 agent.py"
```

---

## 16. Encerrar o Mininet

No CLI:

```text
mininet> exit
```

Depois, se necessário:

```bash
sudo mn -c
```

O comando `mn -c` limpa interfaces e processos residuais do Mininet.

---

## 17. Fluxo completo

A execução completa pode ser resumida:

```text
1. Iniciar a VM
       |
       v
2. Executar topology.py
       |
       v
3. Entrar no CLI do Mininet
       |
       v
4. Iniciar agent.py em h1, h2 e h3
       |
       v
5. Verificar porta 18861
       |
       v
6. Executar controller.py
       |
       v
7. Controller conecta via RPyC
       |
       v
8. Agent executa ping
       |
       v
9. Mininet aplica delay/bw/loss
       |
       v
10. Controller recebe as métricas
```

---

## 18. Próxima evolução

O próximo passo do projeto é automatizar o controller para realizar:

```text
              ┌──> h2
              |
h1 ───────────┼──> h3
              |
h2 ───────────┼──> h1
              |
              ├──> h3
              |
h3 ───────────┼──> h1
              |
              └──> h2
```

e gerar automaticamente uma tabela:

```text
+--------+---------+-----------+---------+
| Origem | Destino | RTT médio | Perda   |
+--------+---------+-----------+---------+
| h1     | h2      | ...       | ...     |
| h1     | h3      | ...       | ...     |
| h2     | h1      | ...       | ...     |
| h2     | h3      | ...       | ...     |
| h3     | h1      | ...       | ...     |
| h3     | h2      | ...       | ...     |
+--------+---------+-----------+---------+
```

Depois disso, o controller poderá ser expandido para alterar dinamicamente:

```text
bandwidth
latency
packet loss
```

permitindo realizar experimentos automatizados de comportamento da rede.

```
```
