# 25 de Março — Potree

Instalação estática do [Potree oficial](https://github.com/potree/potree), tag `1.8.2`, commit `3013577379b5c8530ebca3cdc980f7585ae2320f`.

`vendor/potree-1.8.2/` contém as bibliotecas oficiais e o build sem alterações locais. `index.html` deriva de `examples/lion.html`; a nuvem inicial é a demonstração oficial `lion_takanawa`. As nuvens `25 de março` e `6716-cloud` permanecem em `pointclouds/`, sem serem carregadas nesta base limpa.

## Executar

Na raiz do repositório:

```sh
python3 -m http.server 8000
```

A demonstração Lion usa arquivos individuais, sem precisar de suporte HTTP Range. As nuvens no formato Potree 2.0 precisam de um servidor compatível com Range.

## Reproduzir os arquivos oficiais

Clone `https://github.com/potree/potree` na tag `1.8.2` em uma pasta separada, execute `npm ci` e confirme os arquivos gerados em `build/potree/`. Copie `build/potree/`, `libs/` e `LICENSE` para a pasta versionada de `vendor/`. A página foi adaptada do exemplo oficial apenas para caminhos locais, título, idioma e fundo.

## Publicação

No GitHub Pages, a origem deve ser a branch `main`, pasta `/ (root)`. `.nojekyll` mantém a publicação estática. O envio para `main` não confirma, por si só, que o deploy terminou.
