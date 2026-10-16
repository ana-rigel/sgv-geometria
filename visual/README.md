# Páginas visuais do SGV (16/10/2026)

Cinco páginas HTML autônomas (abrem no navegador, sem servidor; carregam three.js r128 do cdnjs). Feitas na sessão de 16/10 para ver a quarta dimensão do cubo. **Os pontos são simulados** com a receita do sintético M (AR(1) + volatilidade em duas escalas), não dados do BTC; os números do BTC aparecem só onde estão marcados como medidos.

| Arquivo | O que mostra |
|---|---|
| `navegador-estado-atual.html` | O cubo 3D com as camadas do navegador (campo, trajetória, casca), a temperatura σ̂ como cor e fatias, e a tabela "navegador de 13/10 × hoje" |
| `hipercubo-sgv.html` | Projeção 4D→3D do hipercubo (16 vértices, 32 arestas) com a nuvem em 4 coordenadas; controle que gira σ̂ para dentro da tela |
| `cubo-vs-hipercubo.html` | Os dois visores lado a lado, girando juntos; só o da direita tem σ̂ como eixo |
| `fatia-4d-sgv.html` | A quarta dimensão por cortes (como no Miegakure / 4D Toys): andar pela temperatura e ver só os minutos daquela fatia, o hipercubo cortado e a casca HDR50 da fatia |
| `cubo-por-resolucao.html` | Três cubos em 1, 5 e 15 min com os anéis do campo marcados pelo R **medido** no BTC, e os gráficos de R e C por resolução das duas rodadas (`exploracao/autosimilaridade-temporal`) |

Versões publicadas no Claude (privadas) existem com os mesmos nomes; esta pasta é a cópia de registro.
