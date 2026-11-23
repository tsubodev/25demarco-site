# 25 de Março — Potree

Instalação estática do [Potree oficial](https://github.com/potree/potree), tag `1.8.2`, commit `3013577379b5c8530ebca3cdc980f7585ae2320f`.

`vendor/potree-1.8.2/` contém as bibliotecas oficiais e o build sem alterações locais. `index.html` usa a integração do exemplo oficial como base; a cópia `6716-static-v2` foi preparada a partir do arquivo original `6716-cloud` e está sem associação na planilha atual. A nuvem `25 de março` e o arquivo original `6716-cloud` permanecem preservados em `pointclouds/`. As nuvens de demonstração foram removidas.

## Executar

Na raiz do repositório:

```sh
python3 -m http.server 8000
```

A nuvem 6716 usa arquivos individuais, sem precisar de suporte HTTP Range. Para regenerar a cópia de exibição, execute `python3 tools/prepare-6716.py`. O script preserva os 211.969 pontos, exporta posições e RGB e verifica a contagem e o erro máximo de posição (0,00000005 unidade). Os atributos originais permanecem intactos em `6716-cloud`. As nuvens no formato Potree 2.0 precisam de um servidor compatível com Range.

## Reproduzir os arquivos oficiais

Clone `https://github.com/potree/potree` na tag `1.8.2` em uma pasta separada, execute `npm ci` e confirme os arquivos gerados em `build/potree/`. Copie `build/potree/`, `libs/` e `LICENSE` para a pasta versionada de `vendor/`. A integração usa a base do exemplo oficial, com uma interface própria em `assets/interface.css` e `assets/interface.js`. As bibliotecas oficiais não foram modificadas.

## Publicação

No GitHub Pages, selecione **Settings → Pages → Build and deployment → Source → GitHub Actions**. O workflow `.github/workflows/pages.yml` publica automaticamente os commits de `main`.

`python3 tools/build-site.py /tmp/25demarco-site-build` prepara o pacote em um diretório novo, fora do repositório. Ele inclui apenas a aplicação, as bibliotecas e os datasets de exibição cadastrados; originais, XMLs e ferramentas permanecem no Git, fora do pacote publicado. Isso mantém a publicação abaixo do limite de 1 GB do Pages. `.nojekyll` mantém a publicação estática. O envio para `main` não confirma, por si só, que o deploy terminou.

## Interface alpha

O site inicia em uma apresentação com **iniciar >**, conforme o PDF `ev - 25 de março_TESTE_2.pdf`. O botão abre a seleção de puxadores. A associação das nuvens segue o catálogo Fusion 1 abaixo. Cada página carrega apenas seu próprio conjunto; ao trocar de página, apenas os trechos do percurso selecionado ficam visíveis. Os nomes são Guilherme, Emily, Tiago e Benne. O botão MENU permite retornar à seleção; Escape alterna o menu depois que o percurso é aberto. O Potree é inicializado apenas ao entrar no percurso.

O layout usa roxo, amarelo-claro, títulos em itálico e degradê na abertura. A área do Potree usa fundo transparente sobre o roxo do site, Eye-Dome Lighting desligado, tamanho 0.25, sizing ADAPTIVE e shape CIRCLE. A coluna lateral apresenta mapa estático, relato e quatro fotografias extraídos do PDF. O título e o texto de abertura continuam provisórios como na referência. Os controles da visita e dos eixos ficam em uma seção recolhível depois das fotos. Os créditos seguem a referência fornecida. O menu nativo do Potree permanece desativado.

Em telas maiores, a coluna de informações rola independentemente do visualizador. No celular, os painéis ficam empilhados. Inicialmente, deslizar sobre a nuvem rola a página. O botão **EXPLORAR NUVEM** ativa os gestos 3D; **VOLTAR À ROLAGEM** libera novamente a página. Os mapas e fotos ficam em `assets/layout/`, e os nomes/relatos em `assets/people.js`. O mapa é estático nesta versão, conforme solicitado. O botão TÍTULO retorna à apresentação.

Para verificar a navegação, as configurações da nuvem e os tamanhos de tela (1450, 390 e 375 px), com Playwright e Chromium disponíveis:

```sh
python3 tools/check-interface.py --url http://127.0.0.1:8000/
```

O teste também verifica a ausência de erros HTTP/JavaScript, o retorno ao menu e a associação da nuvem ao PUXADOR 1 e a navegação sem duplicar nuvens. Capturas de tela ficam em `/tmp/25demarco-ui-check/`.

## Cadastro de point clouds por puxador

O catálogo [Fusion 1](assets/cloud-catalog.json) registra a ordem das colunas da planilha. Cada item representa uma nuvem. Itens sem `sources` aguardam importação. O visualizador e o pacote do Pages usam o mesmo catálogo.

| Puxador | Disponíveis | Aguardando importação, na ordem da planilha |
| --- | --- | --- |
| 1 · Guilherme | GPBK6717 (3 trechos), GPBK6718, GPBK6719 (12 trechos) | GPBK6720 a GPBK6726 |
| 2 · Emily | — | GPBK627, GPBK6728, GPBK6729, GB016730, GPBK6730 |
| 3 · Thiago | — | GPBK6732 |
| 4 · Benny (Benne no site) | GPBK6735 (17 trechos) | GPBK6733, GPBK6734, GPBK6736 |

Ao importar uma nuvem, prepare a cópia estática em uma pasta própria e preencha `sources` no item correspondente com objetos `{ "url": "pointclouds/.../cloud.js", "name": "..." }`. O caminho deve apontar para um descritor existente. O empacotamento inclui as pastas desses descritores. Se faltar uma nuvem, a página continua acessível com texto, mapa e fotos. O conjunto 6716 fica arquivado. Os momentos de Thiago foram calibrados na 6719 e precisarão de novas posições para a GPBK6732.

Para preparar novos datasets no mesmo formato estático, preservando os originais:

```sh
python3 tools/prepare_point_cloud.py pointclouds/6718-cloud pointclouds/6718-static
```

A nuvem 6718 contém 490.330 pontos. As configurações ADAPTIVE, CIRCLE, 0.25, fundo branco e EDL desligado se aplicam a todos os percursos. As nuvens são carregadas sob demanda e mantidas em cache; retornar a uma página não duplica seu point cloud. O enquadramento usa apenas o percurso selecionado.

## Conjunto 6717

Os três trechos da GPBK6717 ficam em `pointclouds/6717/original/`, com cópias para exibição em `pointclouds/6717/static/`. São 3.710.770 pontos. O Puxador 1 abre com a 6717 e seus três trechos juntos. O seletor **Nuvem** permite alternar entre 6717, 6718 e 6719 no mesmo visualizador, exibindo um conjunto por vez. As coordenadas de cada arquivo são preservadas.

Para regenerar as cópias estáticas:

```sh
for segment in 6717.11_converted 6717.12_converted 6717.2_converted; do
  python3 tools/prepare_point_cloud.py "pointclouds/6717/original/$segment" "pointclouds/6717/static/$segment"
done
```

## Conjunto 6719

Os 12 diretórios recebidos foram movidos de `6719/` para `pointclouds/6719/original/`, sem editar seu conteúdo. A cópia para exibição fica em `pointclouds/6719/static/`; são **11.321.028 pontos** no total.

Todos os trechos são carregados juntos no PUXADOR 1 (Guilherme), ao lado da 6718, quando a GPBK6719 está selecionada no visualizador Potree. As coordenadas e os offsets de origem de cada trecho são preservados; não há translação dos point clouds para zero, troca de eixos ou mudança de escala. O enquadramento existente considera o conjunto selecionado, sem alterar a origem dos dados.

Para reproduzir os arquivos de exibição:

```sh
python3 tools/prepare-6719.py
python3 tools/check-6719.py --url http://127.0.0.1:8000/
```

`project42_converted` fornece `octree.zip`. O preparador lê `octree.bin` de dentro desse ZIP em memória, preservando o arquivo original compactado no Git. Os atributos completos permanecem nos originais; a exibição exporta posições e RGB, com erro de quantização limitado a 0,00000005 unidade. A validação confere as posições dos 12 objetos Potree contra as origens recebidas, a renderização conjunta e a troca de páginas sem duplicar trechos.

## Conjunto 6735

O PUXADOR 4 carrega os 17 trechos da 6735 juntos. Os originais e `6735 cam.xml` permanecem em `pointclouds/6735/`; as cópias de exibição ficam em `pointclouds/6735/static/`. São **8.012.558 pontos**. Cada trecho preserva as coordenadas, os offsets e a origem recebidos, sem translação para zero, troca de eixos ou mudança de escala. O XML é a fonte da trajetória descrita abaixo.

Para reproduzir e verificar:

```sh
python3 tools/prepare-6735.py
python3 tools/check-6735.py --url http://127.0.0.1:8000/
```

O preparador verifica todos os pontos e limita o erro de quantização a 0,00000005 unidade. A cópia estática exporta posições e RGB; os atributos completos permanecem nos originais. O teste verifica as 17 origens, a renderização e a troca de percursos sem duplicação.

## Trajetória e visita guiada — PUXADOR 4

`pointclouds/6735/6735 cam.xml` contém 240 câmeras alinhadas do sensor esférico, em um único chunk/componente, com referência `Local Coordinates (m)`. Os nomes `VÍDEO_6735000` a `VÍDEO_6735239` definem a ordem numérica; não há tempos de captura. As matrizes são poses câmera → chunk; seus centros são a última coluna. Não há transformação adicional de chunk/componente. A rotação `region/R` descreve a caixa de recorte, não deve ser aplicada às câmeras.

O mapeamento do XML para os dados originais da nuvem é identidade: os centros permanecem no referencial local recebido, sem subtrair offsets, recentralizar ou trocar eixos. Os 240 centros estão dentro dos limites dos trechos da 6735. Uma comparação com uma amostra de 1/20 dos pontos originais encontrou distância mediana de 2,37 m e máxima de 4,55 m entre câmeras e superfícies. Isso é evidência de compatibilidade espacial, não substitui uma conferência independente no projeto Metashape; os metadados Potree não declaram projeção nem documentam eventuais transformações externas.

Para reproduzir e validar:

```sh
python3 tools/prepare-6735-trajectory.py
python3 tools/check-6735-trajectory.py --url http://127.0.0.1:8000/
# Opcional: também reproduzir a visita desktop inteira em tempo real.
python3 tools/check-6735-trajectory.py --url http://127.0.0.1:8000/ --full-playback
```

O JSON `assets/6735-trajectory.json` preserva os centros sem suavização, identifica o hash do XML, as unidades, a matriz identidade e os tempos ausentes (`null`). O preparador rejeita frames ausentes, centros consecutivos repetidos e saltos acima de 5 m ou cinco vezes a mediana, exigindo revisão antes de ligar possíveis sessões. Neste XML o maior passo é 2,18 m; o caminho mede cerca de 270,13 m.

A linha de 3 pixels usa o Line2 oficial já incluído no vendor, aparece sobre os pontos e permanece na altura real da captura, com início verde, fim vermelho e marcador amarelo da visita. Sua visibilidade é opcional. A animação interpola linearmente os centros para preservar esquinas, avança pela distância acumulada a 4 m/s (aproximadamente 68 s) e olha 3 m adiante. É uma velocidade de apresentação, não uma reprodução do tempo original. Não se aplica suavização espacial que possa cortar esquinas. A API CameraAnimation incluída foi inspecionada; seu `play()` não oferece pausa/retomada, por isso um controlador próprio usa o evento `update` do Potree e mantém as bibliotecas oficiais intactas.

Há controles para iniciar, pausar/continuar, reiniciar, exploração livre, vista geral e mostrar/ocultar a trajetória. Iniciar ou continuar faz uma transição de 1,2 s da vista atual até a posição guardada, sem avançar o progresso durante essa transição. Essa transição de retorno não representa um trecho da captura. Entradas manuais no visualizador pausam a visita; menu, troca de puxador e aba do navegador oculta também a interrompem. No celular, os controles EXPLORAR NUVEM/VOLTAR À ROLAGEM continuam disponíveis. A publicação inclui o JSON em `assets/`, mantendo o XML original fora do pacote do Pages.

## Referência de eixos — 6735

O PUXADOR 4 possui uma referência XYZ ancorada na origem mundial `(0, 0, 0)`, com X vermelho, Y verde e Z azul, setas positivas, semieixos negativos discretos e letras voltadas à câmera. A opção **MOSTRAR EIXOS XYZ** permite ocultá-la. O marcador ajusta apenas seu próprio tamanho visual com o zoom para manter a legibilidade; não é uma régua. Não altera posições, offsets, escalas ou orientação das nuvens, nem o percurso guiado. Ele fica oculto no menu e nos outros puxadores.

## Rotação de exibição — 6735

O conjunto do PUXADOR 4 é exibido com **+45° em torno do eixo Y mundial**, tendo `(0, 0, 0)` como pivô. O sentido é anti-horário visto de +Y em direção à origem. A mesma matriz é aplicada uma única vez aos 17 trechos e às 240 posições da trajetória, incluindo marcadores e os alvos da visita guiada. As origens exibidas dos trechos giram em torno do pivô comum; eles não são girados individualmente em seus centros. O enquadramento considera os limites transformados.

A configuração está em `rotationYDegrees: 45` no cadastro do PUXADOR 4. Os arquivos de nuvem, offsets de origem, XML e JSON bruto permanecem intactos; a rotação é aplicada apenas no carregamento para exibição. Os eixos XYZ continuam fixos como referência mundial, e os outros puxadores permanecem sem essa rotação. Os testes `check-6735.py` e `check-6735-trajectory.py` verificam as posições transformadas, a orientação dos trechos e o alinhamento da animação.

### Rotação adicional em X

Após os +45° em Y, o conjunto 6735 e o percurso recebem **+90° em X mundial**, anti-horário visto de +X em direção à origem. A composição única de exibição é `Rx(90°) × Ry(45°)`, em torno de `(0, 0, 0)`. `rotationXDegrees: 90` e `rotationYDegrees: 45` ficam no cadastro do PUXADOR 4. Nuvens, trajetória, marcadores e visita recebem a mesma composição, aplicada uma vez ao carregar. Os eixos de referência permanecem mundiais e os arquivos originais continuam intactos.

### Velocidade da visita

A velocidade de apresentação foi duplicada de 2 para **4 m/s**. O percurso de aproximadamente 270 m leva cerca de 68 segundos, além da transição inicial de 1,2 s. Isso altera apenas o avanço da visita guiada; os controles de exploração livre permanecem independentes.

### Câmera nivelada durante a visita

Durante a visita guiada, inclusive na transição de retorno, a câmera mantém inclinação vertical zero (`view.pitch = 0` no referencial Z vertical do Potree). O alvo do olhar fica na mesma altura da câmera; a direção horizontal acompanha as curvas do percurso. A câmera continua seguindo todas as posições 3D da trajetória, inclusive suas variações de altura. Pausar ou sair permite voltar a inclinar livremente a vista. O bloqueio não muda nuvens, rotação do conjunto ou coordenadas do percurso.

## Subpáginas dos puxadores — amostra

Após escolher um puxador, a barra sobre a nuvem oferece **Anterior**, contador e **Próxima**. O cadastro `assets/route-pages.js` representa as páginas do PDF: Guilherme 3–11 (9 subpáginas), Emily 12–14 (3), Tiago 15–16 (2) e Benne 17–22 (6). Cada página possui o mapa correspondente, com a posição luminosa original da referência. Relatos e fotografias são compartilhados dentro do mesmo puxador, como no PDF.

As subpáginas mantêm a nuvem e a vista atual, sem duplicar objetos, alterar transformações ou inventar posições 3D para cada mapa. Mudar de subpágina pausa uma visita guiada em andamento. A última página escolhida é lembrada ao reabrir um puxador na mesma sessão. Links como `#puxador-4/pagina-6` abrem diretamente a subpágina; voltar/avançar do navegador também restaura a seleção.

Para verificar navegação, limites, mapas, links diretos, histórico e preservação da cena:

```sh
python3 tools/check-subpages.py --url http://127.0.0.1:8000/
```

### Ajuste final de 5° horário em Y

A orientação anterior recebe mais **−5° em Y mundial**, no sentido horário visto de +Y em direção à origem. A composição atual é `Ry(−5°) × Rx(90°) × Ry(45°)`, com pivô em `(0, 0, 0)`. O campo `worldYAdjustmentDegrees: -5` é aplicado depois das rotações anteriores, tanto aos 17 point clouds quanto à trajetória, marcadores e visita guiada. Não equivale a alterar a primeira rotação em Y de 45° para 40°, pois há uma rotação em X entre elas. Os arquivos originais continuam intactos.

## Zoom com scroll em navegadores modernos

`assets/wheel-input.js` adapta o evento padrão `wheel` ao `InputHandler` oficial do Potree 1.8.2. O vendor escuta apenas `mousewheel` e `DOMMouseScroll`, que deixaram de ser emitidos pelo Chromium recente. A adaptação preserva a seleção de controles e objetos sob o cursor, suprime os eventos legados para evitar zoom duplicado e não altera os arquivos oficiais. Ctrl+scroll, movimentos só horizontais e input desativado não são consumidos. O zoom durante a visita guiada pausa a animação antes de encaminhar o scroll, preservando o primeiro movimento de zoom. A rolagem nativa do celular continua controlada pelos modos EXPLORAR NUVEM/VOLTAR À ROLAGEM.

```sh
python3 tools/check-wheel-zoom.py --url http://127.0.0.1:8012/
```

O teste usa scroll real do Chromium nas rotas com nuvens disponíveis e verifica aproximação/afastamento, eventos legados duplicados, input desativado, Ctrl+scroll e saída da visita guiada. A compatibilidade dos eventos antigos é simulada; isso não equivale a executar o Firefox.
