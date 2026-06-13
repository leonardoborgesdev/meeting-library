# CrossFire Master — Banco de Dados (SQL Server)

> Documento técnico do banco de dados principal do servidor **CrossFire Master** (CF 1.0, base V2019/PH).
> Gerado a partir de inspeção **somente-leitura** do banco vivo na VPS (`178.83.141.35`) + memória do projeto.
> **Todas as contagens deste documento são reais**, obtidas via `SELECT COUNT(*)` no banco em produção (2026-06-13).

---

## 1. Visão geral

### 1.1 Servidor e instância

| Item | Valor |
|------|-------|
| SGBD | **Microsoft SQL Server 2025 (RTM) 17.0.1000.7 — Express Edition (64-bit)** |
| Host | Windows Server 2022 Standard (VPS Kronic, IP público `178.83.141.35`) |
| Instância | `127.0.0.1` (default), porta 1433 (fechada externamente por firewall) |
| Login de aplicação | `cf` (sysadmin) — senha `<SENHA_SQL>` |
| Login auxiliar | `hgw` (anti-cheat HGW, sysadmin) — senha `<SENHA_SQL>` |
| Banco principal | **`CF_PH_GAME`** |

> O `sqlcmd` **não está no PATH** da VPS. Acesso de fora é feito por SSH + sqlcmd com `-C` (TrustServerCertificate) ou via .NET `System.Data.SqlClient` (connstr `Server=127.0.0.1;Database=CF_PH_GAME;User Id=cf;Password=<SENHA_SQL>;Encrypt=False;TrustServerCertificate=True`).

### 1.2 Bancos do ecossistema

O CF Master é multi-banco. `CF_PH_GAME` é o coração do jogo, mas o servidor depende de outros:

| Banco | Papel |
|-------|-------|
| **`CF_PH_GAME`** | **Catálogo de itens, contas, inventário, slots, gacha, missões, perfis. (este documento)** |
| `CF_PH_LOG` | Logs de fim-de-partida / level-up / conexão. Tabelas `CF_GAME_LOG`, `CF_PLAY_LOG`, `CF_LEVELUP_LOG`, `CF_CONNECT_LOG` + funções `ConvDate`/`ConvVar`. **Se faltar, o save de EXP/KD faz ROLLBACK** (bug histórico). |
| `CF_PH_GUILD` | Dados de clã (ClanServer). |
| `MICROGAMESBILL_DB` | Billing / carteira de cash real do **site** (`TAccountMst.CashReal`, `TCashMst.RemainCashAmt` por `UserNo=USN`). **A loja in-game NÃO usa este banco.** |
| `CF_WEB` | Conteúdo do site (notícias, banner). Acessado pelo PHP como `$connection4`. |

> **Importante (memória):** o saldo de EC/cash que o jogador vê e gasta **in-game** está em `CF_PH_GAME.CF_USER.CASH` / `.GAME_POINT`. O `MICROGAMESBILL_DB` só é o caminho de compra por dinheiro real no site.

### 1.3 Escala do banco (objetos)

| Objeto | Quantidade |
|--------|-----------:|
| Tabelas de usuário (`sys.tables`) | **195** (inclui muitas `*_bak_*` de backup) |
| Stored procedures (`sys.procedures`) | **180** |

> Há **dezenas de tabelas `_bak_*` / `_OLD` / `_TEMP`** (ex.: ~30 cópias de `CF_ITEM_INFO_bak_*`). São snapshots de segurança das mexidas em itens/loja — **não são usadas pelo jogo**, só servem de rollback. Não confundir com as tabelas vivas.

---

## 2. Tabelas-chave (contagens reais)

| Tabela | Linhas (real) | Função |
|--------|--------------:|--------|
| `CF_ITEM_INFO` | **2.559** | **Catálogo mestre** de todos os itens/armas (1 linha por item-período). |
| `CF_USER` | **35** | Conta de jogo: perfil, moedas, stats por modo, nível, EXP. |
| `CF_USER_INFO` | 34 | Dados complementares da conta. |
| `CF_USER_INVENTORY` | **1.716** | Inventário: 1 linha por item que o jogador possui. |
| `CF_USER_SACK` | **136** | "Bags" / loadouts (slots de arma equipada). |
| `CF_USER_CHARACTER` | **48** | Personagens (skins de soldado) que a conta possui + partes (dress). |
| `CF_CHAR_ITEM_INFO` | 0 | Catálogo de peças de personagem (vazio neste servidor). |
| `CF_USER_NEWBIEMISSION_ACHIEVE` | **10** | Progresso da missão de novato (onboarding). |
| `CF_MIN_CU` | **2** | Lista de servidores/canais (SERVER 01 e 02). |
| `CF_GACHA_GROUP` | **324** | Grupos de prêmios de gacha (pesos por grupo). |
| `CF_GACHA_ITEM` | **3.518** | Itens individuais dentro de cada gacha (prêmios). |
| `CF_MEMBER` | 33 | Conta de login (credenciais). |

> Observação: `CF_USER` tem **209 colunas** — a maioria são contadores de stats por modo de jogo (KILL/DEATH/WIN/LOSE por T, D, TD, H, GN, GR, CS, ESP, NA, AI…). `CF_GACHA_GROUP` tem **65 GACHA_IDs distintos** (pools 0–64).

---

## 3. `CF_ITEM_INFO` — catálogo de itens e armas

É a tabela mais importante. Cada item vendável/usável do jogo tem 1+ linhas aqui. Os game servers carregam toda a tabela na inicialização (via gateway gDBGW, query `Q3`/`Q31`) e enviam o catálogo da loja ao cliente. **63 colunas.**

### 3.1 Schema (colunas relevantes)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `ITEM_ID` | varchar(10) NOT NULL | **Chave lógica do item.** É o ID exato que o cliente (bloco `(Item …)` do `BF011.LTC`) envia na compra. **O vínculo de compra é por `ITEM_ID`, não por `ITEM_CODE`.** A tabela é HEAP (sem PK/identity). |
| `ITEM_CODE` | varchar(5) NOT NULL | Rótulo curto (ex. `C0001`=M4A1, `C0309`=Knuckle). Usado por `CF_USER_INVENTORY` para vincular item ao dono. É só rótulo na compra. |
| `NAME` | varchar(100) NOT NULL | Nome de exibição. |
| `ITEM_INDEX` | int NOT NULL | **Índice do recurso no cliente** (bute/modelo). Liga a linha do banco ao `WeaponIndex`/`ItemIndexInBute` do `BF005`/`BF011`. Errar isso = arma sem modelo. |
| `ITEM_TYPE` | varchar(1) NOT NULL | Classe macro do item (ver §3.3). |
| `ITEM_CATEGORY1` | varchar(5) NOT NULL | **Categoria primária (slot/classe da arma).** Ver §4. |
| `ITEM_CATEGORY2` | varchar(5) NOT NULL | **Subcategoria (tipo da arma).** Ver §4. |
| `SALE_TYPE` | varchar(1) NOT NULL | Moeda de venda: `G`=GP (Game Point), `C`=cash/eCoin/ZP, `M`=Master Points. |
| `SALE_STATUS` | varchar(1) NOT NULL | `O`=à venda (Open) / `C`=fechado (Closed/oculto). |
| `SALE_PLACE` | varchar(1) NOT NULL | Onde aparece: `C`(loja), `A`(ambos), `W`(?). GP exige `C` ou `A`. |
| `PRICE` | int NOT NULL | Preço na moeda do `SALE_TYPE`. `999999999` = sentinela "desligado". |
| `SALE_START_DATE` / `SALE_END_DATE` | datetime | Janela de venda. |
| `EFF_START_DATE` / `EFF_END_DATE` | datetime | Janela de efetividade (`EFF_END_DATE='3000-12-31'` = permanente). |
| `USE_TYPE1..5` / `USE_EFFECT1..5` | varchar(1)/int | Efeitos de uso (duração, quantidade). `USE_TYPE1='E'` + `USE_EFFECT1=999999999` = item permanente. `USE_EFFECT3` numa caixa de lotto = nº de jogadas. |
| `GET_LIMIT_LEV` | int | Nível mínimo para comprar. |
| `CHAR_ITEM_ID` | varchar(10) | Para peças de personagem: ID do char dono. |
| `DRESS1..10` | varchar(10) | Peças que compõem um personagem. |
| `FUNCTION1..5`, `Function6` | varchar(10)/int | Flags funcionais. **Numa caixa de gacha: `FUNCTION4='21'` (constante) e `FUNCTION5`=ID do pool de prêmios.** |
| `EVENT_GROUP` | varchar(1) | `M`=item de Mileage (trava compra GP). `-`=normal. |
| `ITEM_INFO` | varchar(1) | `D` = desativado/oculto (o proc de compra rejeita `item_info='D'`). |
| `USER_TYPE` | varchar(1) | `N`=item normal, `C`=item de personagem (exige conta poder receber `C`). |
| `RESOURCE_ID`, `SHORT_NAME`, `SHORT_DESCR`, `LONG_DESCR`, `DISPLAY_TYPE`, `ICON_TYPE`, `ITEM_RANK`, `Team_Effect` | vários | Metadados de exibição/recurso. |

> **Gotcha de integridade (memória):** colunas varchar **não podem ter string zero-byte** (`DATALENGTH=0`) nas colunas que o loader do gateway lê — isso desincroniza o parser `CGDBGWParser::dbreaddata` → `EXCEPTION_ACCESS_VIOLATION` → cf_gamesrv em crash-loop. Receita após qualquer insert em massa: `UPDATE … SET col='-' WHERE DATALENGTH(col)=0` em **toda** coluna varchar (script `sanitize_all.sql`). Há também **limite de quantidade no binário** do game server — com ~2.915 itens o servidor entra em crash-loop; estável até ~1.984–2.559. Nunca inserir centenas de uma vez sem validar que as portas 5174/10011 bindam.

### 3.2 Distribuição por `ITEM_TYPE` (real)

| ITEM_TYPE | Linhas | Significado |
|-----------|-------:|-------------|
| `F` | 1.140 | Caixas/gacha (item de inventário que **abre** outro item) e funções. |
| `W` | 758 | **Armas** (weapon). |
| `D` | 550 | Peças/equip de personagem, granadas, dress. |
| `P` | 82 | Pacotes (abrem múltiplos itens via `SP_PACKAGE_ITEM_OPEN`). |
| `C` | 19 | Personagens (soldados). |
| `S` | 10 | Itens de serviço/especiais. |

### 3.3 Distribuição de venda (real)

| `SALE_TYPE` | Linhas | `SALE_STATUS='O'` (à venda) |
|-------------|-------:|----------------------------:|
| `C` (cash/eCoin/ZP) | 1.713 | 1.703 |
| `G` (GP) | 843 | 822 |
| `M` (Master Points) | 3 | 3 |

| `SALE_STATUS` | Linhas |
|---------------|-------:|
| `O` (à venda) | 2.528 |
| `C` (fechado) | 31 |

---

## 4. Decodificação de `ITEM_CATEGORY1` / `ITEM_CATEGORY2`

`ITEM_CATEGORY1`/`2` definem o **SLOT e a classe da arma**. O cliente monta a lista de armas primárias/secundárias a partir destas colunas (catálogo carregado via gateway). **Categoria errada quebra o slot** (ex.: uma faca marcada como `M/R` polui o slot primário e nenhuma rifle vincula — bug crítico já resolvido).

### 4.1 Tabela de decodificação (armas)

| `CAT1/CAT2` | Classe | Slot |
|-------------|--------|------|
| `M/R` | **Rifle / Fuzil** | Primária |
| `M/SR` | **Sniper** | Primária |
| `M/S` | **Sniper / Shotgun-variante** | Primária |
| `M/SM` | **SMG / Submetralhadora** | Primária |
| `M/M` | **Metralhadora (LMG)** | Primária |
| `S/P` | **Pistola** | Secundária |
| `K/K` | **Faca / Melee** | Faca |
| `D/HE` | **Granada HE** | Arremesso |
| `D/FB` | **Flash Bang** | Arremesso |
| `D/SG` | **Smoke / Granada de fumaça** | Arremesso |

### 4.2 Distribuição real das categorias de arma (`ITEM_TYPE='W'`)

| `CAT1/CAT2` | Linhas |
|-------------|-------:|
| `M/R` (rifle) | 287 |
| `M/SM` (smg) | 87 |
| `S/P` (pistola) | 80 |
| `D/HE` (granada HE) | 76 |
| `M/SR` (sniper) | 72 |
| `K/K` (faca) | 57 |
| `M/M` (metralhadora) | 51 |
| `D/SG` (smoke) | 22 |
| `M/S` (sniper/shotgun) | 19 |
| `D/FB` (flash) | 7 |

### 4.3 Categorias de personagem/equip (`ITEM_TYPE='D'`)

Para peças de personagem/dress as categorias seguem outro vocabulário (`H/SH`, `H/SF`, `B/SB`, `L/SW`, `L/STL`, `H/TF`, `B/SS`) — são partes de soldado (cabeça/corpo/etc.), não armas.

> **Regra de ouro (memória):** ao inserir armas via `INSERT…SELECT` de um template, **nunca herdar a categoria do template** sem corrigir. Clonar a linha do Kukri (faca, `K/K`) num fuzil deixa ele `K/K` → vira "faca" → não aparece como primária na partida. Mapear sempre pela classe real (`M/R`, `M/SM`, etc.).

---

## 5. Tabelas de conta, inventário e slots

### 5.1 `CF_USER` — conta de jogo (35 linhas, 209 colunas)

Identidade + carteira + todos os contadores de stats. Colunas-chave:

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `USN` | bigint | **Chave da conta** (User Serial Number). |
| `NICK` / `LOWER_NICK` | varchar | Apelido (codificado) e versão minúscula. |
| `AUTHORITY` | varchar(1) | **`A`=GM/Admin, `N`=normal.** |
| `GAME_POINT` | bigint | Saldo GP (moeda de jogo). |
| `CASH` | bigint | Saldo cash/eCoin/ZP usado **in-game**. |
| `CLAN_POINTS` | bigint | Pontos de clã. |
| `LEV` / `EXP` | int / bigint | Nível e experiência. |
| `DEFAULT_CHAR_ITEM_ID` | varchar | Personagem equipado (`'-'` se onboarding não concluído). |
| `DEFAULT_SACK_SRL` | int | Bag padrão (aponta `CF_USER_SACK`). |
| `LAST_PLAY_DATE` | datetime | Último jogo (`3000-12-31` = nunca salvou — sinal do bug de save). |
| `RIFLE_KILL`, `SMG_KILL`, `KNIFE_KILL`, `HEADSHOT_KILL_CNT`, `WIN_CNT`, `LOSE_CNT`, … + contadores por modo (`T_*`, `D_*`, `TD_*`, `H_*`, `GN_*`, `GR_*`, `CS_*`, `ESP_*`, `NA_*`, `AI_*`) | int | Stats persistidos pela proc de fim-de-partida. |

Amostra real:

| USN | AUTHORITY | LEV | GAME_POINT | CASH | CLAN_POINTS |
|-----|-----------|----:|-----------:|-----:|------------:|
| 77893 (comptecc, "[GM]CompTec") | A | 99 | 999.797.999 | 999.995.049 | 1.000.000.000 |
| 77899 (azared) | N | 1 | 1.000.452.344 | 999.998.999 | 1.000.000.000 |
| 77909 | N | 0 | 1.349.034 | -24.110 | NULL |

### 5.2 `CF_USER_INVENTORY` — inventário (1.716 linhas)

Uma linha por item possuído. **O dono é vinculado por `ITEM_CODE`** (não `ITEM_ID`).

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `INVENTORY_SRL` | bigint | Chave da linha de inventário (retornada pelos procs de compra). |
| `USN` | bigint | Dono. |
| `ITEM_TYPE` | varchar(1) | Tipo (espelha `CF_ITEM_INFO.ITEM_TYPE`). |
| `ITEM_CODE` | varchar(5) | Item possuído (liga a `CF_ITEM_INFO.ITEM_CODE`). |
| `CHAR_ITEM_ID` | varchar(10) | Char dono (para peças). |
| `EFF_START_DATE` / `EFF_END_DATE` | datetime | Validade (`3000-12-31` = permanente). |
| `GAUGE` | int | **Contador de usos** (ex.: jogadas restantes de uma caixa de lotto; `SP_CONFIRM_GACHA` faz `GAUGE = GAUGE - 1`). |
| `CNT` | int | Quantidade. |
| `FUNCTION_USE_YN` | varchar(1) | Item ativado/funcional. |
| `LIST_POSITION` | int | Ordem na lista do inventário. |

### 5.3 `CF_USER_SACK` — bags / loadouts (136 linhas)

Cada "bag" guarda os itens equipados (loadout) nos slots de cada classe.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `USN` | bigint | Dono. |
| `SACK_SRL` | int | ID da bag. |
| `DISP_ORDER` | int | Ordem de exibição. |
| `RIFLE_SLOT` | bigint | **Slot primário** (rifle/sniper/smg). |
| `PISTOL_SLOT` | bigint | Slot secundário (pistola). |
| `KNIFE_SLOT` | bigint | Slot de faca. |
| `THROW_SLOT1..3` | bigint | Slots de granada/arremesso. |
| `GAUGE` | int | Contador da bag. |
| `EFF_START_DATE` / `EFF_END_DATE` | datetime | Validade da bag. |

> **Assinatura de bug conhecido:** quando a categoria primária está corrompida (faca dentro de `M/R`), o cliente grava **lixo** em `RIFLE_SLOT` (valor `9223372036854775791` ≈ LLONG_MAX) e o gateway loga `Out of present range` na query `update CF_USER_SACK set RIFLE_SLOT=…`. Pistola/faca/granada continuam salvando.

### 5.4 `CF_USER_CHARACTER` — personagens (48 linhas)

Personagens (skins de soldado) que a conta possui, com as partes vestidas.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `USN` | bigint | Dono. |
| `CHAR_ITEM_ID` | varchar(10) | ID do personagem. |
| `EFF_START_DATE` / `EFF_END_DATE` | datetime | Validade. |
| `SH_PART`, `TF_PART`, `SF_PART`, `SS_PART`, `SB_PART`, `STL_PART`, `SW_PART`, `SFU_PART`, `TJ_PART`, `TB_PART`, `TH_PART`, `TP_PART`, `STR_PART`, `TFT_PART` | bigint/int | Partes (dress) vestidas: cabeça, tronco, etc. |

> **Gotcha (memória):** inserir um personagem (ITEM_TYPE `C` / client type 2) copiando linha de outro deixa as partes (dress) órfãs → `CCharItem::PutOnDress Error` → cliente fecha ao entrar no servidor para **todos**. Personagem só porta com o ecossistema de dress completo.

### 5.5 `CF_USER_NEWBIEMISSION_ACHIEVE` — onboarding (10 linhas)

Progresso da missão de novato. Sua presença é pré-requisito do onboarding (escolha de nick/soldado).

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `USN` | bigint | Conta. |
| `LEV_101..LEV_105`, `LEV_201..LEV_205`, `LEV_301..LEV_305` | int NOT NULL | 15 contadores de progresso (sem default → o insert **tem** que preencher todos com 0). |
| `NB_KIND` | varchar(1) | Tipo de novato (`'N'` é o que `SP_GS_GAME_LOGIN` espera). |

> **Bug histórico:** `SP_GS_CREATE_USER_NEWBIE_DATA` era um stub que inseria só `USN` → falhava (15 colunas NOT NULL sem default) → onboarding travava com `DEFAULT_CHAR_ITEM_ID='-'`. Corrigido reescrevendo o proc para inserir todas as colunas.

### 5.6 `CF_MIN_CU` — lista de servidores/canais (2 linhas)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `SERVER` | varchar(10) | ID do servidor (`01`, `02`). |
| `SERVER_NAME` / `SERVER_WEB_NAME` | varchar(30) | Nome exibido (lobby/web). |
| `CONNECT_CNT` | int | Conexões atuais. **`-1` = manutenção/lobby vazio.** |
| `LIMIT_CNT` | int | Capacidade. |
| `IP` | varchar(15) | IP do game server (`178.83.141.35`). |
| `PORT` | int | Porta (srv01=`5174`, srv02=`10011`). |
| `EVENT` | int | Flag de evento. |

> Operação crítica: `UPDATE CF_MIN_CU SET CONNECT_CNT=0 WHERE CONNECT_CNT<0` tira a "manutenção". Leituras retornando vazio/timeout geralmente são **lock por transação órfã** do gDBGW, não dados perdidos — checar `sys.dm_tran_locks` antes de assumir perda.

---

## 6. Gacha / Lotto

O "Mega Lotto" (mercado negro/caixas) usa duas tabelas. Comprar a caixa é uma operação (`SP_BUY_*`); **abrir** a caixa é outra (`SP_CONFIRM_GACHA`).

### 6.1 `CF_GACHA_GROUP` — grupos de prêmios (324 linhas, 65 GACHA_IDs)

Define os grupos de raridade dentro de um pool e seus pesos.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `SRL` | int | Chave. |
| `GACHA_ID` | int | **Pool de prêmios** (0–64). Referenciado por `CF_ITEM_INFO.FUNCTION5` da caixa. |
| `GROUP_ID` | int | Grupo de raridade dentro do pool. |
| `WIN_RATE` | float | Peso/probabilidade do grupo. |
| `CASH_TYPE` | int | Moeda (`0`=eCoin/cash, `1`=GP). |
| `DROP_CNT` | int | Quantos itens caem. |

### 6.2 `CF_GACHA_ITEM` — prêmios individuais (3.518 linhas)

Cada prêmio possível, ligado a um pool/grupo e a um `ITEM_ID` real.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `SRL` | int | Chave. |
| `GACHA_ID` | int | Pool. |
| `GROUP_ID` | int | Grupo de raridade. |
| `ITEM_ID` | varchar(10) | **Prêmio** (deve existir em `CF_ITEM_INFO`, senão é "ghost"). |
| `CASH_TYPE` | int | `0`=eCoin, `1`=GP, `2`/`3`=outras moedas. |
| `WIN_RATE` | float | Peso. |
| `CNT` | int | Quantidade do prêmio. |
| `DISPLAY` | varchar(1) | `Y`=visível na vitrine, `N`=oculto. |

Distribuição real por `CASH_TYPE` × `DISPLAY`:

| CASH_TYPE | DISPLAY=Y | DISPLAY=N |
|-----------|----------:|----------:|
| 0 (eCoin) | 775 | 1.823 |
| 1 (GP) | 153 | 527 |
| 2 | 41 | 119 |
| 3 | 14 | 66 |

> **Ghosts:** muitas linhas `DISPLAY='N'` são sentinelas/slots vazios ou prêmios que apontam para itens inexistentes em `CF_ITEM_INFO`. Um prêmio `DISPLAY='Y'` apontando para `ITEM_ID` inexistente faz o player "girar → prêmio não existe → falha". A correção é `SET DISPLAY='N'` nesses (mantendo cada pool com ≥1 prêmio válido). Tabelas de log relacionadas: `CF_GACHA_LOG` (todo pull), `CF_GACHA_RARE_USER` (wins raros — alimenta o feed de ganhadores do banner).

### 6.3 Como a caixa liga ao pool

Uma caixa de lotto em `CF_ITEM_INFO` é uma linha com:
- `ITEM_TYPE='F'`, `SALE_TYPE='C'`(eCoin) ou `'G'`(GP), `SALE_PLACE='C'`, `SALE_STATUS='O'`;
- `FUNCTION4='21'` (constante), **`FUNCTION5` = `GACHA_ID` do pool**;
- `USE_EFFECT3` = nº de jogadas do tier (1EA→1, 5EA→5, 10EA→10).

Ao comprar, `SP_BUY_CASH_ITEM` cria a linha de inventário com o `GAUGE`. Ao abrir, `SP_CONFIRM_GACHA` decrementa o `GAUGE` e sorteia o prêmio dentro do `GACHA_ID` (o `GACHA_ID` chega do **cliente**, não da caixa).

---

## 7. Stored procedures importantes

> O servidor tem **180 procedures**. As do fluxo de jogo são chamadas pelos game servers **através do gateway gDBGW** (mapeadas em `C:\Windows\DBGWMGR.ini`, queries `Q*`). Todas confirmadas existentes no banco vivo.

### 7.1 `SP_BUY_GPITEM` — compra com GP

```
@p_usn int, @p_log_type varchar(2), @p_item_id varchar(10),
@p_item_type varchar(1), @p_user_type varchar(1),
@p_Inventory_srl bigint, @p_Result int OUTPUT
```

Compra um item pagando **GAME_POINT**. Lógica (do corpo real):
1. `SET NOCOUNT ON; SET XACT_ABORT ON` (já tem proteção transacional).
2. Valida `@p_log_type IN ('11'..'21')` (tipo de log da operação).
3. Lê `LEV` e `GAME_POINT` do `CF_USER`.
4. Localiza o item em `CF_ITEM_INFO` com **todos** os filtros: `item_id=@p_item_id AND item_type=@p_item_type AND GETDATE() BETWEEN sale_start/end AND eff_start/end AND sale_status='O' AND sale_type='G' AND sale_place IN ('C','A') AND item_info!='D' AND @v_lev >= get_limit_lev`.
5. Se `@p_user_type='N'` e o item é `user_type='C'` (personagem) → erro `-99981`.
6. Pacotes (`item_type='P'`) → reserva seq e chama `SP_PACKAGE_ITEM_OPEN`.
7. `BEGIN TRAN` → `UPDATE CF_USER SET GAME_POINT = GAME_POINT - @v_price` → insere a linha de inventário → loga em `CF_ITEM_GET_LOG_GAME_POINT`.
8. Retorna `@p_Result` = `INVENTORY_SRL` (positivo) em sucesso, ou código de erro negativo.

> Se o item não passar em **qualquer** filtro (não existe, status/tipo/data/place errados, `item_info='D'`, nível insuficiente), retorna negativo → cliente mostra "failed to purchase". Item com `EVENT_GROUP='M'` (Mileage) calcula preço NULL → falha de GP (corrigido para `'-'`).

### 7.2 `SP_BUY_CASH_ITEM` — compra com cash/eCoin/ZP

```
@p_usn bigint, @p_log_type varchar, @p_item_id varchar,
@p_item_type varchar, @p_Saleinfo_id varchar, @p_Cdl_id varchar,
@p_user_type varchar, @p_Inventory_srl bigint, @p_Result int OUTPUT
```

Análogo ao anterior, mas valida `sale_type='C'` e debita **`CF_USER.CASH`**. **A loja in-game NÃO consulta o billing** (`MICROGAMESBILL_DB`) — debita o `CASH` local. Também seta o `GAUGE` quando o item é uma caixa de lotto. É a rota correta para itens cash; tentar comprar item `sale_type='C'` via GP dá `@v_price NULL` → erro.

### 7.3 `SP_CONFIRM_GACHA` — abrir caixa / girar gacha

```
@p_inventory_srl bigint, @p_gacha_cnt int, @p_gacha_items varchar,
@p_cash_type int, @p_gacha_id int, @p_encode_nick varchar,
@p_inventory_srl_str varchar OUTPUT, @p_rare_nick varchar OUTPUT, @p_result int OUTPUT
```

Executa a abertura de uma caixa de gacha/lotto:
1. `UPDATE CF_USER_INVENTORY SET GAUGE = GAUGE - 1 WHERE inventory_srl=@p_inventory_srl`; se `GAUGE-1 < 0` → resultado negativo (`-1`/`-6`) = "failed to purchase".
2. Sorteia o(s) prêmio(s) no pool `@p_gacha_id` usando `CF_GACHA_GROUP` (pesos) + `CF_GACHA_ITEM` (prêmios `DISPLAY='Y'`).
3. Credita o(s) item(ns) em `CF_USER_INVENTORY`, loga em `CF_GACHA_LOG` e, em wins raros, em `CF_GACHA_RARE_USER`.
4. Tem `XACT_ABORT ON` aplicado (fix de "girou e o item sumiu").

### 7.4 `SP_CREATE_USER` — criação de conta

```
@p_usn bigint, @p_encode_nick varchar, @p_encode_lnick varchar,
@p_reg_no int, @p_o_usn bigint OUTPUT, @p_Result int OUTPUT
```

Cria a linha de jogo (`CF_USER`) para uma conta nova, gravando nick codificado e número de registro. (O nickname em si sempre funcionou; o travamento de onboarding vinha do passo de novato — §7.5.)

### 7.5 `SP_GS_CREATE_USER_NEWBIE_DATA` — dados de novato (onboarding)

```
@p_i_usn bigint, @p_o_result int OUTPUT
```

Cria a linha em `CF_USER_NEWBIEMISSION_ACHIEVE` para a conta. **Tem que preencher as 15 colunas `LEV_*` (=0) + `NB_KIND='N'`** (todas NOT NULL sem default). Sem essa linha, o onboarding (escolha de nick/soldado/treino) não conclui. Foi reescrita para corrigir o stub original que só inseria `USN`.

### 7.6 `SP_GS_GAME_LOGIN` — login no jogo

```
@p_usn bigint + 209 parâmetros OUTPUT (perfil completo) + @p_result OUTPUT
```

Carrega **todo** o perfil do jogador no login: nick, authority, moedas (`GAME_POINT`), nível/EXP, **todos os contadores de stats por modo**, personagem padrão (`DEFAULT_CHAR_ITEM_ID`), bag padrão (`DEFAULT_SACK_SRL`), bindings de teclado, configurações de mira/macros, medalhas, status de liga e `NB_KIND` (espera `'N'`). É a proc de carga de sessão — espelho do `CF_USER` (211 parâmetros no total).

### 7.7 Outras procs do fluxo (confirmadas existentes)

| Proc | Função |
|------|--------|
| `SP_GS_SCORE` | Save de fim-de-partida (EXP/KD/wins por modo). Sensível ao `DBGWMGR.ini` (params duplicados travavam o save → rank/clã/Point Mall em cascata). |
| `SP_USE_ITEM` | Usar/consumir item do inventário. (XACT_ABORT aplicado.) |
| `SP_SEND_GIFT` | Presentear item a outro jogador. (XACT_ABORT aplicado.) |
| `GSP_CF_GIVE_ITEM` | Dar item a uma conta (admin/sistema). (XACT_ABORT aplicado.) |
| `SP_GIVE_GPITEM` | Conceder item GP. |
| `SP_PACKAGE_ITEM_OPEN` | Abrir pacote (`ITEM_TYPE='P'`) — entrega múltiplos itens. |

> **NÃO existe** proc de "Black Market" (`GSP_BUY_FP_ITEM` nunca existiu em nenhum banco). O mercado negro foi mapeado para `SALE_TYPE='C'` (compra com eCoin via `SP_BUY_CASH_ITEM`). Só `'G'` e `'C'` têm proc de compra — itens `'F'`/`'M'`/etc. sem rota dão "failed to purchase".

---

## 8. Como itens são dados a contas

Há duas formas práticas de colocar um item no inventário de um jogador:

### 8.1 Via compra (fluxo normal do jogo)

1. Cliente envia o **`ITEM_ID` exato** (do bloco `(Item …)` do `BF011.LTC`) ao game server.
2. Game server chama, via gateway gDBGW, `SP_BUY_GPITEM` (GP) ou `SP_BUY_CASH_ITEM` (cash).
3. A proc valida `CF_ITEM_INFO` (status/tipo/datas/place/nível), debita `GAME_POINT`/`CASH` em `CF_USER` e insere a linha em `CF_USER_INVENTORY` (com `ITEM_CODE`, `EFF_END_DATE`, `GAUGE`, `CNT`).
4. Loga em `CF_ITEM_GET_LOG_GAME_POINT` / `CF_ITEM_GET_LOG_CASH`.

> Pré-condição: o item **tem** que existir em `CF_ITEM_INFO` com o `ITEM_ID` exato que o cliente manda. Se não existir, a compra falha **no cliente**, antes de chegar ao servidor (nada aparece no `cash_*.log`).

### 8.2 Via concessão direta (admin / banco)

- Proc `GSP_CF_GIVE_ITEM` (ou `SP_GIVE_GPITEM`) — concede o item por código a uma conta, criando a linha de inventário corretamente. **Forma recomendada** (passa pela lógica de validação/log).
- `INSERT` direto em `CF_USER_INVENTORY` (USN + ITEM_TYPE + ITEM_CODE + EFF_END_DATE `3000-12-31` + GAUGE/CNT). Funciona, mas exige cuidado: usar `ITEM_CODE` (não `ITEM_ID`), respeitar tipo, e não dar itens que exijam infra extra (VVIP → tabela `CF_VVIP_ITEM_INFO`; personagem → dress completo) sob risco de crash no connect do dono.

### 8.3 Caixas / gacha

Dar uma caixa = dar o item `ITEM_TYPE='F'` com `GAUGE` = nº de jogadas. O jogador **abre** chamando `SP_CONFIRM_GACHA`, que decrementa o `GAUGE`, sorteia em `CF_GACHA_GROUP`/`CF_GACHA_ITEM` e credita o prêmio.

---

## 9. Resumo das contagens reais (snapshot 2026-06-13)

| Métrica | Valor |
|---------|------:|
| Itens no catálogo (`CF_ITEM_INFO`) | 2.559 |
| — armas (`ITEM_TYPE='W'`) | 758 |
| — caixas/gacha (`ITEM_TYPE='F'`) | 1.140 |
| — itens à venda (`SALE_STATUS='O'`) | 2.528 |
| — vendáveis GP (`G`,`O`) / cash (`C`,`O`) | 822 / 1.703 |
| Contas de jogo (`CF_USER`) | 35 |
| Linhas de inventário (`CF_USER_INVENTORY`) | 1.716 |
| Bags/loadouts (`CF_USER_SACK`) | 136 |
| Personagens (`CF_USER_CHARACTER`) | 48 |
| Linhas de onboarding (`CF_USER_NEWBIEMISSION_ACHIEVE`) | 10 |
| Servidores/canais (`CF_MIN_CU`) | 2 |
| Grupos de gacha (`CF_GACHA_GROUP`) — 65 pools | 324 |
| Prêmios de gacha (`CF_GACHA_ITEM`) | 3.518 |
| Stored procedures (`sys.procedures`) | 180 |
| Tabelas (`sys.tables`, inclui backups) | 195 |

---

*Acesso de leitura via SSH + `sqlcmd -S 127.0.0.1 -U cf -P <SENHA_SQL> -C -d CF_PH_GAME`. Documento somente-leitura — nenhuma alteração foi feita no banco durante sua geração.*
