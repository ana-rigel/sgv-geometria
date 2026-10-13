# SGV M11-I — protocolo de integração instrumental
Status: desenvolvimento de medição, **não** experimento confirmatório sobre BTC.
**Ramo:** `research/m11i-integracao-instrumental`, iniciado do M11, sem mudar main.

## Assinatura
`G(A->B)=(dc_x,dc_y,dc_z,log(VB/VA),theta,R_M11,D_A,D_B,delta_D)`.
Uma única casca GMM2 HDR50 por fotografia, da mesma transformação marginal
30% de âncora, 35% A, 35% B. Grade 35³; cobertura >=95%.
As demais propriedades saem das próprias malhas; não refazer GMM para obter D.
`D=mean_area(max(0,-K*r_eq²))`, K da Hessiana analítica da densidade.
O ângulo é distância SO(3)/D2 com limiar de gap 0,07, ausente quando ambíguo.
O residual é a distância direta à malha M11 após centrar/escala/registro.

## Extensão declarada em relação ao M11
Além do ICP multistart, calcular quatro candidatas de registro definidas
pelos eixos principais e escolher a de menor distância ponto-triângulo
em 64 pontos; então calcular R_M11 em 256/512 pontos. Esse
ajuste estabiliza controles rigidamente equivalentes. É extensão
instrumental que precisa ser validada; os resultados M11 históricos
não são alterados.

## Testes sintéticos (não equivalem a mercado)
Identidade; translação [0,4;-0,3;0,2]; escala 1,1;
rotação 25° em elipsoide triaxial; deformação anisotrópica
[1,18;0,78;1]; rotação em esfera com eixo indefinido;
GMM2 gerada em trajetória sintética; rejeição de malha aberta.
Transformações puramente rígidas devem gerar residual baixo;
uma transformação anisotrópica deve gerar residual maior.
Para malhas artificiais transformadas sem GMM subjacente não
atribuir falsos índices D.

## Limites
São geometrias de isodensidade em scores gaussianizados,
não curvatura Fisher–Rao, tensão física nem vantagem preditiva.
Sem trajetória multi-janela com referência global congelada,
sem bootstrap calibrado da variabilidade do GMM e sem
validação de desempenho financeiro. Nenhum ETH/SOL/BNB,
BTC reservado ou dado de teste é carregado automaticamente.
