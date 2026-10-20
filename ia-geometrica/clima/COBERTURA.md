# Cobertura dos dados de clima de Juara (auditoria; nenhum valor lido)

19/10/2026 · conta só campos vazios ou −9999, por ano; não olha magnitudes

**INMET A914 JUARA** (lat −11,280, lon −57,527, alt. 263 m, fundada em 02/11/2006). A estação do texto (A936) não é a de Juara.

| ano | chuva ausente | ano | chuva ausente |
|---|---|---|---|
| 2008 | 27 % | 2017 | 29 % |
| 2009 | 0 % | 2018 | 1 % |
| 2010 | 0 % | 2019 | 38 % |
| 2011 | 0 % | 2020 | 30 % |
| 2012 | 54 % | 2021 | **100 %** |
| 2013 | 16 % | 2022 | 83 % |
| 2014 | 0 % | 2023 | 17 % |
| 2015 | 0 % | 2024 | **100 %** |
| 2016 | 24 % | 2025 | **100 %** |

Anos completos: 2009–2011, 2014, 2015 e 2018. Com buracos desse tamanho, a estação não serve de entrada contínua para um registro de meses (o andar 3 lembra por ≈ 28 dias e o 4 por ≈ 9 meses com passo horário). Serve como conferência da reanálise nos anos completos.

**ERA5-Land via Open-Meteo, 1ª rodada (run 39360875918):** 140.256 horas (2010–2025), sem falhas de ano; umidade do solo nas quatro camadas, temperatura, umidade do ar e VPD completos; **chuva, radiação e ET0 vieram vazias em todas as horas** (o modelo `era5_land` da Open-Meteo não as entrega). Corrigido no script: essas três vêm do ERA5 (mesma reanálise, grade de ≈ 25 km). 2ª rodada a seguir.
