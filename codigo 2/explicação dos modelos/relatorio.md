# Sistema Distribuído com RPyC, Mininet, Transparência e Performance

## 1. Visão geral

Este projeto implementa um sistema distribuído utilizando **Mininet** para simular a rede e **RPyC (Remote Python Call)** para realizar a comunicação entre os computadores virtuais.

A arquitetura possui:

* **H1** → cliente
* **H2** → servidor principal
* **H3** → servidor secundário
* **H4** → servidor secundário
* **H5** → servidor secundário

O cliente H1 não precisa conhecer qual servidor secundário irá executar uma determinada operação.

A decisão é tomada pelo servidor principal H2, que mede o desempenho dos servidores secundários e escolhe aquele que apresenta o **menor RTT (Round Trip Time)** no momento da requisição.

A arquitetura pode ser representada da seguinte forma:

```text
                         ┌───────────────┐
                         │      H3       │
                         │ Secundário    │
                         └───────▲───────┘
                                 │
                                 │ RPyC
                                 │
┌──────────┐       RPyC    ┌─────┴─────┐
│    H1    │ ─────────────>│    H2     │
│ Cliente  │               │ Principal │
└──────────┘               └─────┬─────┘
                                 │
                       ┌─────────┴─────────┐
                       │                   │
                      RPyC                RPyC
                       │                   │
                 ┌─────▼─────┐       ┌────▼──────┐
                 │    H4     │       │    H5     │
                 │Secundário │       │Secundário │
                 └───────────┘       └───────────┘
```

---

# 2. Objetivo do projeto

O objetivo é demonstrar dois conceitos importantes de sistemas distribuídos:

1. **Transparência**
2. **Performance**

O sistema busca fazer com que o cliente não precise conhecer detalhes internos da distribuição dos serviços.

Por exemplo, H1 solicita:

```text
"Faça um ping para 10.0.2.4"
```

O cliente não precisa informar:

```text
"Use H3"
```

ou:

```text
"Use H4"
```

ou:

```text
"Use H5"
```

Essa decisão é responsabilidade do servidor principal H2.

---

# 3. Topologia de rede

A rede utiliza duas sub-redes.

## Rede entre H1 e H2

```text
H1
10.0.0.1
   |
   |
  S1
   |
   |
H2
10.0.0.2
```

## Rede entre H2 e os servidores secundários

```text
                 H3
            10.0.2.3
                 |
                 |
                 S2
                /  \
               /    \
             H4      H5
        10.0.2.4   10.0.2.5
               \    /
                 |
                 |
                H2
           10.0.2.1
```

O H2 possui duas interfaces:

```text
H2-eth0 = 10.0.0.2
H2-eth1 = 10.0.2.1
```

Assim, H2 funciona também como roteador entre as duas redes.

---

# 4. Componentes do sistema

## H1 — Cliente

O H1 é responsável apenas por solicitar uma operação.

Seu programa estabelece uma conexão RPyC com H2:

```python
conn = rpyc.connect("10.0.0.2", 18861)
```

Portanto:

```text
H1 ───── RPyC ─────> H2
```

O cliente não estabelece uma conexão direta com H3, H4 ou H5.

---

# 5. H2 — Servidor principal

O H2 funciona como um **intermediário e gerenciador**.

Ele possui conhecimento dos servidores secundários:

```python
SERVIDORES = {
    "h3": "10.0.2.3",
    "h4": "10.0.2.4",
    "h5": "10.0.2.5"
}
```

Quando recebe uma requisição, H2 realiza duas tarefas principais:

1. Mede o desempenho dos servidores secundários.
2. Encaminha a operação para o servidor escolhido.

---

# 6. H3, H4 e H5 — Servidores secundários

Os servidores secundários executam as operações solicitadas pelo H2.

Todos executam um servidor RPyC na porta:

```text
18861
```

Cada um disponibiliza, por exemplo, a função:

```python
exposed_ping()
```

Assim, H2 pode solicitar remotamente:

```python
conn.root.ping(ip_destino)
```

---

# 7. Funcionamento completo

O fluxo completo pode ser dividido em etapas.

## Etapa 1 — H1 solicita uma operação

O usuário executa:

```text
h1 python3 cliente_h1.py
```

E informa:

```text
10.0.2.4
```

O H1 envia essa informação para H2.

```text
H1
 |
 | "ping 10.0.2.4"
 |
 ▼
H2
```

---

# 8. Etapa 2 — H2 recebe a requisição

No H2 aparece:

```text
Nova requisicao recebida

Destino solicitado: 10.0.2.4
```

Nesse momento, H2 sabe:

```text
Destino = 10.0.2.4
```

Mas ainda não decidiu quem irá executar a operação.

---

# 9. Etapa 3 — H2 mede os servidores

H2 testa os servidores secundários.

No experimento realizado, foi obtido:

```text
h4 -> 502.03 ms
h3 -> 301.88 ms
h5 -> 382.327 ms
```

Podemos representar:

```text
             RTT

H3  ───────── 301.88 ms
H4  ───────── 502.03 ms
H5  ───────── 382.327 ms
```

O menor RTT foi:

```text
H3 = 301.88 ms
```

Portanto, H2 escolheu H3.

---

# 10. Etapa 4 — H2 seleciona o servidor

O código compara os valores:

```python
if menor_rtt is None or rtt < menor_rtt:
    menor_rtt = rtt
    melhor_servidor = nome
```

Consequentemente:

```text
H3 = 301.88 ms
H4 = 502.03 ms
H5 = 382.327 ms
```

Resultado:

```text
Servidor escolhido: H3
```

---

# 11. Etapa 5 — H2 conecta em H3

Depois da escolha, H2 cria uma nova conexão RPyC:

```python
conn = rpyc.connect(
    ip_servidor,
    18861
)
```

Nesse momento temos:

```text
H1 ─────── RPyC ───────> H2
                          |
                          |
                         RPyC
                          |
                          ▼
                         H3
```

---

# 12. Etapa 6 — H3 executa a operação

H2 solicita ao H3:

```python
resultado = conn.root.ping(ip_destino)
```

Como o destino era:

```text
10.0.2.4
```

H3 executa:

```text
ping -c 5 10.0.2.4
```

Ou seja:

```text
H3 ───────────────> H4
       ICMP
```

O H4 é o destino do ping.

É importante perceber que:

> H4 é o destino da operação, mas H3 é o servidor que executa a operação.

Portanto:

```text
Destino:  H4
Executor: H3
```

---

# 13. Etapa 7 — Resultado retorna para H1

Depois de executar o ping, H3 devolve o resultado para H2.

```text
H3
 |
 | resultado
 ▼
H2
 |
 | resultado
 ▼
H1
```

O H1 recebe:

```text
PING 10.0.2.4

64 bytes from 10.0.2.4:
time=601 ms

64 bytes from 10.0.2.4:
time=602 ms

64 bytes from 10.0.2.4:
time=601 ms
```

O cliente não precisou estabelecer uma conexão direta com H3.

---

# 14. Fluxo completo da requisição

O processo completo pode ser representado assim:

```text
                 REQUISIÇÃO

H1
 |
 | 1. "ping 10.0.2.4"
 |
 ▼
H2
 |
 | 2. mede RTT
 |
 +--------------------+
 |                    |
 ▼                    ▼
H3                   H4
301 ms               502 ms
 |
 +--------------------+
 |
 ▼
H5
382 ms

H2 escolhe H3
 |
 | 3. RPyC
 ▼
H3
 |
 | 4. ping 10.0.2.4
 ▼
H4
 |
 | 5. resultado
 ▼
H3
 |
 | 6. resultado
 ▼
H2
 |
 | 7. resultado
 ▼
H1
```

---

# 15. Onde está a transparência?

A transparência aparece principalmente porque **H1 não precisa conhecer a localização do servidor que irá executar a operação**.

O H1 conhece apenas:

```text
H2 = servidor principal
```

Ele não precisa conhecer:

```text
H3
H4
H5
```

nem precisa decidir qual deles será utilizado.

A decisão fica escondida atrás do H2.

Podemos comparar:

## Sem transparência

```text
H1
 |
 | "Use H3 para executar"
 ▼
H3
```

O cliente precisa conhecer detalhes da infraestrutura.

## Com a arquitetura deste projeto

```text
H1
 |
 | "Execute esta operação"
 ▼
H2
 |
 | decide internamente
 +------> H3
 +------> H4
 +------> H5
```

O cliente trabalha apenas com o serviço oferecido por H2.

Isso reduz a dependência do cliente em relação à estrutura interna do sistema.

---

# 16. Transparência de localização

Um dos conceitos demonstrados é a **transparência de localização**.

O cliente não precisa saber onde está o recurso responsável pela execução.

Para H1:

```text
"Eu quero executar uma operação."
```

Para H2:

```text
"Qual servidor secundário deve executar?"
```

Para o cliente, a escolha é transparente.

Por exemplo, hoje H2 pode escolher:

```text
H3
```

Em outro momento, devido às condições da rede, poderia escolher:

```text
H5
```

O código do cliente H1 continua o mesmo.

---

# 17. Transparência de acesso

Também existe uma forma de **transparência de acesso**.

O H1 utiliza:

```python
conn.root.executar(ip_destino)
```

Ele não precisa saber como a operação será realizada internamente.

Internamente, H2 pode:

```text
1. medir servidores
2. escolher servidor
3. criar conexão RPyC
4. executar operação
5. receber resultado
6. retornar resultado
```

Mas H1 enxerga apenas:

```text
executar()
```

Essa separação entre interface utilizada pelo cliente e implementação interna é uma característica importante da arquitetura distribuída.

---

# 18. Onde entra a performance?

A performance entra na decisão realizada pelo H2.

Em vez de simplesmente escolher sempre:

```text
H3
```

ou sempre:

```text
H4
```

ou sempre:

```text
H5
```

o H2 mede uma característica da rede:

```text
RTT
```

Neste experimento:

```text
H3 = 301.88 ms
H4 = 502.03 ms
H5 = 382.327 ms
```

O H2 escolheu o menor valor:

```text
H3 = 301.88 ms
```

A ideia é utilizar informações de desempenho para escolher dinamicamente um servidor.

---

# 19. Por que isso é melhor do que escolher um servidor fixo?

Imagine que o código sempre utilizasse:

```text
H4
```

Mesmo que naquele momento H4 apresentasse:

```text
502 ms
```

enquanto H3 apresentasse:

```text
301 ms
```

o sistema continuaria utilizando H4.

Na arquitetura atual, o H2 observa o estado medido no momento da requisição.

Assim:

```text
          Medição

H3 ───── 301 ms ────┐
H4 ───── 502 ms ────┼──> H2 escolhe
H5 ───── 382 ms ────┘
```

Isso permite que a escolha seja baseada em uma métrica de desempenho.

---

# 20. Importante: o que o RTT representa neste projeto?

O RTT utilizado pelo H2 representa o tempo de ida e volta entre:

```text
H2 ↔ servidor secundário
```

Por exemplo:

```text
H2 ↔ H3 = aproximadamente 301 ms
```

Portanto, o código atual não está medindo diretamente:

```text
tempo total da operação
```

nem:

```text
uso de CPU
```

nem:

```text
memória
```

nem:

```text
carga do servidor
```

nem:

```text
tempo de processamento
```

O critério atual é especificamente:

> **RTT entre H2 e o servidor secundário.**

Isso deve ser explicado dessa maneira na apresentação para que o funcionamento do sistema fique tecnicamente correto.

---

# 21. Relação entre transparência e performance

Esses dois conceitos trabalham juntos.

### Transparência

Permite que:

```text
H1
```

não precise conhecer:

```text
H3
H4
H5
```

### Performance

Permite que:

```text
H2
```

escolha um servidor baseado em uma métrica observada.

Assim:

```text
             TRANSPARÊNCIA
                  │
                  ▼
        H1 não escolhe o servidor
                  │
                  ▼
                 H2
                  │
                  │
          mede performance
                  │
                  ▼
             ┌────┴────┐
             │         │
            H3        H4        H5
             │         │         │
          301 ms    502 ms    382 ms
             │         │         │
             └─────────┼─────────┘
                       │
                       ▼
                  escolhe H3
```

O cliente recebe o serviço sem precisar conhecer a decisão interna.

---

# 22. Exemplo real do experimento

O H1 solicitou:

```text
ping 10.0.2.4
```

H2 recebeu:

```text
Destino solicitado: 10.0.2.4
```

Depois mediu:

```text
h4 -> 502.03 ms
h3 -> 301.88 ms
h5 -> 382.327 ms
```

Escolheu:

```text
Servidor escolhido: h3
```

E conectou:

```text
Conectado ao h3
```

Então H3 executou o ping para H4.

O resultado retornou para H1:

```text
5 packets transmitted
5 received
0% packet loss
```

Portanto, a operação solicitada por H1 foi executada por um servidor que **H1 não precisou escolher nem conhecer**.

---

# 23. Resumo da arquitetura

```text
┌──────────────────────────────────────────┐
│                  H1                      │
│                Cliente                   │
└──────────────────┬───────────────────────┘
                   │
                   │ RPyC
                   ▼
┌──────────────────────────────────────────┐
│                  H2                      │
│           Servidor Principal              │
│                                          │
│  1. recebe requisição                    │
│  2. mede RTT                             │
│  3. compara servidores                   │
│  4. escolhe o menor RTT                  │
│  5. encaminha operação                   │
└──────────────┬─────────────┬─────────────┘
               │             │
              RPyC          RPyC
               │             │
               ▼             ▼
             ┌────┐       ┌────┐
             │ H3 │       │ H4 │
             └────┘       └────┘
                 \          /
                  \        /
                   \      /
                    ┌────┐
                    │ H5 │
                    └────┘
```

---

# 24. Conceitos demonstrados

O projeto demonstra principalmente:

### Sistemas distribuídos

Os serviços estão distribuídos entre diferentes hosts:

```text
H1 + H2 + H3 + H4 + H5
```

### Comunicação remota

A comunicação entre os processos é feita utilizando:

```text
RPyC
```

### Transparência

O cliente não precisa conhecer qual servidor secundário executará a operação.

### Seleção dinâmica

O H2 escolhe um servidor em tempo de execução.

### Avaliação de performance

O H2 utiliza RTT como métrica para comparar os servidores.

### Encaminhamento de requisições

O H2 atua como intermediário entre o cliente e os servidores secundários.

---

# 25. Conclusão

O sistema implementa uma arquitetura em que o **H1 atua como cliente**, o **H2 atua como servidor principal e coordenador**, e **H3, H4 e H5 atuam como servidores secundários**.

Quando H1 solicita uma operação, ele não precisa conhecer a estrutura interna do sistema. A requisição é enviada para H2, que avalia os servidores secundários utilizando o RTT como métrica de desempenho.

Após realizar a medição, H2 seleciona o servidor com menor RTT e encaminha a operação através de RPyC.

No experimento:

```text
H3 = 301.88 ms
H4 = 502.03 ms
H5 = 382.327 ms
```

H2 selecionou H3.

H3 então executou:

```text
ping 10.0.2.4
```

e devolveu o resultado para H2, que finalmente retornou o resultado para H1.

Dessa forma, o projeto demonstra uma combinação de **transparência e seleção baseada em desempenho**:

```text
              CLIENTE
                 │
                 │
                 ▼
        ┌────────────────┐
        │       H2       │
        │   Coordenação  │
        └───────┬────────┘
                │
       mede performance
                │
        ┌───────┼───────┐
        ▼       ▼       ▼
       H3      H4      H5
        │       │       │
      301ms   502ms   382ms
        │
        ▼
    escolhido
        │
        ▼
     executa
        │
        ▼
     resultado
        │
        ▼
       H1
```

**O ponto central do projeto é que H1 solicita um serviço, e H2 esconde do cliente a decisão de qual servidor secundário será utilizado, enquanto utiliza uma métrica de desempenho para realizar essa escolha.**
