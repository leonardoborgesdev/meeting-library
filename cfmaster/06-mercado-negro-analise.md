# Mercado Negro (Caixas / Tickets / Recompensas) — Análise + Plano de Port

> CrossFire BR Ilusion  →  CrossFire Master
> Análise **read-only** (não modifica cliente nem servidor). Data: 2026-06-13.
> Fontes: `C:\Users\Administrator\Desktop\BLACK MARKET CFMASTER\` (README + manifesto), banco `CF_PH_GAME` (somente leitura), e memória do projeto (`cfmaster-loja-itens-compra.md`, `cfmaster-onboarding-loja-fixes.md`).

---

## 0. Resumo executivo

O "mercado negro" do CF Master é a tela de **Mega Lotto / caixas premium** (gacha). Funcionalmente já existe e está saudável: o servidor tem **65 pools de gacha** (`GACHA_ID 0–64`), **324 grupos** (`CF_GACHA_GROUP`), **3518 linhas de prêmio** (`CF_GACHA_ITEM`) e **547 caixas** (`ITEM_TYPE='F'`, `FUNCTION4='21'`) cadastradas em `CF_ITEM_INFO`. A compra usa `SP_BUY_CASH_ITEM`/`SP_BUY_GPITEM` e a abertura usa `SP_CONFIRM_GACHA`. **Não existe** proc de "Free Point" (`GSP_BUY_FP_ITEM` nunca existiu em nenhum banco).

"Portar o mercado negro do BR Ilusion" = trazer as **famílias de caixas** listadas no README (Brazil, Red Dragon, Royal Dragon, …) que ainda não estão no CF Master. Para cada caixa: (1) ela precisa existir no **cliente** (`ITEM.CFT`/`ItemIcon`) para ser exibida e clicável; (2) precisa de uma **linha em `CF_ITEM_INFO`** com o `ITEM_ID` exato que o cliente manda, apontando para um **pool de gacha** (`FUNCTION5`); (3) o pool precisa ter prêmios em `CF_GACHA_ITEM`/`CF_GACHA_GROUP`. **Prêmio existente** no CF Master = só banco (linha de gacha apontando para um `ITEM_ID` já cadastrado). **Prêmio novo** = banco + cliente + assets.

> ⚠️ **Ressalva sobre as fontes:** os 6 docs do `_TUTORIAL/docs/` referenciados no README (`10_video_05_capsule_crate.md`, `10_video_08_AI_ticket.md`, `10_video_09_ZM_chest.md`, `20_TUTORIAL_MESTRE.md`, `61_caixas_blackmarket_cfmaster.md`, `60_MEMORIA_UPGRADE_CF_MASTER.md`) **não existem na VPS** — busquei recursivamente em todo `C:\Users\Administrator` e não há pasta `_TUTORIAL` nem esses arquivos. São referências penduradas (dangling) no README. Da mesma forma, **não há dump de dados do "BR Ilusion"** na VPS: a única especificação de port presente é o próprio README + `manifesto_caixas.csv`. Logo, a "fonte" da família de caixas a portar terá que vir do **cliente do BR Ilusion** (ITEM.xlsx/ITEM.CFT daquele build) — que precisa ser providenciado antes da execução. Esta análise descreve a **mecânica e o pipeline**; o conteúdo concreto por família depende dessa fonte.

---

## 1. O que é o mercado negro

No CF Master a feature aparece como **"Play Lotto" / Mega Lotto** (a memória chama de "mercado negro"). É a vitrine de **caixas premium (gacha)**:

- **Duas abas**: *eCoin Lotto* (paga em EC/cash) e *GP Lotto* (paga em GP), cada uma com ~5 páginas.
- Cada slot da vitrine é uma **CAIXA** = um item `ITEM_TYPE='F'` (funcional), `ITEM_ID` na faixa `9000xxxxxx`, normalmente vendida em 3 tiers (1EA / 5EA / 10EA → preços tipo 30 / 120 / 240 EC).
- Comprar a caixa **adiciona o item ao inventário** com um GAUGE (contador de jogadas). Abrir/jogar a caixa **consome 1 do GAUGE** e sorteia um prêmio do **pool de gacha** associado.

Componentes do "mercado negro":

| Componente | O que é | Onde vive |
|---|---|---|
| **Caixa premium** | Item vendável que, ao abrir, dispara o sorteio | `CF_ITEM_INFO` (banco) + cliente (vitrine/ícone) |
| **Ticket** | Item funcional (`Ixxxx`) — cupom/funcional/spray/muzzle, pode ser caixa, prêmio ou consumível | `CF_ITEM_INFO` (banco) + cliente |
| **Recompensa / prêmio** | O que sai no sorteio | `CF_GACHA_ITEM` aponta para um `ITEM_ID` que existe em `CF_ITEM_INFO` |
| **Gacha (pool/sorteio)** | A roleta em si: pools, grupos e taxas | `CF_GACHA_GROUP` + `CF_GACHA_ITEM` |

---

## 2. A regra `Ixxxx`

Do README: **`Ixxxx` = item de caixa, ticket ou funcional**.

Confirmado no banco: `ITEM_CODE LIKE 'I%'` retorna **1140 itens** — número idêntico à contagem de `ITEM_TYPE='F'` (1140). Ou seja, **todo item cujo `ITEM_CODE` começa com `I` é um item funcional `ITEM_TYPE='F'`** (caixas de lotto, cupons, sprays `[SP]`, muzzle fires, logos, packages). Exemplos reais:

```
I0001  [SP]BL Logo            F  G   (spray, GP)
I0072  Blue Muzzle Fire       F  ...
I0087  Lotto coupon [Lotto]   F  ...
I0088  Elite M4A1 Cash Lotto  F  C   (CAIXA: 1EA/5EA/10EA, FUNCTION4=21, FUNCTION5=0)
I0095  Elite AK-47 Lotto      F  C   (CAIXA: FUNCTION5=1)
```

Contraste com os outros prefixos: `Cxxxx` = arma/consumível (weapon `W`), `Bxxxx` = dress/equip de personagem, `Axxxx` = personagem (`C`). **A família `Ixxxx` é exatamente o domínio do mercado negro** — qualquer caixa/ticket nova a portar entra como `Ixxxx` / `ITEM_TYPE='F'`.

**Sub-regra das caixas (subset de `Ixxxx`):** uma caixa de lotto é um `Ixxxx` com:
- `ITEM_TYPE='F'`
- `FUNCTION4='21'` (constante = "é uma caixa de gacha")
- `FUNCTION5 = <GACHA_ID do pool de prêmios>` (0–64 hoje)
- `USE_EFFECT3 = nº de jogadas do tier` (1EA→1, 5EA→5, 10EA→10)
- `SALE_TYPE='C'` (eCoin) ou `'G'` (GP), `SALE_PLACE='C'`, `SALE_STATUS='O'`

Confirmado: **547 itens** têm `FUNCTION4='21' AND ITEM_TYPE='F'` (as caixas atualmente vendáveis).

---

## 3. Como o sorteio funciona (`CF_GACHA_ITEM` + `CF_GACHA_GROUP`)

### Esquema (verificado)

`CF_GACHA_GROUP` (324 linhas, define os "andares" do sorteio):

| Coluna | Tipo | Significado |
|---|---|---|
| SRL | int | id da linha |
| GACHA_ID | int | qual pool (0–64) |
| GROUP_ID | int | qual grupo dentro do pool (tier de raridade: 0,1,2,3) |
| WIN_RATE | float | peso do grupo no sorteio |
| CASH_TYPE | int | moeda (0/1/2/3 — variantes de cash/GP) |
| DROP_CNT | int | quantos itens caem (geralmente NULL/1) |

`CF_GACHA_ITEM` (3518 linhas, os prêmios individuais):

| Coluna | Tipo | Significado |
|---|---|---|
| SRL | int | id da linha |
| GACHA_ID | int | qual pool (0–64) |
| GROUP_ID | int | a qual grupo pertence |
| ITEM_ID | varchar(10) | **o prêmio** (FK lógica para `CF_ITEM_INFO.ITEM_ID`) |
| CASH_TYPE | int | moeda |
| WIN_RATE | float | peso do item dentro do grupo (ex.: 12.0, 0.5, 99.5) |
| CNT | int | quantidade entregue |
| DISPLAY | varchar(1) | `'Y'` aparece na vitrine de prêmios / `'N'` oculto |

### Estrutura observada

- **65 pools** (`GACHA_ID 0–64`); cada pool tem ~4 grupos (`GROUP_ID 0–3`) e ~40 prêmios por pool (10 por grupo × 4 grupos).
- O **2 níveis** funcionam como: o grupo é o tier de raridade (`WIN_RATE` do grupo decide qual tier sai), e dentro do tier o `WIN_RATE` do item decide qual prêmio.
- Cada combinação `(GACHA_ID, GROUP_ID)` aparece em `CF_GACHA_GROUP` repetida por `CASH_TYPE` (0,1,2,3) — o sistema escolhe a linha de grupo pela moeda usada.

Exemplo real (pool 0, grupo 0):
```
ITEM_ID     CODE   NAME                       WIN_RATE  DISPLAY
2010028601  C0234  Scar Heavy-Camo 7day        12.0      Y
9000004901  I0087  Lotto coupon [Lotto]        99.5      Y     <- prêmio "consolo" alto
2010011801  C0065  Elite M4A1 Permanent         0.5      Y     <- prêmio raro
2010018801  C0136  Anaconda-Black               0.5      Y
9000010401  I0072  Blue Muzzle Fire 7day       20.5      Y
```

### Fluxo de execução (compra + abertura)

1. **Comprar a caixa** → cliente manda o `ITEM_ID` exato da caixa → `SP_BUY_CASH_ITEM @usn,'11',@boxid,'F','-','-','N',-1` (ou `SP_BUY_GPITEM`). Debita EC/GP, insere em `CF_USER_INVENTORY` com `GAUGE` = tier (1/5/10).
2. **Abrir/jogar** → `SP_CONFIRM_GACHA`:
   - `UPDATE CF_USER_INVENTORY SET GAUGE=GAUGE-1 WHERE inventory_srl=@p`; se `GAUGE-1 < 0` → retorno `-1/-6` → "failed to purchase".
   - sorteia em `CF_GACHA_GROUP`/`CF_GACHA_ITEM` pelo `GACHA_ID` e entrega o prêmio (insere no inventário).
   - **GOTCHA confirmado na memória:** o `GACHA_ID` usado na abertura vem do **CLIENTE**, não da coluna `FUNCTION5` da caixa. Ou seja, cliente e banco têm que concordar no `GACHA_ID`. Se o cliente mandar um pool e o banco esperar outro, sai prêmio errado ou erro.

> Procs presentes (verificado): `SP_BUY_CASH_ITEM`, `SP_BUY_GPITEM`, `SP_CONFIRM_GACHA`, `SP_CF_GACHA_RARE` (+ versões datadas legadas). **Não existe** `GSP_BUY_FP_ITEM` nem qualquer proc de Free Point.

---

## 4. Cliente vs Banco — o que cada lado precisa

| Necessidade | Cliente (`RB001.REZ` / `ITEM.CFT` / `ITEM.xlsx` / ItemIcon) | Banco (`CF_PH_GAME`) |
|---|---|---|
| Caixa aparecer na vitrine do lotto | ✔ bloco no config do Mega Lotto + ícone | — |
| Caixa ser clicável/comprável (mandar o ID certo) | ✔ `ITEM_ID` exato no bloco da caixa (`GachaShopAttr 1`, `Func4 21`, `Func5`=pool, `CashItem`, `MaxUseCount`) | ✔ linha em `CF_ITEM_INFO` com **o MESMO `ITEM_ID`** |
| Caixa de fato comprar | — | ✔ `SALE_STATUS='O'`, `SALE_TYPE` C/G, `SALE_PLACE='C'`, datas válidas, `ITEM_INFO<>'D'` |
| Caixa abrir e sortear | ✔ `GACHA_ID` no config (o cliente manda na abertura) | ✔ pool em `CF_GACHA_ITEM`/`CF_GACHA_GROUP` |
| Prêmio existir/ser entregue | ✔ **só se o prêmio for novo** (modelo/ícone) | ✔ `CF_GACHA_ITEM.ITEM_ID` aponta para `ITEM_ID` que existe em `CF_ITEM_INFO` |
| Prêmio renderizar na partida (arma) | ✔ `ITEM_INDEX` (modelo), categoria correta | ✔ `ITEM_CATEGORY1/2` correta (fuzil=`M/R`, etc.); VVIP exige tabela `CF_VVIP_ITEM_INFO` |

**Regra-chave (memória, comprovada):** o vínculo da compra é por **`ITEM_ID` exato do cliente**, não pelo `ITEM_CODE`. Se o servidor não tiver a linha com aquele `ITEM_ID`, a compra **falha no cliente, antes de chegar no banco** (nada aparece em `cash_*.log`).

### Prêmio existente (só banco) vs prêmio novo (banco + cliente + assets)

- **Prêmio já existe no CF Master** (a arma/item já está em `CF_ITEM_INFO` e o cliente já a conhece): basta **um INSERT em `CF_GACHA_ITEM`** apontando para esse `ITEM_ID`, com `GACHA_ID/GROUP_ID/WIN_RATE/DISPLAY`. Zero trabalho de cliente/asset. **Caminho preferido** para começar.
- **Prêmio novo** (arma/item que o CF Master ainda não tem): precisa do pipeline completo de item custom — modelos/ícones no cliente (`RF0xx`/`BUTES`/`ITEM.CFT`), linha em `CF_ITEM_INFO` com `ITEM_INDEX` dentro do limite do cliente (BF011 ≤1059, BF005 ≤897), **e** a linha em `CF_GACHA_ITEM`. Se for VVIP, exige `CF_VVIP_ITEM_INFO`. Muito mais caro e arriscado (limite de ~2900 itens no executável, crash de carga por zero-byte/range — ver §7).

---

## 5. Ordem de prioridade das famílias (README)

O README e o `manifesto_caixas.csv` definem a ordem de port. As 8 primeiras estão marcadas **`alta`** no CSV; as demais **`media`**:

| # | Família | Prioridade (CSV) |
|---|---|---|
| 1 | Brazil | alta |
| 2 | Red Dragon | alta |
| 3 | Royal Dragon | alta |
| 4 | Black Dragon / Gold Black Dragon | alta |
| 5 | Gold Phoenix | alta |
| 6 | Ultimate Gold / Ultimate Goldsmith | alta |
| 7 | Noble Gold | alta |
| 8 | Beast / Iron Beast | alta |
| 9 | VIP / VVIP | media |
| 10 | Knight Blue | media |
| 11 | Magma | media |
| 12 | Ares | media |
| 13 | Shadow | media |
| 14 | Blue Power | media |
| 15 | Tactical Sniper | media |
| 16 | Super Deadly Shot | media |
| 17 | Golden Knife | media |
| 18 | Graffiti | media |
| 19 | Rival Factions | media |

**Escopo declarado (README):** caixas premium, tickets, recompensas de caixa, itens ganhos em gacha. **Fora de escopo:** personagens; e **não misturar** com o pacote de armas (o port das armas é um trabalho separado, já feito — ver memória).

> Observação operacional: **VIP/VVIP é `media`, não `alta`** — coerente com o risco de VVIP (precisa de `CF_VVIP_ITEM_INFO`). Começar pelas `alta` que mais provavelmente reaproveitam prêmios já existentes (Brazil/Red Dragon costumam premiar armas comuns).

---

## 6. Mapeamento do `manifesto_caixas.csv`

O `manifesto_caixas.csv` é **enxuto** (407 bytes): apenas 2 colunas — `family` e `priority` — com as 19 famílias acima. **Não contém** `ITEM_ID`s, pools, preços nem prêmios. É um **índice de prioridades**, não um manifesto de itens.

```
family,priority
Brazil,alta
Red Dragon,alta
... (8 alta)
VIP / VVIP,media
... (11 media)
```

**Implicação:** o manifesto sozinho **não basta** para executar o port. Falta o "manifesto de itens" por família (os `ITEM_ID` das caixas + os `ITEM_ID` dos prêmios + taxas), que deveria vir dos docs `_TUTORIAL/docs/` (ausentes) ou ser **extraído do cliente do BR Ilusion** (ITEM.xlsx/ITEM.CFT + config do Mega Lotto daquele build). **Esse é o principal artefato faltante** para começar a execução — ver Passo 0 do plano.

---

## 7. Plano de integração passo-a-passo (testável, sem aplicar agora)

> Filosofia: **lote pequeno → validar carga → validar conexão → validar compra → validar abertura → rollback se falhar.** Sempre com backup `_bak`. Nunca passar de ~2900 itens em `CF_ITEM_INFO` (crash de executável comprovado).

### Passo 0 — Obter a fonte de conteúdo (pré-requisito bloqueante)
- Conseguir o **cliente / catálogo do BR Ilusion** (ITEM.xlsx ou ITEM.CFT + config do Mega Lotto) OU os docs `_TUTORIAL/docs/` que faltam.
- Sem isso, só dá para **adensar pools existentes com prêmios já cadastrados** (Passos 6–7 isolados); não dá para criar as famílias novas.

### Passo 1 — Backup e fotografia do estado
- `SELECT INTO CF_ITEM_INFO_bak_mn_<data>`, `CF_GACHA_ITEM_bak_mn_<data>`, `CF_GACHA_GROUP_bak_mn_<data>`.
- Registrar contagens atuais: 2559 itens, 547 caixas, 65 pools, 3518 prêmios, 324 grupos.

### Passo 2 — Inventário do que já existe (evitar duplicar)
- Para cada família do manifesto, identificar quais caixas/prêmios **já existem** no CF Master (busca por NAME/ITEM_CODE). Tudo que já existe → só ajuste de gacha, não insert de item.
- Mapear pools livres: hoje `GACHA_ID` vai até 64. Caixas novas podem **reusar pools existentes** (se o tema combinar) ou **criar pools novos** `GACHA_ID 65+` (precisa que o cliente também aponte para esse novo `GACHA_ID`).

### Passo 3 — Definir o "manifesto de itens" por família
- Planilha por família: `caixa_ITEM_ID (1EA/5EA/10EA)`, `pool (FUNCTION5/GACHA_ID)`, `preço`, `moeda (C/G)`, e a **lista de prêmios** (`ITEM_ID`, `GROUP_ID`/tier, `WIN_RATE`, `DISPLAY`). Classificar cada prêmio em **existente** vs **novo**.
- Os `ITEM_ID` das caixas têm que ser **exatamente** os que o cliente manda (extrair do BF011/config do lotto do build de destino — ver memória, parser `parse_lotto.ps1`).

### Passo 4 — Prêmios NOVOS primeiro (se houver) — pipeline de item custom
- Para cada prêmio novo: assets no cliente (`ITEM.CFT`/ItemIcon/modelos), `ITEM_INDEX` dentro do limite, linha em `CF_ITEM_INFO` (com `ITEM_CATEGORY` correta por classe de arma; pular VVIP a menos que `CF_VVIP_ITEM_INFO` exista).
- Validar carga em lote pequeno (ver Passo 8). **Adiar** prêmios novos sempre que possível — priorizar prêmios existentes.

### Passo 5 — Inserir as CAIXAS em `CF_ITEM_INFO`
- Por caixa, `INSERT ... SELECT FROM` template de uma caixa que funciona (ex. AWM-Pink `9000016301/02/03`), sobrescrevendo: `ITEM_ID`, `ITEM_CODE`, `NAME`, `ITEM_INDEX` (do cliente), `PRICE`, `SALE_TYPE` (C/G por `CashItem`), `USE_EFFECT3` (=tier/MaxUse), `FUNCTION4='21'`, `FUNCTION5`=pool, `SALE_STATUS='O'`, `SALE_PLACE='C'`.
- Sanitizar varchar (sem zero-byte/NULL: `SET col='-'`) — causa nº1 de crash de carga.
- **Lote ≤150 caixas.** Gerar `.sql` local e `scp` + `sqlcmd -i` (o wrapper corrompe valores com `|`/especiais no `-Q`).

### Passo 6 — Popular os pools em `CF_GACHA_GROUP`
- Para cada pool novo (`GACHA_ID`), criar os grupos (tiers) replicando o padrão existente: ~4 grupos, com linhas por `CASH_TYPE` (0/1/2/3) e `WIN_RATE` por tier.
- Para pool reusado, pular.

### Passo 7 — Popular os prêmios em `CF_GACHA_ITEM`
- Inserir cada prêmio: `GACHA_ID`, `GROUP_ID` (tier), `ITEM_ID` (tem que existir em `CF_ITEM_INFO`), `CASH_TYPE`, `WIN_RATE`, `CNT=1`, `DISPLAY='Y'` (prêmios de vitrine) ou `'N'`.
- **Invariante a checar:** todo `CF_GACHA_ITEM.ITEM_ID` deve existir em `CF_ITEM_INFO` (senão "ghost" → falha/crash). Rodar o anti-ghost antes de subir.

### Passo 8 — Refresh de catálogo + validação de carga
- Ordem: `Restart-Service gDBGW -Force` (esperar 6666+5174 LISTEN) → `cf_gamesrv` → `cf_cgamesrv` (recarrega catálogo da loja) → `UPDATE CF_MIN_CU SET CONNECT_CNT=0 WHERE CONNECT_CNT<0`.
- Confirmar no log do `cf_cgamesrv` que aparece `LoadGameModeInfo`/`Room Info` **sem** `Failed gDBGW ManagerInit`.
- Confirmar que `cf_gamesrv` **bindou 5174** e `cf_cgamesrv` **10011** (se não bindar → crash de carga → rollback do lote).

### Passo 9 — Teste in-game (dono / conta de teste)
1. Caixa **aparece** na vitrine do lotto (cliente atualizado).
2. Caixa **compra** (EC/GP debita; `[CASH_ITEM_BUY_SUCCESS]` no `cash_cf_gamesrv`).
3. Caixa **abre** (`SP_CONFIRM_GACHA` consome GAUGE e entrega prêmio).
4. Prêmio **renderiza** na partida (se arma) — categoria correta.
- Validar pelo menos 1 caixa por família antes de avançar para a próxima.

### Passo 10 — Iterar por prioridade
- Famílias `alta` (1–8) primeiro, uma de cada vez, com validação completa entre elas. Depois `media` (9–19), deixando VIP/VVIP por último (depende de `CF_VVIP_ITEM_INFO`).

---

## 8. Riscos

1. **DECISÃO DE MOEDA PENDENTE (mercado negro) — risco aberto nº1.** A memória registra: 38 itens do mercado negro tiveram `sale_type 'F'(Free Point)→'C'(cash)`; o botão original chamava `GSP_BUY_FP_ITEM` que **nunca existiu** e `CF_USER_FP` está vazia. Antes de portar caixas é preciso **decidir a moeda das caixas novas**:
   - (A) `SALE_TYPE='C'` → compra com **eCoin** via `SP_BUY_CASH_ITEM` (caminho que funciona hoje; recomendado).
   - (B) `SALE_TYPE='G'` → compra com **GP** via `SP_BUY_GPITEM`.
   - (C) reviver Free Point → exige **criar `GSP_BUY_FP_ITEM`** + popular `CF_USER_FP` + dar FP aos players (mais trabalho, sem proc de referência). **Não recomendado** sem necessidade de design.
   - Enquanto a moeda não for decidida, não cadastrar caixas em `sale_type='F'` (não há proc → "failed to purchase").
2. **Fontes ausentes.** Os 6 docs `_TUTORIAL/docs/` e o dump do BR Ilusion **não estão na VPS**. O port das famílias novas está **bloqueado** até obter o catálogo/cliente de origem. Sem isso só dá para densificar pools existentes.
3. **Limite de itens do executável (~2900).** Hoje 2559. Cada família de caixas + prêmios novos soma linhas. Inserir em lotes pequenos e validar que os game servers sobem e bindam as portas; passar de ~2900 → crash-loop sem log.
4. **Crash de carga (`0x0057CCE3` / zero-byte) e de conexão (`0x004130F2` / valor fora de vocabulário).** Toda linha nova tem que ser sanitizada (varchar sem NULL/zero-byte; enums/ranges dentro do vocabulário do set bom) — senão crash.
5. **GACHA_ID vem do cliente.** Se o cliente do build de destino apontar a caixa para um `GACHA_ID` diferente do `FUNCTION5`/do pool populado, sorteia errado. Cliente e banco têm que concordar.
6. **Prêmios VVIP.** Qualquer prêmio com `VVIPItemIndex` exige a tabela `CF_VVIP_ITEM_INFO` (já recriada vazia na VPS) povoada corretamente; senão a arma "cai pra faca" / crash no connect. Tratar VVIP só no fim.
7. **Ghost de gacha.** `CF_GACHA_ITEM` apontando para `ITEM_ID` inexistente em `CF_ITEM_INFO` → "falha ao comprar"/crash. Sempre validar a integridade pool→item antes de subir.
8. **Cache do gDBGW + refresh perde no reboot.** Após qualquer INSERT, é obrigatório o refresh de catálogo (Passo 8); e o refresh **some a cada reboot** do servidor — reaplicar.
9. **Wrapper SSH/SQL instável.** Valores com `|`/especiais corrompem via `-Q`; usar `sqlcmd -i` com arquivo. INSERTs idempotentes (`WHERE NOT EXISTS`) e retry loop.

---

## 9. Estado atual do banco (verificado, read-only)

```
CF_ITEM_INFO ............ 2559 itens
  por ITEM_TYPE: F=1140  W=758  D=550  P=82  C=19  S=10
  por SALE_TYPE: C=1713  G=843  M=3
  ITEM_CODE LIKE 'I%' ... 1140  (= todos os ITEM_TYPE='F')
  caixas (FUNCTION4='21' AND ITEM_TYPE='F') ... 547

CF_GACHA_ITEM ........... 3518 linhas  (65 pools, GACHA_ID 0..64)
CF_GACHA_GROUP .......... 324 linhas   (65 pools)
  por pool: ~40 prêmios, 4 grupos (GROUP_ID 0..3), DISPLAY mistura Y/N

Procs presentes: SP_BUY_CASH_ITEM, SP_BUY_GPITEM, SP_CONFIRM_GACHA, SP_CF_GACHA_RARE
Procs AUSENTES: GSP_BUY_FP_ITEM (nunca existiu — confirma a memória)
```

**Conclusão:** a infraestrutura do mercado negro (procs, pools, schema) está **pronta e saudável**. O port é, na prática, **conteúdo**: trazer os `ITEM_ID` de caixa do cliente do BR Ilusion, cadastrar as caixas em `CF_ITEM_INFO`, e povoar/reusar pools de gacha — priorizando prêmios já existentes. Os dois bloqueios reais para começar são: **(1) decidir a moeda** e **(2) obter a fonte de conteúdo do BR Ilusion** (ausente na VPS).
