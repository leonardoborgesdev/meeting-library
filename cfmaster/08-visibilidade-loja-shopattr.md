# 08 — Arma existe no DB mas NÃO aparece na loja/lotto → ShopAttr (RESOLVIDO)

**Data:** 2026-06-13 · Validado com a família **Royal Dragon** (C0272 M4A1, C0307 Mauser, C0359 Kukri, C0255 Barrett).

## Sintoma
Arma já existe em `CF_ITEM_INFO` (sale_type `G`, status `O`, categoria correta) **e** no `BF011` do cliente, mas **não aparece na loja GP nem no lotto**. Refresh de catálogo não resolve. Bute do servidor não é o problema (isso é só pra aparecer **na sala**).

## Causa raiz
A loja é montada pelo **CLIENTE** a partir do `BF011`. No bloco do item, armas premium vêm com:
- `( ShopAttr 0 )`  → 0 = **não exibir na loja** (1 = exibir)
- `( Price 999999999 )` → sentinela "não vendável"

São itens desenhados pra **lotto/cash**, não pra loja GP. Por isso ficam escondidos. (As colunas do DB são idênticas a um item visível — o lever é **client-side**, no BF011.)

## Diagnóstico (read-only)
Comparar o bloco BF011 do item escondido vs um visível (ex. `C0001` base ou `C0900` M4 Brasil):
- Visível: `ShopAttr 1` + `Price` real (ex. 30000).
- Escondido: `ShopAttr 0` + `Price 999999999`.

## FIX — Caminho A (loja GP direta)
1. **Cliente BF011:** nos blocos-alvo, `ShopAttr 0→1` e `Price 999999999→<preço>`. ⚠️ `ShopAttr 0`/`Price 999999999` aparecem em centenas de itens — editar **só os blocos do ItemCode-alvo** (awk block-aware por ItemCode, não sed global).
2. **DB:** `UPDATE CF_ITEM_INFO SET PRICE=<preço> WHERE ITEM_CODE IN (...)` (pra cobrança/exibição baterem).
3. **Compilar** BF011 (CFLTC exige **CRLF**), **rebuild** do `RB001.REZ` do cliente (cfrez), **deploy**.
4. **Refresh** do catálogo: `Restart-Service cf_cgamesrv` (gateway no ar) + `UPDATE CF_MIN_CU SET CONNECT_CNT=0 WHERE CONNECT_CNT<0`.
5. **Relogar** e conferir no Item Shop → GP.
- **Servidor (cf_hostsrv butes): NÃO precisa.** Visibilidade de loja é cliente+DB.

## FIX — Caminho B (lotto/gacha) [pendente]
Manter `ShopAttr 0` e montar/ativar o **grupo gacha**: `CF_GACHA_GROUP` (caixa→grupo) + `CF_GACHA_ITEM` (grupo→prêmios). Infra de gacha já saudável (ver 06-mercado-negro-analise).

## Distinção-chave
- **Não aparece na LOJA** → `ShopAttr` no BF011 do cliente (este doc).
- **Não aparece na SALA** → bute da arma no `cf_hostsrv\rez\RB001.REZ` do servidor (ver 05-receita-armas-completa).

## Backups deste fix
Cliente: `RB001.REZ.bak_prerd_20260613`; fonte `BF011.LTA.bak_pre_rd`. DB: preço anterior = 100 (reverter `SET PRICE=100`).
