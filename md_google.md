# Guia de Boas Práticas de CSS (Google/Material-Inspired)

Este guia resume práticas recomendadas inspiradas por Google/Material Design e padrões modernos para manter o CSS sustentável e consistente.

## 1. Filosofia
- Componentes antes de páginas; utilidades pequenas e previsíveis
- Sem `!important` (evite salvo em correções temporárias) 
- CSS determinístico: seletores específicos, sem heranças agressivas
- Preferir variáveis CSS para tema e tokens

## 2. Estrutura
- Tokens: cores, espaçamentos, sombras, raios, tipografia
- Utilidades: classes atômicas previsíveis (.u-*)
- Componentes: blocos com BEM (`.block__element--modifier`)
- Páginas: estilos específicos mínimos

## 3. Nomenclatura
- BEM aproximado: `.card`, `.card__header`, `.card--highlight`
- Sem encadeamento profundo (máx. 3 níveis)

## 4. Especificidade
- Evite estilos globais no `*` e `body *`
- Não estilize tags puras (ex.: `input {}`) sem contexto de classe do sistema
- Use classes dedicadas: `.input`, `.btn-brand`, `.login__body`

## 5. Layout/Responsivo
- Mobile first com media queries progressivas
- Use Flex/Grid de forma explícita nos componentes

## 6. Desempenho
- Um único arquivo `static/css/style.css` minificado em produção
- Evitar reflows com mudanças pesadas

## 7. Acessibilidade
- Contraste suficiente, foco visível, tamanhos tocáveis (48px area)

## 8. Processo
- Antes de criar um novo estilo, busque utilidades/componentes existentes
- Evite estilos inline; mantenha tudo no stylesheet

## 9. Cores do Tema
- Roxo mantido: `--brand-start: #667eea`, `--brand-end: #764ba2`

## 10. Revisões
- Toda alteração de CSS deve citar o componente afetado e motivação.

