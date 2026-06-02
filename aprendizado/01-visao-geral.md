# 1. Visão geral do projeto

## O que é o steamscope?

Imagine um **caderno de anotações automático** sobre promoções da Steam:

1. Todo dia (ou quando você rodar manualmente), o programa **visita** a página de ofertas da Steam.
2. **Lê** o HTML como um humano leria a lista de jogos — título, preço, desconto, link.
3. **Guarda** cada jogo no **MongoDB** (banco na nuvem), com a data da coleta.
4. No futuro, um **site simples** vai usar esse histórico + **Gemini** (IA do Google) para dizer se um desconto que *você* viu é bom ou não.

Você não precisa decorar nomes de bibliotecas. O fluxo mental é:

```
Steam (site) → extrair dados → validar → salvar no banco → (depois) analisar → site + IA
```

---

## O que já está pronto (hoje)

| Fase | Status | Em português |
|------|--------|----------------|
| 1 — Setup | Feito | Pastas, dependências, `.env` |
| 2 — Scraper (1 página) | Feito | Baixa e interpreta **uma** página de ofertas |
| 3 — MongoDB | Feito | Salva os jogos no Atlas |
| 4 — Paginação | Feito | Várias páginas por execução (~100 jogos) |
| 5 — Agendador | Feito | Roda sozinho todo dia no horário que você configurar |
| 6 — Coleta de dados | Não começou | Deixar rodando dias para ter histórico |
| 7 — Contexto JSON | Feito | Resumir histórico de um jogo para a IA |
| 8 — Site + Gemini | Em andamento | Gemini pronto; site pendente |

---

## Pastas e arquivos (mapa mental)

```
steamscope/
├── main.py                 → “Liga o despertador” (agendador diário)
├── application/
│   ├── scraper.py          → Vai na Steam, extrai jogos, valida
│   ├── db.py               → Fala com o MongoDB (salvar / depois consultar)
│   ├── scheduler.py        → Combina scraper + banco + horário fixo
│   ├── context.py          → Monta o JSON de contexto do jogo
│   └── gemini_advisor.py   → Chama o Gemini e devolve o veredito
├── .env                    → Senhas e URLs (NUNCA commitar)
├── pyproject.toml          → Lista de bibliotecas do projeto
├── PLANNING.md             → Roteiro técnico (inglês, para o projeto)
├── README.md               → Apresentação do projeto (inglês)
└── aprendizado/            → Estes guias (só no seu PC)
```

**Regra importante:** quase toda a “inteligência” do scraping está em `scraper.py`. O banco é só armazenamento. O agendador só **chama** o scraper no horário certo.

---

## O “documento” de cada jogo no MongoDB

Cada vez que um jogo aparece numa coleta, vira um registro parecido com:

```json
{
  "title": "Nome do Jogo",
  "original_price": 99.99,
  "discounted_price": 49.99,
  "discount_pct": 50,
  "url": "https://store.steampowered.com/app/...",
  "scraped_at": "2026-05-26T16:00:00"
}
```

O mesmo jogo pode ter **vários** registros em dias diferentes — isso é o que permite dizer “esse preço já foi mais barato antes”.

---

## Objetivo final (depois das fases 6–8)

**Cenário:** você vê Elden Ring por R$ 150 e quer saber se vale.

1. Abre o site do projeto.
2. Escolhe o jogo na lista (veio do seu banco).
3. Digita **150** como preço que você viu.
4. O sistema monta um JSON com histórico (menor preço já visto, média, etc.).
5. O Gemini lê esse JSON e responde algo como: *“Bom negócio — está perto do menor preço que você registrou.”*

Você vai **escrever** a parte de consulta ao banco e a lógica do JSON. Para o **front** (HTML bonito), pode pedir ajuda à IA algumas vezes — e está tudo bem, desde que você entenda o que o back-end faz.

---

## Próximo passo

Leia [02-como-rodar.md](02-como-rodar.md) antes de mexer no código. Rodar certo evita 90% dos erros de “módulo não encontrado”.
