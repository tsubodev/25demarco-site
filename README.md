# 25 de Março — Potree

Instalação estática do [Potree oficial](https://github.com/potree/potree), tag `1.8.2`, commit `3013577379b5c8530ebca3cdc980f7585ae2320f`.

`vendor/potree-1.8.2/` contém as bibliotecas oficiais e o build sem alterações locais. `index.html` deriva de `examples/lion.html`; a nuvem inicial é `6716-static-v2`, preparada a partir do arquivo original `6716-cloud`. A nuvem `25 de março` e o arquivo original `6716-cloud` permanecem preservados em `pointclouds/`. As nuvens de demonstração foram removidas.

## Executar

Na raiz do repositório:

```sh
python3 -m http.server 8000
```

A nuvem 6716 usa arquivos individuais, sem precisar de suporte HTTP Range. Para regenerar a cópia de exibição, execute `python3 tools/prepare-6716.py`. O script preserva os 211.969 pontos, exporta posições e RGB e verifica a contagem e o erro máximo de posição (0,00000005 unidade). Os atributos originais permanecem intactos em `6716-cloud`. As nuvens no formato Potree 2.0 precisam de um servidor compatível com Range.

## Reproduzir os arquivos oficiais

Clone `https://github.com/potree/potree` na tag `1.8.2` em uma pasta separada, execute `npm ci` e confirme os arquivos gerados em `build/potree/`. Copie `build/potree/`, `libs/` e `LICENSE` para a pasta versionada de `vendor/`. A página foi adaptada do exemplo oficial apenas para caminhos locais, título, idioma e fundo.

## Publicação

No GitHub Pages, a origem deve ser a branch `main`, pasta `/ (root)`. `.nojekyll` mantém a publicação estática. O envio para `main` não confirma, por si só, que o deploy terminou.
