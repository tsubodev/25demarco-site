# 25 de Março — Potree

Instalação estática do [Potree oficial](https://github.com/potree/potree), tag `1.8.2`, commit `3013577379b5c8530ebca3cdc980f7585ae2320f`.

`vendor/potree-1.8.2/` contém as bibliotecas oficiais e o build sem alterações locais. `index.html` usa a integração do exemplo oficial como base; a nuvem é `6716-static-v2`, preparada a partir do arquivo original `6716-cloud`. A nuvem `25 de março` e o arquivo original `6716-cloud` permanecem preservados em `pointclouds/`. As nuvens de demonstração foram removidas.

## Executar

Na raiz do repositório:

```sh
python3 -m http.server 8000
```

A nuvem 6716 usa arquivos individuais, sem precisar de suporte HTTP Range. Para regenerar a cópia de exibição, execute `python3 tools/prepare-6716.py`. O script preserva os 211.969 pontos, exporta posições e RGB e verifica a contagem e o erro máximo de posição (0,00000005 unidade). Os atributos originais permanecem intactos em `6716-cloud`. As nuvens no formato Potree 2.0 precisam de um servidor compatível com Range.

## Reproduzir os arquivos oficiais

Clone `https://github.com/potree/potree` na tag `1.8.2` em uma pasta separada, execute `npm ci` e confirme os arquivos gerados em `build/potree/`. Copie `build/potree/`, `libs/` e `LICENSE` para a pasta versionada de `vendor/`. A integração usa a base do exemplo oficial, com uma interface própria em `assets/interface.css` e `assets/interface.js`. As bibliotecas oficiais não foram modificadas.

## Publicação

No GitHub Pages, a origem deve ser a branch `main`, pasta `/ (root)`. `.nojekyll` mantém a publicação estática. O envio para `main` não confirma, por si só, que o deploy terminou.

## Interface alpha

O site inicia em **START MENU**, conforme as referências visuais. A opção **PUXADOR 1** abre a nuvem 6716, **PUXADOR 2** abre a 6718 e **PUXADOR 3** reúne os 12 trechos da 6719 no mesmo visualizador. PUXADOR 4 mostra um aviso de percurso ainda não disponível. Cada página carrega apenas seu próprio conjunto; ao trocar de página, apenas os trechos do percurso selecionado ficam visíveis. Os nomes pessoais continuam provisórios. O botão MENU permite retornar à seleção; Escape alterna o menu depois que o percurso é aberto. O Potree é inicializado apenas ao entrar no percurso.

O layout usa roxo, amarelo-claro, títulos em itálico e degradê na abertura. A área do Potree mantém fundo branco, Eye-Dome Lighting desligado, tamanho 0.25, sizing ADAPTIVE e shape CIRCLE. A coluna lateral tem espaços identificados para o mapa e quatro fotografias. Título, nomes e conteúdo definitivo ainda são provisórios. Os créditos seguem a referência fornecida. O menu nativo do Potree permanece desativado.

Em telas maiores, a coluna de informações rola independentemente do visualizador. No celular, os painéis ficam empilhados. Inicialmente, deslizar sobre a nuvem rola a página. O botão **EXPLORAR NUVEM** ativa os gestos 3D; **VOLTAR À ROLAGEM** libera novamente a página. Substitua os espaços de imagem por arquivos com textos alternativos quando os materiais separados estiverem disponíveis.

Para verificar a navegação, as configurações da nuvem e os tamanhos de tela (1450, 390 e 375 px), com Playwright e Chromium disponíveis:

```sh
python3 tools/check-interface.py --url http://127.0.0.1:8000/
```

O teste também verifica a ausência de erros HTTP/JavaScript, o retorno ao menu e a associação da nuvem ao PUXADOR 1 e a navegação sem duplicar nuvens. Capturas de tela ficam em `/tmp/25demarco-ui-check/`.

## Cadastro de point clouds por puxador

As páginas são independentes e o vínculo fica em `assets/point-clouds.js`:

| Página do menu | Point cloud |
| --- | --- |
| PUXADOR 1 | 6716 (disponível) |
| PUXADOR 2 | 6718 (disponível) |
| PUXADOR 3 | 6719 — 12 trechos alinhados (disponível) |
| PUXADOR 4 | Reservado para um novo arquivo |

Uma entrada `null` exibe “O percurso deste puxador será adicionado em breve” e não carrega a nuvem de outro puxador. Ao receber um novo dataset, prepare seus arquivos em uma pasta própria e preencha o cadastro da página correspondente com `url` e `name`. Preserve os arquivos das outras páginas.

Para preparar novos datasets no mesmo formato estático, preservando os originais:

```sh
python3 tools/prepare_point_cloud.py pointclouds/6718-cloud pointclouds/6718-static
```

A nuvem 6718 contém 490.330 pontos. As configurações ADAPTIVE, CIRCLE, 0.25, fundo branco e EDL desligado se aplicam a todos os percursos. As nuvens são carregadas sob demanda e mantidas em cache; retornar a uma página não duplica seu point cloud. O enquadramento usa apenas o percurso selecionado.

## Conjunto 6719

Os 12 diretórios recebidos foram movidos de `6719/` para `pointclouds/6719/original/`, sem editar seu conteúdo. A cópia para exibição fica em `pointclouds/6719/static/`; são **11.321.028 pontos** no total.

Todos os trechos são carregados juntos no PUXADOR 3, em um único visualizador Potree. As coordenadas e os offsets de origem de cada trecho são preservados; não há translação dos point clouds para zero, troca de eixos ou mudança de escala. O enquadramento existente considera o conjunto selecionado, sem alterar a origem dos dados.

Para reproduzir os arquivos de exibição:

```sh
python3 tools/prepare-6719.py
python3 tools/check-6719.py --url http://127.0.0.1:8000/
```

`project42_converted` fornece `octree.zip`. O preparador lê `octree.bin` de dentro desse ZIP em memória, preservando o arquivo original compactado no Git. Os atributos completos permanecem nos originais; a exibição exporta posições e RGB, com erro de quantização limitado a 0,00000005 unidade. A validação confere as posições dos 12 objetos Potree contra as origens recebidas, a renderização conjunta e a troca de páginas sem duplicar trechos.
