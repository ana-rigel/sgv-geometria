# M29 — Registro de engenharia (depois do protocolo, antes de qualquer posto)

- Testes unitários: o perfil recupera um relógio plantado (:00 mais alto, encolhimento > 0,5, correlação > 0,8), encolhe para perto de zero sem relógio, e a simulação reproduz a fase do relógio na janela futura.
- Piloto local (origem 0, par, 2 referências): sem problemas, 26 s. Nenhum posto ou diagnóstico de dado real inspecionado.
- Workflow: mesmo esquema do M28 (42 shards de 2 origens). O diagnóstico das pares (`reports/m29diag/`) é lido só na agregação, para a correlação descritiva do perfil.
