# Mininet — Transparência e Desempenho

Projeto desenvolvido em **Mininet** para simular uma rede e analisar conceitos de **transparência** e **desempenho** em redes de computadores.

## Objetivo

Criar uma topologia de rede com diferentes condições de enlace, permitindo observar:

* Latência;
* Largura de banda;
* Perda de pacotes;
* Comunicação entre diferentes redes;
* Roteamento entre hosts.

## Topologia
![[Pasted image 20260921092546.png]]
### Endereçamento

| Host    | IP          |
| ------- | ----------- |
| h1      | 10.0.0.1/24 |
| h2      | 10.0.0.2/24 |
| h2-eth1 | 10.0.2.1/24 |
| h3      | 10.0.2.3/24 |
| h4      | 10.0.2.4/24 |
| h5      | 10.0.2.5/24 |

O `h2` atua como roteador entre as redes `10.0.0.0/24` e `10.0.2.0/24`.

## Desempenho

Os enlaces utilizam `TCLink` para simular diferentes condições de rede:

* **Bandwidth (`bw`)** — limita a largura de banda;
* **Delay (`delay`)** — adiciona latência;
* **Loss (`loss`)** — simula perda de pacotes.

Por exemplo, a comunicação entre `h3` e `h5` passa por:

```text
h3 → s2 → h5
```

Com `100 ms` no enlace de `h3` e `140 ms` no enlace de `h5`, o RTT esperado é aproximadamente:

```text
(100 + 140) × 2 = 480 ms
```

Além disso, os enlaces possuem **5% de perda de pacotes**.

## Transparência

A transparência é observada pela abstração da infraestrutura de rede. Os hosts podem se comunicar utilizando seus endereços IP sem precisar conhecer diretamente os detalhes internos dos switches.

O roteamento entre as redes também é configurado no `h2`, permitindo a comunicação entre diferentes segmentos da rede.

## Tecnologias

* Python
* Mininet
* Linux
* Miniedit
* RPyC
