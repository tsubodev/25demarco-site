# 25 de Março — Potree

Instalação estática do [Potree oficial](https://github.com/potree/potree), tag `1.8.2`, commit `3013577379b5c8530ebca3cdc980f7585ae2320f`.

`vendor/potree-1.8.2/` contém as bibliotecas oficiais e o build sem alterações locais. `index.html` usa a integração do exemplo oficial como base. Os conjuntos da planilha ficam em `pointclouds/`, organizados por puxador e código.

## Executar

Na raiz do repositório:

```sh
python3 -m http.server 8000
```

As cópias estáticas usam arquivos individuais e dispensam suporte a requisições HTTP Range. Os originais em Potree 2.0 continuam preservados.

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
| 1 · Guilherme | GPBK6717 (3 trechos), GPBK6718 (7 trechos), GPBK6719 (12 trechos), GPBK6720 (5 trechos), GPBK6722 (7 trechos), GPBK6723 (11 trechos) | GPBK6721, GPBK6724 a GPBK6726 |
| 2 · Emily | — | GPBK627, GPBK6728, GPBK6729, GB016730, GPBK6730 |
| 3 · Thiago | — | GPBK6732 |
| 4 · Benny (Benne no site) | GPBK6735 (17 trechos) | GPBK6733, GPBK6734, GPBK6736 |

Ao importar uma nuvem, use `pointclouds/puxador-<número>/<código>/original/` para os arquivos recebidos e `pointclouds/puxador-<número>/<código>/static/` para a cópia de exibição. Preencha `sources` no item correspondente com objetos `{ "url": "pointclouds/.../cloud.js", "name": "..." }`. O caminho deve apontar para um descritor existente. O empacotamento inclui as pastas desses descritores. Se faltar uma nuvem, a página continua acessível com texto, mapa e fotos. Os momentos de Thiago foram calibrados na 6719 e precisarão de novas posições para a GPBK6732.

Para preparar novos datasets no mesmo formato estático, preservando os originais:

```sh
python3 tools/prepare_point_cloud.py pointclouds/puxador-1/6718/original/6718.1_converted pointclouds/puxador-1/6718/static/6718.1_converted
```

As configurações ADAPTIVE, CIRCLE, 0.25 e EDL desligado se aplicam a todos os percursos. As nuvens são carregadas sob demanda e mantidas em cache; retornar a uma página não duplica seu point cloud. O enquadramento usa apenas o percurso selecionado.

## Conjunto 6717

Os três trechos da GPBK6717 ficam em `pointclouds/puxador-1/6717/original/`, com cópias para exibição em `pointclouds/puxador-1/6717/static/`. São 3.710.770 pontos. O Puxador 1 abre com a 6717 e seus três trechos juntos. A barra **Anterior / Próxima** permite alternar entre os conjuntos de Guilherme no mesmo visualizador, exibindo um conjunto por vez. As coordenadas de cada arquivo são preservadas.

Para regenerar as cópias estáticas:

```sh
for segment in 6717.11_converted 6717.12_converted 6717.2_converted; do
  python3 tools/prepare_point_cloud.py "pointclouds/puxador-1/6717/original/$segment" "pointclouds/puxador-1/6717/static/$segment"
done
```

## Conjunto 6718

A GPBK6718 é composta por sete trechos e soma 5.790.014 pontos. Os originais ficam em `pointclouds/puxador-1/6718/original/`, e as cópias para exibição, em `pointclouds/puxador-1/6718/static/`. Na segunda etapa de Guilherme, os sete trechos são exibidos juntos no Puxador 1.

## Conjuntos 6720, 6722 e 6723

As etapas 4, 6 e 7 de Guilherme exibem a GPBK6720, a GPBK6722 e a GPBK6723, respectivamente. Os originais ficam em `pointclouds/puxador-1/<código>/original/`, e as cópias para exibição, em `pointclouds/puxador-1/<código>/static/`. Os 23 trechos mantêm suas coordenadas de origem.

## Conjunto 6719

Os 12 diretórios recebidos foram movidos de `6719/` para `pointclouds/puxador-1/6719/original/`, sem editar seu conteúdo. A cópia para exibição fica em `pointclouds/puxador-1/6719/static/`; são **11.321.028 pontos** no total.

Todos os trechos são carregados juntos no PUXADOR 1 (Guilherme) quando a GPBK6719 está selecionada no visualizador Potree. As coordenadas e os offsets de origem de cada trecho são preservados; não há translação dos point clouds para zero, troca de eixos ou mudança de escala. O enquadramento existente considera o conjunto selecionado, sem alterar a origem dos dados.

Para reproduzir os arquivos de exibição:

```sh
python3 tools/prepare-6719.py
python3 tools/check-6719.py --url http://127.0.0.1:8000/
```

`project42_converted` fornece `octree.zip`. O preparador lê `octree.bin` de dentro desse ZIP em memória, preservando o arquivo original compactado no Git. Os atributos completos permanecem nos originais; a exibição exporta posições e RGB, com erro de quantização limitado a 0,00000005 unidade. A validação confere as posições dos 12 objetos Potree contra as origens recebidas, a renderização conjunta e a troca de páginas sem duplicar trechos.

## Conjunto 6735

O PUXADOR 4 carrega os 17 trechos da 6735 juntos. Os originais e `6735 cam.xml` ficam em `pointclouds/puxador-4/6735/original/`. As cópias de exibição ficam em `pointclouds/puxador-4/6735/static/`. São **8.012.558 pontos**. Cada trecho preserva as coordenadas, os offsets e a origem recebidos, sem translação para zero, troca de eixos ou mudança de escala. O XML é a fonte da trajetória descrita abaixo.

Para reproduzir e verificar:

```sh
python3 tools/prepare-6735.py
python3 tools/check-6735.py --url http://127.0.0.1:8000/
```

O preparador verifica todos os pontos e limita o erro de quantização a 0,00000005 unidade. A cópia estática exporta posições e RGB; os atributos completos permanecem nos originais. O teste verifica as 17 origens, a renderização e a troca de percursos sem duplicação.

## Dados de referência da 6735

O XML original em `pointclouds/puxador-4/6735/original/6735 cam.xml` contém 240 posições de câmera. O script `tools/prepare-6735-trajectory.py` permite extrair essas posições para análise. Na etapa 3 de Benne, o site oferece exploração livre da nuvem.

## Rotação de exibição — 6735

O conjunto do PUXADOR 4 é exibido com **+45° em torno do eixo Y mundial**, tendo `(0, 0, 0)` como pivô. O sentido é anti-horário visto de +Y em direção à origem. A mesma matriz é aplicada uma única vez aos 17 trechos. As origens exibidas dos trechos giram em torno do pivô comum; eles não são girados individualmente em seus centros. O enquadramento considera os limites transformados.

A configuração está em `rotationYDegrees: 45` no cadastro do PUXADOR 4. Os arquivos de nuvem, offsets de origem, XML e JSON bruto permanecem intactos; a rotação é aplicada apenas no carregamento para exibição. O teste `check-6735.py` verifica as posições transformadas e a orientação dos trechos.

### Rotação adicional em X

Após os +45° em Y, o conjunto 6735 recebe **+90° em X mundial**, anti-horário visto de +X em direção à origem. A composição única de exibição é `Rx(90°) × Ry(45°)`, em torno de `(0, 0, 0)`. `rotationXDegrees: 90` e `rotationYDegrees: 45` ficam no cadastro do PUXADOR 4. Os arquivos originais continuam intactos.

## Etapas dos puxadores

A barra **Anterior / Próxima** segue as posições do catálogo Fusion 1. O Puxador 1 tem 10 etapas, Emily tem 5, Thiago tem 1 e Benne tem 4. Cada etapa abre apenas a nuvem correspondente. Os trechos de uma mesma nuvem são exibidos juntos e as associações pendentes mostram o código que aguarda importação. A GPBK6735 está na etapa 3 de Benne.

Os mapas de `assets/route-pages.js` acompanham as etapas pela posição na lista. Uma etapa sem mapa mostra o relato e as fotos. As referências do PDF que excedem a quantidade de etapas ficam disponíveis nos arquivos para uso futuro. Links como `#puxador-4/pagina-3` abrem diretamente uma etapa. Voltar e avançar no navegador também restaura a nuvem e o mapa correspondentes.

```sh
python3 tools/check-subpages.py --url http://127.0.0.1:8000/
```

### Ajuste final de 5° horário em Y

A orientação anterior recebe mais **−5° em Y mundial**, no sentido horário visto de +Y em direção à origem. A composição atual é `Ry(−5°) × Rx(90°) × Ry(45°)`, com pivô em `(0, 0, 0)`. O campo `worldYAdjustmentDegrees: -5` é aplicado depois das rotações anteriores, aos 17 point clouds. Não equivale a alterar a primeira rotação em Y de 45° para 40°, pois há uma rotação em X entre elas. Os arquivos originais continuam intactos.

## Zoom com scroll em navegadores modernos

`assets/wheel-input.js` adapta o evento padrão `wheel` ao `InputHandler` oficial do Potree 1.8.2. O vendor escuta apenas `mousewheel` e `DOMMouseScroll`, que deixaram de ser emitidos pelo Chromium recente. A adaptação preserva a seleção de controles e objetos sob o cursor, suprime os eventos legados para evitar zoom duplicado e não altera os arquivos oficiais. Ctrl+scroll, movimentos só horizontais e input desativado não são consumidos. A rolagem nativa do celular continua controlada pelos modos EXPLORAR NUVEM/VOLTAR À ROLAGEM.

```sh
python3 tools/check-wheel-zoom.py --url http://127.0.0.1:8012/
```

O teste usa scroll real do Chromium nas rotas com nuvens disponíveis e verifica aproximação/afastamento, eventos legados duplicados, input desativado, e Ctrl+scroll. A compatibilidade dos eventos antigos é simulada; isso não equivale a executar o Firefox.
