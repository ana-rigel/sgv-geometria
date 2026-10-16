# Painel de replay 4D (16/10/2026)

Painel alternativo do SGV, ligado aos dados **abertos** (maio–setembro/2026). Nasce do que a Fase 5 fechou: instrumento de 1 minuto, quarta dimensão (σ̂) por cortes, sem camada de direção, nula ao lado, duas semanas rolantes mais a âncora de maio.

**Ao vivo: desligado.** Outubro é reservado até 3/11 e novembro até 1/12. O servidor responde 403 em `/vivo` com o motivo. Ligar o fluxo é uma decisão da Ana, depois dos julgamentos, e passa por este README.

## Como roda

```
python painel/exportar_replay.py --meses 2026-05 2026-06 2026-07          # gera painel/dados/replay_*.npz (+ .json de metadados)
python painel/servidor.py --arquivo painel/dados/replay_2026-05_2026-07.npz --porta 8765
# abrir http://localhost:8765/
```

O exportador usa o pipeline do repositório sem modificação (`coords_orig`, `estimativas` har, `regua`, quantis de fatias de `confirmatorio_4d`). Nenhuma definição nova.

## O que a página mostra

- O cubo (E_norm, jerk, memory_flux) na régua de caudas, com os minutos da janela escolhida (1 dia a 2 semanas) coloridos pela temperatura (tercis de maio).
- Corte por fatia (calma / média / quente), botão "unidades de σ̂" (colapso), trajetória dos últimos 240 min, casca HDR50 da seleção (elipsoide a 1,538 σ da covariância).
- Controle de tempo sobre o período exportado; "andar" avança 1 h por segundo.
- Faixa de densidade da temperatura na janela; extremidade e σ̂ do minuto corrente.
- Os números **medidos** nos meses abertos, com a fonte.

## O que não mostra, por decisão

Direção μ(x). Vereditos de outubro antes de 3/11. Qualquer número que não tenha sido medido e registrado.

## Serviço ao vivo (`painel/vivo.py`): escrito, desligado

- Obedece `painel/LIBERACAO.json`. Com `ligado: false` (o estado atual) ele recusa partir e não busca nada.
- Quando a Ana liberar (depois de 3/11, o exemplo está no próprio arquivo), ele busca klines 1 min da Binance por REST **só dentro das janelas liberadas** e liga o fluxo corrente **só a partir de `ao_vivo_desde`**. Qualquer candle fora disso é descartado antes de entrar no buffer.
- A âncora de maio (régua, quantis) vem do `.json` do replay; nunca é recalculada.
- Buffer rolante de 2 semanas + 1 dia de aquecimento; coordenadas pelo mesmo pipeline; mesmas rotas do replay, mais `/vivo` com o estado da liberação.
- `--simular <npz>` alimenta o laço com os meses abertos, para ensaio local. O caminho de cálculo foi testado assim em 16/10; o caminho de rede (Binance) não foi testado nesta sessão, porque o ambiente não alcança a API.

## Manual de leitura

As quatro métricas principais (ext, w, R, C), cenários combinados e o que o painel não diz: [MANUAL.md](MANUAL.md).
