# 5. Como um desenvolvedor experiente pensa (e como você pode imitar)

Você disse que quer **escrever você mesmo** e usar IA só às vezes. Este capítulo é sobre o **processo**, não sobre decorar sintaxe.

---

## 1. Comece pelo problema, não pelo código

**Pergunta do projeto:** *“Como saber se um desconto é bom?”*

Quebra em pedaços menores:

| Pedaço | Pergunta |
|--------|----------|
| Dados | De onde vêm os preços antigos? |
| Armazenamento | Onde guardo dia após dia? |
| Coleta automática | Como não depender de abrir o site manualmente? |
| Decisão | Quem compara preço novo vs histórico? |
| Interface | Como o jogador informa jogo e preço? |

Cada fase do `PLANNING.md` é **um pedaço**. Você não constrói o site antes de ter dados no banco — assim como não faz o telhado antes das paredes.

---

## 2. Uma função = uma responsabilidade

Exemplos no seu projeto:

- `fetch_page` — **só** baixa HTML
- `parse_game` — **só** extrai um jogo
- `validate_game_record` — **só** valida
- `insert_deals` — **só** salva

**Anti-padrão:** uma função gigante que baixa, parseia, valida, salva e manda email. Difícil de testar, difícil de consertar.

**Se você fosse refazer do zero:** escreva no papel os nomes das funções antes de implementar.

---

## 3. Dados como contrato

O dicionário do jogo é um **contrato** entre scraper e banco:

```python
{
  "title": str,
  "url": str,
  "original_price": float,
  "discounted_price": float,
  "discount_pct": int,
  "scraped_at": str  # ISO datetime
}
```

Se amanhã você adicionar `rating`, **todos** precisam saber: scraper preenche, validação aceita, banco guarda.

Desenvolvedores experientes perguntam: *“Quem produz esse campo? Quem consome?”*

---

## 4. Falhas são normais — desenhe para elas

| Situação | O que o projeto faz |
|----------|---------------------|
| Steam fora do ar | `fetch_page` tenta 3 vezes |
| Um jogo sem título | `parse_game` retorna `None`, continua os outros |
| Preço estranho | `validate_game_record` barra |
| Scrape diário falhou | Scheduler loga e espera o próximo dia |

**Regra:** um jogo ruim não pode derrubar os 40 bons.

---

## 5. Ambiente e segredos

- Senhas no `.env`, nunca no código
- Dependências no `pyproject.toml` + `uv sync`
- Rodar com `uv run`

Isso não é frescura — é o que evita o erro `No module named 'dotenv'`.

---

## 6. Como estudar um arquivo que você não escreveu

1. Leia o `if __name__ == "__main__"` (ou `main.py`) — **ponto de entrada**
2. Siga as chamadas de função como um mapa
3. Anote inputs e outputs de cada função
4. Rode com log e veja na prática
5. Mude **uma coisa pequena** (ex: mensagem de log) e rode de novo

---

## 7. Como usar IA sem parar de aprender

**Bom pedido à IA:**

> “Estou na Fase 4. Quero que `fetch_page` aceite `page_num`. Já tenho o loop em mente. Me explique o que mudar em `fetch_page` e onde chamar no `scraper.py`, sem escrever o arquivo inteiro.”

**Pedido que ensina pouco:**

> “Implementa a paginação completa.”

**Depois que receber código:** leia linha por linha, digite você mesmo no editor, rode, quebre de propósito, conserte.

Para o **front-end** (HTML/CSS), pedir um rascunho e depois **alterar textos e layout você mesmo** é um meio-termo saudável.

---

## 8. Ordem mental para construir qualquer feature nova

1. **Entrada** — o que o usuário ou o sistema fornece?
2. **Saída** — o que precisa existir no final?
3. **Passos** — lista numerada em português
4. **Função por passo** — nome + arquivo
5. **Teste mínimo** — um comando ou print que prova que funcionou
6. **Só então** código

Exemplo Fase 7 (`context.py`):

- Entrada: nome do jogo + preço proposto
- Saída: JSON com média, mínimo, últimos 5 registros
- Passos: buscar no Mongo → calcular → montar dict
- Teste: `uv run python scripts/print_context.py "Elden Ring"`

---

## 9. Você já está no caminho certo

Ter validação, logs, agendador e banco separado **não é projeto de iniciante mal feito** — são escolhas sensatas. O que falta é **volume de dados** (Fase 6) e as features novas (4, 7, 8), construídas no mesmo estilo: pequeno, testável, uma função por vez.

Próximo: [06-proximas-fases-passo-a-passo.md](06-proximas-fases-passo-a-passo.md)
