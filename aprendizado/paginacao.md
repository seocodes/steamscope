# Paginação no scraper: como pensar do zero

Este documento explica a lógica da paginação (3 páginas de specials da Steam), as decisões de arquitetura e um exercício mental para treinar o raciocínio antes de codar.

## Pensamento passo a passo (do zero)

1. **Defina o objetivo operacional.** “Quero buscar *N* páginas, em ordem, e extrair os jogos de cada uma”.  
2. **Separe responsabilidades.**  
   - Buscar HTML de **uma** página (rede + retry).  
   - Extrair jogos **de um** HTML (parsing).  
   - Orquestrar **várias** páginas (loop + logs + dedup).  
3. **Decida onde fica o loop.** O loop pertence à camada de orquestração (main ou função “run”). Assim `fetch_page` continua simples e reutilizável.  
4. **Planeje deduplicação entre páginas.** O mesmo jogo pode aparecer em páginas diferentes; use um `seen_urls` compartilhado.  
5. **Inclua limites e respeito ao servidor.** Delay entre páginas evita bloqueios e mantém o scraping estável.

## Mudanças de paginação (o que muda e por quê)

### 1) `fetch_page` recebe o número da página
**Motivo:** manter a função de rede focada em uma página.  

```py
def fetch_page(page=1, max_retries=3, timeout=10):
    base_url = "https://store.steampowered.com/search/?specials=1"
    url = f"{base_url}&page={page}" if page > 1 else base_url
```

### 2) Deduplicação entre páginas
**Motivo:** evitar jogos repetidos quando a Steam “reordena” resultados.  

```py
def scrape_deals(page, rate_limit_delay=1, seen_urls=None):
    if seen_urls is None:
        seen_urls = set()
```

### 3) Loop de páginas no ponto de orquestração
**Motivo:** é a camada que decide fluxo, ordem, logs e o que fazer quando uma página falha.  

```py
total_pages = 3
all_records = []
seen_urls = set()

for page_number in range(1, total_pages + 1):
    page = fetch_page(page=page_number, max_retries=3, timeout=10)
    if page is None:
        continue
    page_records = scrape_deals(page, rate_limit_delay=1, seen_urls=seen_urls)
    all_records.extend(page_records)
```

### 4) Pequeno delay entre páginas
**Motivo:** reduzir risco de bloqueio (Steam pode limitar requests em sequência).  

```py
if page_number < total_pages:
    time.sleep(1)
```

## Exercício mental (para pensar sozinho)

**Cenário:** você quer subir de 3 para 5 páginas, mas precisa parar cedo se uma página vier vazia.

1. Onde você colocaria a regra “parar cedo”?  
2. Como você logaria o motivo da parada?  
3. Você quebraria o loop (`break`) ou marcaria um estado?  
4. O que muda em `fetch_page` (se é que muda)?

**Resposta esperada:**  
O loop é o ponto certo para essa regra, porque ele controla o fluxo. `fetch_page` continua sendo “uma página por vez”. Quando uma página vier vazia, você decide no loop se deve encerrar o scraping daquela execução.

## Checklist mental rápido (antes de codar)

1. “Qual função só busca HTML?”  
2. “Qual função só extrai dados?”  
3. “Onde o loop faz mais sentido?”  
4. “Dedup é por página ou por execução?”  
5. “Preciso respeitar rate limit entre páginas?”

---

Se você quiser, posso transformar esse raciocínio em um patch pronto mais tarde — mas a ideia é você conseguir aplicar a mudança de forma consciente.
