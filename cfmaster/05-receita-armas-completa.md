# 05 — Receita Completa: Adicionar Armas Custom no CrossFire Master

> **Status:** validado em produção com a **M4A1-C Brasil** aparecendo perfeita no shop, no inventário (bag) **e na partida** (cliente FoxxFire 1.0 + VPS 178.83.141.35). Documento de **referência reutilizável** para portar as **~215 armas** do pack `UPGRADE CF Master - ARMAS`.
>
> **Escopo:** este é um documento de ANÁLISE/RECEITA. Os comandos abaixo são os que JÁ foram usados; antes de repetir em lote, faça backup e teste 1 arma ponta-a-ponta.
>
> Relacionados: `04-guia-replicacao.md`, `03-erros-e-solucoes.md`, `02-banco-de-dados.md`, `01-arquitetura-servicos.md`. Memórias: `cfmaster-arma-custom`, `cfmaster-primaria-categoria-fix`, `cfmaster-loja-itens-compra`.

---

## 0. TL;DR — o modelo mental

Uma arma custom no CF 1.0 **não é um arquivo só**. Ela vive em **4 CAMADAS** que precisam estar **consistentes entre si** (mesmos índices, mesma categoria, mesmo ITEM_ID), senão a arma buga de um jeito diferente em cada lugar:

| # | Camada | Onde | Renderiza? | Validada por |
|---|--------|------|-----------|--------------|
| 1 | **Butes do CLIENTE** | `RB001.REZ → REZ\BUTES\BF005.LTC` (arma) + `BF011.LTC` (item) | — | shop/inventário do cliente |
| 2 | **Modelos/texturas/sons/ícones** | `RF*.REZ` (cliente) — pack ⇒ `RF002/016/017/018/019/020/031`; cliente vivo costuma consolidar em `RF124` | **SIM** (cliente desenha) | engine gráfica do cliente |
| 3 | **Banco** | `CF_PH_GAME..CF_ITEM_INFO` (1 linha) | — | loja in-game / catálogo |
| 4 | **Butes do SERVIDOR** | `cf_hostsrv\rez\RB001.REZ → BF005.LTC + BF011.LTC` | **NÃO** (servidor não renderiza) | host da sala (partida) |

**O ELO QUE FALTAVA (a lição mais cara):** a Camada 4. O **cf_hostsrv** (host da sala) carrega a **PRÓPRIA cópia** dos butes e **valida** a arma equipada contra ela. Se a arma existe nas camadas 1-3 mas **não** na 4, o sintoma é clássico e confunde: **"funciona no shop, equipa, mas na PARTIDA pula pra faca"**.

### Mapa de sintoma → camada quebrada

| Sintoma | Camada culpada |
|---------|----------------|
| Não aparece na loja / "failed to purchase" antes de chegar no DB | Camada 3 (linha ausente/filtrada) ou ITEM_ID do BF011 ≠ DB |
| Aparece na loja mas **sem ícone** / ícone errado no bag/buy | Camada 2 (DTX do ícone) + `BigIconName`/`SmallIconName` no BF005 |
| Compra, equipa, mas **arma invisível / modelo errado** na mão | Camada 2 (modelos `.LTB`/texturas `.DTX` ausentes ou caminho errado) |
| Compra e equipa no shop, mas **na partida vira faca** | **Camada 4** (servidor não tem a arma) — OU índice da arma > 897 |
| **Todas as primárias** somem/não salvam pra TODO MUNDO | Camada 3 com **ITEM_CATEGORY errada** (faca K/K num rifle, ou rifle marcado como K) — ver §6.3 |
| Servidor crasha quando dono da arma conecta | arma VVIP sem `CF_VVIP_ITEM_INFO` (ver §6.5) ou personagem sem dress |

---

## 1. Inventário do pack (fonte das 215)

Local (VPS, **read-only**): `C:\Users\Administrator\Desktop\UPGRADE CF Master\UPGRADE CF Master - ARMAS\`

```
ITEMS_215.csv      <- mapa family,code,item_id,name das 215 armas
README.md          <- regras por família
ASSETS\
  RB001\
    Table\         130 .CFT  (tabelas de jogo decifradas; fonte p/ stats/lote)
    REZ\BUTES\     380 arquivos: BF005.LTC (1.33MB), BF011.LTC (85KB), +263 .LTC, 115 .DAT
  RF002\IMPOUI\RIFLECROSSHAIR\   62 .DTX  (crosshair por arma)
  RF016\MODELS\WEAPONS\          486 .LTB (modelo de mundo QV-)
        MODELS\PLAYERVIEW\      1646 .LTB (viewmodel 1ª pessoa PV-, + _BL/_GR variantes)
  RF017\MODELTEXTURES\WEAPONS\   694 .DTX (skin do mundo)
        MODELTEXTURES\PLAYERVIEW\888 .DTX (skin do viewmodel)
  RF018\SND\WEAPON\<ARMA>\      1702 .WAV (sons por arma, ~5-7 por arma)
  RF019\TEX\UI\WEAPONICON\      1165 .DTX (BUYWEAPON_INFO_*, WEAPON_SELECT_*)
        TEX\UI\AMMOICON\        1946 .DTX
        TEX\UI\KILLMSG\          713 .DTX (ícone de kill feed)
        TEX\UI\CROSSHAIR\         10
  RF020\TEXFX\                   efeitos (light/sky/water/magma)
  RF031\FX_MAP\                  efeitos de mapa/sniper/shotgun
```

### Distribuição por família (215 total)

| Família | Qtd | Regra do README |
|---------|-----|-----------------|
| **Noble Gold** | 86 | inclui `Ultimate Gold`, `Ultimate Goldsmith`, `Noble Gold` — manter cada variante permanente |
| **Royal Dragon** | 61 | preservar TODOS os sufixos numéricos (`Royal Dragon3/4/6`, `RoyalDragon8/9/10`) — modelos diferentes |
| **Ultimate Gold** | 22 | idem Noble Gold |
| **Red Dragon** | 19 | usar a variante **permanente**; sufixo `R.D`/`RD` = mesma família |
| **Gold Phoenix** | 12 | preservar `Gold Phoenix`/`GoldPhoenix`; não separar modelo da textura |
| **Black Dragon** | 7 | `GoldBlackDragon` reaproveita a estrutura da linha Black Dragon |
| **Knight Blue** | 6 | — |
| **Brazil** | 2 | `AK-47-Knife-Brazil Permanent` (C1513) + `M4A1-C-Brazil` (C1252); reaproveita estrutura do M4A1 |

> **GOTCHA de família (Beast/Royal Dragon):** *NÃO colapsar* nomes de variante quando o **modelo muda**. `Born Beast`, `Prism Beast`, `Fury Beast`, `Iron Beast`, `Steel-Empire`, `Beast2` são modelos distintos — cada um precisa do próprio `.LTB`/`.DTX`. Se você apontar duas armas para o mesmo modelo, uma sai com a skin da outra.

> **Inventariar sem extrair os enormes:** os RF*.REZ no servidor passam de 600MB. Sempre liste com `Get-ChildItem -Recurse | Measure-Object` (contagem/extensão), NUNCA extraia o pacote inteiro. Os butes (BF005/BF011) e a tabela CFT são pequenos e SÃO o que importa para a receita.

---

## 2. CAMADA 1 — Butes do cliente (BF005 + BF011 dentro do RB001.REZ)

`RB001.REZ` contém `REZ\BUTES\BF005.LTC` (definição das ARMAS) e `BF011.LTC` (definição dos ITENS compráveis). São arquivos `.LTC` (binário, magic CF `54 83 B2 E1`) que decompilam para `.LTA` (texto S-expression).

### 2.1 Bloco da ARMA — BF005 (`(Weapon ...)`)

A arma custom é um **clone estrutural** de uma arma-base que funciona (o M4A1). Você copia o bloco inteiro do M4A1 e troca **só**: `WeaponIndex`, `WeaponName`, os 4 caminhos de modelo/skin, sons (se houver), e os ícones. Mantém toda a física (Perturb/Recoil/Damage/RPM) da base — é o que faz a arma se comportar bem.

Bloco final REAL da M4A1-C Brasil (`conv\BF005.LTA`, índice 140):

```
(Weapon
 (WeaponIndex 140 )                                              ; <- slot DummyWeapon reaproveitado, ≤897
 (WeaponClass 3 )                                                ; classe da base (rifle)
 (WeaponName "M4A1-C Brasil" )
 (ModelFileName    "Models\weapons\QV-M4A1_C_Brasil_M.ltb" )     ; modelo de MUNDO (3ª pessoa)
 (SkinFileName     "ModelTextures\weapons\QV-M4A1_C_Brasil.dtx" )
 (RenderStyleFileName "RS\\NinjaTranslucent.ltb" )
 (PViewModelFileName  "Models\PlayerView\PV-M4A1_C_Brasil" )     ; viewmodel 1ª pessoa (SEM extensão; engine acha _BL/_GR)
 (PViewSkinFileName   "ModelTextures\PlayerView\PV-M4A1_C_Brasil.dtx" )
 (PViewSkinFileName2  "TexFX\Cubic\CubicEnvMapNew1.dtx" )
 (PViewRenderStyleFileName "RS\\PVModelDefault.ltb" )
 (GViewAnimName "M4A1" )                                         ; animação herdada da base
 (ShotSoundName "ShootM4A1" )                                    ; som herdado da base (ok reaproveitar)
 (MagazineClipOutSoundName "ClipOutM4A1" )
 (MagazineClipInSoundName "ClipInM4A1" )
 (ReloadSoundName "ReloadM4A1" )
 (BigIconName   "M4A1_C_BRASIL" )                                ; <- ÍCONE do shop/bag (ver §5)
 (SmallIconName "M4A1_C_BRASIL" )
 (BulletPosOffset 20.0 -10.0 15.0 )
 (GVModelScale 1.5 )
 ... (todos os blocos Perturb*/FullReact*/ShotReact*/Range/MaxAmmo/AmmoDamage/RPM herdados do M4A1) ...
)
```

**Campos que você TROCA por arma** (o resto copia da base): `WeaponIndex`, `WeaponName`, `ModelFileName`, `SkinFileName`, `PViewModelFileName`, `PViewSkinFileName`, `BigIconName`, `SmallIconName`. Se o pack trouxer sons próprios da arma (pasta em `RF018\SND\WEAPON\<ARMA>`), troque também os `*SoundName`; senão, reaproveite os da base.

> **Reaproveitar som da base é seguro.** A Brasil mantém `ShootM4A1` etc. e funciona 100%. Só vale a pena trocar som quando a família tem áudio próprio no pack.

### 2.2 Bloco do ITEM — BF011 (`(Item ...)`)

Esse é o bloco que o **cliente envia na compra** (o vínculo é por **ITEM_ID do BF011**, ver §4). Bloco final REAL da Brasil (`conv\BF011.LTA`):

```
(Item
 (ItemIndex 1060 )                ; índice do ITEM (esparso, pode passar de 897; max observado 1060)
 (CashItem 0 )                    ; 0=GP, 1=eCoin/cash
 (PeriodCount 1 )                 ; nº de durações (1 = só permanente)
 (ItemID "2010990001" )           ; <- ID EXATO que o cliente manda na compra; tem que existir no DB
 (Day 0 )                         ; 0 = permanente; >0 alinhado a PeriodCount (ex 30 15 7 3)
 (Price 30000 )
 (ItemCode "C0900" )              ; rótulo (NÃO é o que casa a compra)
 (ItemName " " )                  ; <- NOME do BAG (mostrado no inventário). " " => herda do DB/base
 (ItemType 0 )
 (ItemCategory 0 )
 (ItemCategory2 2 )
 (ShopAttr 1 )
 (ResellItem 1 )(RepairItem 1 )(LimitRankingLevel 0 )(FullGauge 100 )(RegDate 20070303 )
 (Description "M4A1 Custom com tema Brasil. Reskin do M4A1. [Permanente.]" )
 (WeaponPower 66 )(WeaponAccuracy 95 )(WeaponContinuity 64 )(WeaponRecoil 60 )(WeaponWeight 43 )
 (WeaponLoadAmmo 30 )(WeaponFullAmmo 60 )
 (ItemButeType 3 )                ; 3 = arma
 (ItemIndexInBute 140 )           ; ★ DEVE ser igual ao WeaponIndex do BF005 (140)
)
```

> **★ INVARIANTE DE OURO:** `ItemIndexInBute` (BF011) **= `WeaponIndex`** (BF005). É o ponteiro item→arma. Se divergir, o item compra mas não vincula a arma certa.

> **★ DIFERENÇA item vs DB:** o `ItemIndex` do BF011 (1060) é o que vai para a coluna `ITEM_INDEX` do `CF_ITEM_INFO` (camada 3) — **não** o `WeaponIndex`. Verificado no DB vivo: `C0900 / 2010990001 / ITEM_INDEX=1060`. O `WeaponIndex` 140 só existe nos butes.

### 2.3 GOTCHA crítico de índice — o limite ≤897

- **BF005 (armas): o array da PARTIDA é 0–897 (899 entradas, está CHEIO).** WeaponIndex **898** RENDERIZA no preview do shop (carrega sob demanda) mas é **DROPADO na partida** → vira faca. **NUNCA use 898+ para armas que precisam funcionar em jogo.**
- Há **502 slots `DummyWeapon`** livres ≤897 (placeholders vazios). **Reaproveite um** via **swap atômico de índice**: a Brasil nasceu em 898 e foi movida para o dummy 140 (898 ↔ 140). Nada é removido, só os números trocam.
- Achar dummies livres: na `BF005.LTA`, buscar blocos `(WeaponName "DummyWeapon")` e ler o `WeaponIndex` da linha acima. (Confirmado: 502 dummies, max WeaponIndex = 898.)
- **BF011 (itens): índice esparso, pode passar de 897.** Item @1060 funciona no shop + inventário + partida (uma vez que o servidor sabe da arma). Max observado = 1060.

> **Para as 215:** há 502 dummies e você precisa de ~215 slots de arma — **cabe folgado**. Reserve uma faixa contígua de WeaponIndex de dummies (ex. 140–360) e uma faixa de ItemIndex livre no BF011 (ex. 1061–1280) e mapeie 1:1.

### 2.4 Toolchain dos butes

| Operação | Comando | Onde |
|----------|---------|------|
| **LTC → LTA** (decompilar) | `cfltc.exe <arq.LTC>` (1 arg) | `C:\Users\henrique\elite_rb001\conv\` |
| **LTA → LTC** (compilar) | `CFLTC_Converter.exe <in.lta> <out.ltc>` | `C:\Users\henrique\Desktop\cfwarserverfiles\` |
| **Extrair REZ** | `cfrez.exe x <rez> <dir>` | `C:\Users\henrique\elite_rb001\` (precisa `cfrezformat.dll` ao lado) |
| **Empacotar REZ** | `cfrez.exe c <rez> <dir>` | idem |
| **Conferir magic** | `xxd -l4 <arq.ltc>` → deve dar `54 83 b2 e1` | — |

**Gotchas do compilador `CFLTC_Converter.exe`:**
1. **Extensões em MINÚSCULAS** (`.lta`/`.ltc`), senão falha.
2. **Adicionar a pasta ao PATH** — ele invoca `LTC.exe` internamente.
3. **Precisa de stdin** — chamar com `echo "" | CFLTC_Converter.exe in.lta out.ltc`.
4. **★ EXIGE CRLF.** O `.LTA` editado precisa ter quebras de linha **Windows (CRLF)**. `sed -i` no Git Bash grava **LF** e o compilador **quebra** (gera LTC inválido/truncado). Edite com ferramenta que preserve CRLF (PowerShell `-Encoding`, ou normalize com `unix2dos` antes de compilar).
5. Sempre **confira o magic** do LTC gerado antes de empacotar.

**Round-trip do REZ:**
- **Cliente (RB001):** `cfrez` é **byte-idêntico** (md5 do container bate). Trocar só os 2 LTC e re-empacotar é seguro.
- **Servidor (RB001 13MB, packer oficial):** round-trip **NÃO** é byte-idêntico (cresce ~25KB), mas é **CONTENT-fiel** — validar por **diff de conteúdo** (só BF005/BF011 devem mudar), nunca por md5 do container.

### 2.5 Passo a passo da Camada 1

```
# 1. extrair o RB001 do cliente
cfrez.exe x RB001.REZ out\

# 2. decompilar os dois butes
cfltc.exe out\REZ\BUTES\BF005.LTC      # -> BF005.LTA
cfltc.exe out\REZ\BUTES\BF011.LTC      # -> BF011.LTA

# 3. editar BF005.LTA: achar dummy livre, escrever o bloco (Weapon ...) (clone do M4A1)
# 4. editar BF011.LTA: escrever o bloco (Item ...) com ItemIndexInBute = WeaponIndex
#    (manter CRLF!)

# 5. recompilar (PATH + stdin)
echo "" | CFLTC_Converter.exe bf005.lta bf005.ltc
echo "" | CFLTC_Converter.exe bf011.lta bf011.ltc
xxd -l4 bf005.ltc    # confere 54 83 b2 e1

# 6. colocar de volta e re-empacotar
copy bf005.ltc out\REZ\BUTES\BF005.LTC
copy bf011.ltc out\REZ\BUTES\BF011.LTC
cfrez.exe c RB001_new.REZ out\
```

---

## 3. CAMADA 2 — Modelos, texturas, sons e ícones (RF*, só CLIENTE)

Estes arquivos são o que o **cliente desenha**. O **servidor não precisa deles** (ele não renderiza — por isso a rez do servidor só vai até RF123). Mapeamento por caminho relativo (mantenha EXATO o que o BF005 referencia):

| Tipo | Caminho dentro da REZ | Convenção de nome |
|------|----------------------|-------------------|
| Modelo de mundo (3ª pessoa) | `Models\Weapons\QV-<NOME>_M.ltb` (M=masculino; pode ter `_F` feminino) | `ModelFileName` do BF005 |
| Viewmodel (1ª pessoa) | `Models\PlayerView\PV-<NOME>` (+ engine acha `_BL`/`_GR` e `_WOMAN_BL`/`_WOMAN_GR`) | `PViewModelFileName` (SEM extensão) |
| Skin do mundo | `ModelTextures\Weapons\QV-<NOME>.dtx` | `SkinFileName` |
| Skin do viewmodel | `ModelTextures\PlayerView\PV-<NOME>.dtx` | `PViewSkinFileName` |
| Som da arma | `Snd\Weapon\<ARMA>\*.wav` | `*SoundName` (se a família tiver som próprio) |
| **Ícone shop/bag** | `Tex\UI\WeaponIcon\BUYWEAPON_INFO_<BigIconName>.DTX` | `BigIconName` (ver §5) |
| Ícone de seleção | `Tex\UI\WeaponIcon\WEAPON_SELECT_<NOME>.DTX` | — |
| Ícone de munição | `Tex\UI\AmmoIcon\*.DTX` | herdado da base, normalmente |
| Kill message | `Tex\UI\KillMsg\*.DTX` | — |
| Crosshair | `Tex\UI\Crosshair\` e `IMPOUI\RIFLECROSSHAIR\` (RF002) | — |

**Regra de ouro de caminho:** o `ModelFileName`/`SkinFileName` no BF005 tem que casar **byte a byte** com o caminho real dentro do REZ. Se o BF005 diz `Models\weapons\QV-X_M.ltb` e o arquivo está em `Models\Weapons\QV-X.ltb` (sem `_M`), a arma sai **invisível**.

**O que pode dar errado (do README):** "se abrir sem imagem ou sem áudio" = caminho relativo diferente, falta de `PV`/`QV`, falta de `DTX`, ou falta do bloco BF011/BF005.

> **Cliente vivo vs pack:** o pack entrega os assets soltos em `RF002/016/017/018/019/020/031`. No cliente FoxxFire vivo esses recursos foram consolidados (a M4 Brasil entrou no `RF124`). Para o cliente de produção, você empacota os assets novos num REZ que o cliente carregue (ex. um `RF124` próprio) OU injeta nos REZ correspondentes. **O servidor NUNCA recebe RF* novos.**

---

## 4. CAMADA 3 — Banco (`CF_ITEM_INFO`, 1 linha por arma)

A linha do catálogo é um **clone da linha-base** (M4A1 `C0001`/equivalente) sobrescrevendo identidade e índice. **Vínculo da compra = `ITEM_ID` (do BF011), não `ITEM_CODE`.**

Linha viva da M4A1-C Brasil (confirmada no DB):

```
ITEM_ID=2010990001  ITEM_CODE=C0900  ITEM_TYPE=W  ITEM_INDEX=1060
ITEM_CATEGORY1=M    ITEM_CATEGORY2=R  RESOURCE_ID=-  SALE_TYPE=G  SALE_STATUS=O
```

Campos que importam:
- **`ITEM_ID`** = o `ItemID` EXATO do bloco BF011 (`2010990001`). Se o DB não tiver essa linha, a compra **falha NO CLIENTE**, antes de chegar no servidor (nada aparece no `cash_*.log`, nenhum `sp_buy`).
- **`ITEM_INDEX`** = o `ItemIndex` do BF011 (**1060**), NÃO o WeaponIndex.
- **`ITEM_TYPE='W'`** (arma). Crítico para GP: `SP_BUY_GPITEM` valida `item_type=@p_item_type`.
- **`ITEM_CATEGORY1`/`ITEM_CATEGORY2`** = **classe real da arma** (ver tabela §6.3). Rifle = `M`/`R`. **NUNCA** copiar de template de faca (K/K) — quebra a primária de todo mundo.
- **`SALE_STATUS='O'`** (aberto), **`SALE_TYPE`** = `G` (GP) ou `C` (eCoin), **`SALE_PLACE` IN ('C','A')** para GP.
- **`RESOURCE_ID='-'`**, **`EVENT_GROUP='-'`** (se ficar `'M'`=Mileage, o GP rejeita/calcula NULL).
- Datas: `SALE_START_DATE <= getdate()` e `EFF_END_DATE >= getdate()` (a query de carga filtra por isso).

INSERT seguro (clone da base, sobrescrevendo identidade):

```sql
INSERT INTO CF_ITEM_INFO
SELECT ... -- todas as colunas da base C0001
FROM CF_ITEM_INFO WHERE ITEM_CODE='C0001';
-- depois UPDATE da nova linha: ITEM_ID, ITEM_CODE, ITEM_INDEX, ITEM_CATEGORY1/2 corretos,
-- SALE_STATUS='O', SALE_TYPE, PRICE, EVENT_GROUP='-', RESOURCE_ID='-'
```

> **Gotcha do wrapper SQL:** valores com `|` ou caracteres especiais (ex. `M|SM`) são corrompidos quando passados via `-Q` pelo wrapper rexec/EncodedCommand (vira `M SM`). **Gere o `.sql` localmente e rode `sqlcmd -i arquivo.sql`** (ou copie por scp). Para inserts em lote idempotentes use `INSERT...SELECT FROM (VALUES...) v WHERE NOT EXISTS(...)` em batches de ~150.

> **★ GOTCHA do cache do gDBGW:** depois de inserir/alterar `CF_ITEM_INFO`, o item **NÃO** fica comprável só reiniciando o gamesrv — o **gDBGW cacheia** o resultado da query de carga. Faça o **refresh de catálogo** (§7) na ordem certa.

> **★ LIMITE de itens do binário:** o gamesrv crasha com catálogo grande (~2915 crashou; ~1984–2484 estável). **NÃO insira centenas de linhas de uma vez** — faça em lotes e valide que o gamesrv SOBE e BINDA as portas (5174/10011) entre cada lote. 215 armas é um lote grande: divida em ~3-4 levas e teste a estabilidade entre elas.

---

## 5. ÍCONE do bag/buy — a parte cosmética que dá trabalho

O ícone que aparece no shop e no bag vem de um **DTX** no cliente, apontado pelo `BigIconName`/`SmallIconName` do BF005. Convenção:

```
BigIconName "M4A1_C_BRASIL"  ->  Tex\UI\WeaponIcon\BUYWEAPON_INFO_M4A1_C_BRASIL.DTX
```

**Bug clássico (Brasil, antes do fix):** o BF005 da Brasil tinha `BigIconName "m4a1"`/`SmallIconName "m4a1"` (herdado da base) → o bag mostrava o ícone do M4A1 base. **Fix:** trocar para `"M4A1_C_BRASIL"` (o `BUYWEAPON_INFO_M4A1_C_BRASIL.DTX` já existe no pack, em `RF019\TEX\UI\WEAPONICON`).

**O nome do bag** (texto no inventário) vem do `ItemName` do bloco BF011 (camada 1). `" "` faz herdar do DB/base.

### 5.1 Gerar o ícone do zero (quando o pack não tem)

Os `BUYWEAPON_INFO_*.DTX` do pack têm **131236 bytes** = imagem **256×128 BGRA** + header de **164 bytes**. O ícone exibido no bag é **113×58**. Para gerar um novo a partir de outro:

1. **Decodificar o DTX origem:** pular o **header de 164 bytes**, ler **256×128 pixels BGRA** (4 bytes/pixel) → bitmap.
2. **Recortar a região do texto/arte** que você quer e **redimensionar para 113×58**.
3. **Re-emitir** como **PNG + TGA 113×58** na pasta SOLTA do cliente: `UI\ItemIcon\ItemIcon_<ITEM_INDEX>` (pasta do cliente, fora do REZ).
4. O bag busca o ícone por `UI\ItemIcon\ItemIcon_<ITEM_INDEX>` (PNG+TGA), enquanto o shop/preview usa `BUYWEAPON_INFO_<BigIconName>.DTX` dentro do REZ. **Atenda os dois** para o ícone ficar consistente em shop E bag.

> Para as 215, padronize: gere `ItemIcon_<ITEM_INDEX>.png/.tga` (113×58) por arma a partir do `BUYWEAPON_INFO_*` correspondente, e garanta que cada BF005 tenha `BigIconName`/`SmallIconName` próprios (não os da base).

---

## 6. CAMADA 4 — Butes do SERVIDOR (o elo que faltava) + perigos do DB

### 6.1 Por que a arma "pula pra faca" na partida

- O **shop é 100% cliente** → funciona com as camadas 1-3.
- A **partida é autoritativa do servidor**: o **cf_hostsrv** (processos `GameServerManager` + N×`ServerApp`) carrega o **PRÓPRIO** `C:\pmang\crossfire\cf_hostsrv\rez\RB001.REZ` e **valida** a arma equipada contra os butes DELE. Se essa cópia não tem a arma no índice, o host **rejeita → faca**.

### 6.2 Fix da Camada 4

Injetar a **MESMA** arma (bloco BF005 weapon + bloco BF011 item, **MESMOS índices do cliente**) no `RB001.REZ` do **servidor** e reiniciar o host.

- **Modelos NÃO precisam no servidor** (ele não renderiza) — só os 2 butes.
- Os butes BF005/BF011 originais do servidor são **byte-idênticos aos do cliente** (md5 BF005 `7ed9fcea`, BF011 `be55f328`) → os butes editados do cliente **encaixam direto** no servidor.
- Round-trip do RB001 do servidor é **content-fiel** (não byte) — validar por diff de conteúdo (§2.4).

```
# no servidor, em backup primeiro:
copy cf_hostsrv\rez\RB001.REZ cf_hostsrv\rez\RB001.REZ.bak_<data>
cfrez.exe x RB001.REZ srv\
copy <BF005_editado.LTC> srv\REZ\BUTES\BF005.LTC
copy <BF011_editado.LTC> srv\REZ\BUTES\BF011.LTC
cfrez.exe c RB001_new.REZ srv\
# substituir e reiniciar:
Restart-Service cf_hostsrv -Force    # volta como GameServerManager + ServerApp; portas 14001/5174 LISTEN
```

> **Transferir para a VPS:** use **scp** para arquivos. O wrapper `rexec` FALHA com comando grande (base64 embutido > ~8KB) — não tente injetar o REZ via comando inline. `cfrez.exe` + `cfrezformat.dll` já estão em `C:\` na VPS (reusar para as 215).

### 6.3 ★ NUNCA quebrar a primária (categoria)

Este é o bug mais destrutivo (ver `cfmaster-primaria-categoria-fix`). Se você inserir armas com `ITEM_CATEGORY` errada, **TODAS as primárias de TODOS os jogadores** param de aparecer/salvar.

- **Causa típica:** clonar de um **template de FACA** (Kukri = `K`/`K`) → toda arma vira K/K → a engine trata fuzil como faca/slot errado → não aparece como primária na partida.
- **Causa inversa:** marcar facas como `M`/`R` → polui a categoria primária com bute de faca → o slot primário inteiro corrompe → cliente manda **lixo** (`9223372036854775791`) no `RIFLE_SLOT` → erro `Out of present range` no log do gateway.

**Mapeamento canônico (decodificado):**

| Categoria | Classe |
|-----------|--------|
| `M`/`R` | rifle (fuzil) |
| `M`/`SR` | sniper |
| `M`/`SM` | SMG |
| `M`/`M` | metralhadora |
| `M`/`S` | shotgun |
| `S`/`P` | pistola |
| `K`/`K` | **faca de verdade** |
| `D`/`HE`·`FB`·`SG` | granadas |

**Receita confiável para lote:** extrair do cliente o par `ItemID → (ItemCategory, ItemCategory2)`, cruzar com armas já corretas no servidor para derivar a categoria canônica por classe, e setar `ITEM_CATEGORY1/2` pela **classe real** de cada arma (NUNCA herdar a do template de clone).

### 6.4 Diagnóstico decisivo "funciona no shop, faca na partida"

Trocar os **modelos custom** da arma pelos **modelos BASE** (ex. `m4a1.ltb`/`pv-m4a1`) mantendo índice/item, rebuildar, testar:
- Se **AINDA** pula pra faca → **NÃO são os modelos** → é bute/índice/servidor (Camada 4 ou índice >897).
- Se passar a funcionar → o problema estava nos modelos custom (Camada 2).

Foi isso que isolou a causa para o lado servidor na Brasil. (Descartados por evidência: versão LTB `09 00`, nome de osso `Bone01`, esqueletos/tamanhos — todos normais.)

### 6.5 Armas que exigem infra extra (PULAR ou preparar antes)

- **VVIP** (blocos com `VVIPItemIndex`/`VVIPItemBuffFlag` no BF011, ex El Diablo/Savage Beast): exigem a tabela **`CF_VVIP_ITEM_INFO`** + proc `GSP_VVIP_KILL_DEATH`. Sem a tabela, o subsistema VVIP não inicializa → a arma **cai pra faca** e o servidor **crasha** quando o dono conecta (`Invalid object name 'CF_VVIP_ITEM_INFO'` → `EXCEPTION_ACCESS_VIOLATION 0x0057C904`). **Fix:** criar a tabela vazia (heap: `ITEM_INDEX int`, `FUNCTION_NO int`) + a proc, do backup original, ANTES de liberar VVIP. No pack, a família **VIP/VVIP** (variantes `Spirit/Portal/Ticket/NGB/NoMark`) cai aqui — trate por último, com a infra pronta.
- **Personagens (não é arma):** não copiar linha de personagem (type C) — quebra o dress de todo mundo. Fora do escopo deste pack de armas.

---

## 7. Refresh de catálogo (obrigatório após mexer no DB)

Some a cada reboot — **refazer sempre**. Ordem:

```powershell
Restart-Service gDBGW -Force          # esperar 6666 + 5174 LISTEN (race: pode precisar 2ª vez; gDBGW leva >12s)
Restart-Service cf_gamesrv -Force
Restart-Service cf_cgamesrv -Force    # recarrega o catálogo da LOJA
sqlcmd ... -Q "UPDATE CF_MIN_CU SET CONNECT_CNT=0 WHERE CONNECT_CNT<0"   # tira manutenção (lobby)
Restart-Service cf_hostsrv -Force     # só se mexeu na Camada 4 (butes do servidor)
```

Verificar: portas **5174 / 10011 / 6666** LISTEN; log do cf_cgamesrv **SEM** `Failed gDBGW ManagerInit`; **cliente fecha e reabre** (baixa catálogo novo + lê RB001 no boot). Cuidado para o patcher/launcher NÃO sobrescrever seu RB001 editado. Script existente: `C:\Users\henrique\gachafix\refresh_catalog2.ps1`.

---

## 8. Fluxo de TESTE (shop → partida → bag)

Testar **uma** arma ponta-a-ponta antes de qualquer lote:

1. **Shop:** abrir a loja in-game, achar a arma, **comprar**. Se "failed to purchase" sem nada no `cash_*.log` → ITEM_ID do BF011 ≠ DB (Camada 3) ou cache do gDBGW (refresh §7).
2. **Inventário (bag):** a arma aparece no bag com **nome** (BF011 `ItemName`) e **ícone** (§5) corretos? Ícone errado = `BigIconName`/`SmallIconName` ou DTX (Camada 2/5).
3. **Equipar + entrar na partida:** entrar numa sala e spawnar.
   - **Pulou pra faca?** → Camada 4 (servidor sem a arma) ou WeaponIndex >897. Diagnóstico §6.4.
   - **Arma invisível / skin errada?** → Camada 2 (modelo/textura/caminho).
   - **Funciona perfeito?** → arma OK, pode ir para o lote da mesma família.
4. **Regressão da primária:** logar com outra conta e confirmar que **rifles normais** ainda aparecem/salvam (garante que a categoria nova não poluiu M/R). Assinatura de quebra: `Out of present range` / `9223372036854775791` no `GDBGW_*.txt`.

---

## 9. PROCEDIMENTO PASSO-A-PASSO (1 arma) — pronto para repetir

> Pré-requisitos: toolchain em `elite_rb001\` (cfrez + dll) e `cfwarserverfiles\` (CFLTC_Converter + LTC.exe no PATH). Backups SEMPRE antes.

```
[0] BACKUP
    - cliente: copy RB001.REZ RB001.REZ.bak_<arma>_<data>
    - servidor: copy cf_hostsrv\rez\RB001.REZ ...bak_<arma>_<data>
    - DB: SELECT * INTO CF_ITEM_INFO_bak_<arma> FROM CF_ITEM_INFO

[1] ESCOLHER ÍNDICES
    - WeaponIndex: pegar um dummy livre ≤897 (lista de DummyWeapon no BF005.LTA)
    - ItemIndex (BF011) e ITEM_INDEX (DB): um valor livre (ex 1061+), MESMO valor nos dois
    - ItemIndexInBute (BF011) = WeaponIndex

[2] CAMADA 1 (butes do cliente)
    - cfrez x RB001.REZ out\
    - cfltc BF005.LTC ; cfltc BF011.LTC
    - editar BF005.LTA: clonar bloco do M4A1, trocar WeaponIndex/Name/4 caminhos/2 IconNames
    - editar BF011.LTA: novo (Item ...) com ItemID, ItemCode, ItemIndex, ItemIndexInBute=WeaponIndex
    - MANTER CRLF; compilar: echo "" | CFLTC_Converter bf005.lta bf005.ltc (idem bf011)
    - xxd -l4 confere 54 83 b2 e1
    - copiar de volta + cfrez c RB001_new.REZ out\

[3] CAMADA 2 (assets, só cliente)
    - copiar QV-<NOME>_M.ltb / PV-<NOME>(_BL/_GR) / QV-<NOME>.dtx / PV-<NOME>.dtx
    - copiar BUYWEAPON_INFO_<BigIconName>.DTX (+ WEAPON_SELECT_, AMMOICON, KILLMSG se houver)
    - empacotar no REZ de assets do cliente (ex RF124); caminhos = EXATO o que o BF005 referencia
    - (§5) gerar UI\ItemIcon\ItemIcon_<ITEM_INDEX>.png/.tga 113x58 se quiser ícone fiel no bag

[4] CAMADA 3 (banco)
    - INSERT clone de C0001; setar ITEM_ID(=BF011 ItemID), ITEM_CODE, ITEM_INDEX(=BF011 ItemIndex),
      ITEM_CATEGORY1/2 pela CLASSE REAL, ITEM_TYPE='W', SALE_STATUS='O', SALE_TYPE, PRICE,
      EVENT_GROUP='-', RESOURCE_ID='-', datas válidas
    - gerar .sql local e sqlcmd -i (não passar valores via -Q)

[5] CAMADA 4 (butes do servidor)
    - scp dos BF005.LTC/BF011.LTC editados p/ a VPS
    - cfrez x cf_hostsrv\rez\RB001.REZ srv\ ; trocar os 2 LTC ; cfrez c
    - validar por DIFF de conteúdo (só BF005/BF011 mudam)

[6] APLICAR + REFRESH
    - substituir RB001 do cliente e do servidor
    - refresh de catálogo (§7) + Restart-Service cf_hostsrv
    - cliente fecha e reabre

[7] TESTE (§8): shop -> bag -> partida -> regressão da primária
```

---

## 10. EM LOTE pelas famílias (as 215)

A escala é viável (502 dummies para 215 armas). Estratégia por famílias usando `ITEMS_215.csv` + as tabelas **CFT** do pack como fonte da verdade.

### 10.1 Preparação única (uma vez)
1. **Reservar faixas de índice:** WeaponIndex de dummies (ex. 140–360) e ItemIndex/ITEM_INDEX no BF011 (ex. 1061–1280). Mapear `ITEMS_215.csv` 1:1 nessas faixas → gerar um **CSV mestre** `code,item_id,name,family,weapon_index,item_index`.
2. **Identificar a arma-BASE de cada família** (a do mesmo tipo de arma que já funciona: M4A1, AK47, AWM, Desert Eagle, Kukri, etc.). O clone herda física + animação + som da base correta.
3. **Derivar `ITEM_CATEGORY1/2` por arma** cruzando o `ItemCategory`/`ItemCategory2` do BF011 do pack com armas já corretas no servidor (mapa §6.3). NUNCA herdar K/K para fuzil.

### 10.2 Geração em lote (script)
- **BF005:** para cada linha do CSV mestre, emitir um bloco `(Weapon ...)` clonando o bloco da base e substituindo WeaponIndex/Name/4 caminhos/2 IconNames. Concatenar no `BF005.LTA`, reaproveitando slots DummyWeapon.
- **BF011:** emitir um `(Item ...)` por arma com ItemID/ItemCode/ItemIndex/ItemIndexInBute. Preço e duração conforme política da loja (permanente Day 0, ou períodos).
- **DB:** gerar um `.sql` com os INSERTs (clone da base por classe) + UPDATEs de categoria. **Em batches de ~150**, validando estabilidade do gamesrv entre eles (§4).
- **Assets:** copiar `QV-`/`PV-`/`.dtx`/ícones de cada arma para o REZ de assets, respeitando os caminhos do BF005. Famílias com modelos distintos por variante (Beast, Royal Dragon) ⇒ um conjunto por variante (NÃO colapsar — §1).

### 10.3 Ordem de execução recomendada
1. **Brazil (2)** — já provada; serve de smoke test do pipeline.
2. **Gold Phoenix (12)**, **Knight Blue (6)**, **Black Dragon (7)** — lotes pequenos, fáceis de validar.
3. **Red Dragon (19)**, **Ultimate Gold (22)** — médio.
4. **Royal Dragon (61)**, **Noble Gold (86)** — grandes; subdividir em sub-lotes de ~30, refresh + teste entre cada um (limite do binário §4).
5. **VIP/VVIP por último** — só depois de garantir `CF_VVIP_ITEM_INFO` + proc (§6.5).

### 10.4 Checkpoints obrigatórios por lote
- gamesrv **sobe e binda** 5174/10011 (senão reverter o lote: `DELETE WHERE ITEM_ID IN(...)` ou restaurar backup).
- **regressão da primária** OK (nenhum `Out of present range` novo).
- 1 arma de cada família testada **na partida** (não só no shop).

---

## 11. Backups de referência (estado FUNCIONANDO)

- **DB completo:** `C:\dbclone\game_TUDO_OK_20260612_1933.bak` (armas + onboarding + compras OK).
- **Cliente RB001 (Brasil final):** `C:\cfmaster_backups\m4_brasil_FINAL_20260613\RB001.REZ`; e `RB001.REZ.bak_custom140_20260613` (arma@140 custom).
- **Servidor RB001:** `cf_hostsrv\rez\RB001.REZ.bak_pre_m4_140_20260613` (pré-Brasil) e `.bak_prebrasil_20260611`.
- **DB item table:** `CF_ITEM_INFO_bak_pre_m4brasil`, `CF_ITEM_INFO_bak_catfix0612` (fix da categoria).
- **Toolchain local:** `C:\Users\henrique\elite_rb001\` (cfrez + cfrezformat.dll), `C:\Users\henrique\elite_rb001\conv\` (cfltc + BF005/BF011 LTA/LTC), `C:\Users\henrique\Desktop\cfwarserverfiles\` (CFLTC_Converter + LTC.exe).

---

## 12. Checklist final (1 arma = PERFEITA)

- [ ] WeaponIndex em slot DummyWeapon livre **≤897** (não 898+)
- [ ] `ItemIndexInBute` (BF011) **= WeaponIndex** (BF005)
- [ ] `ItemIndex` (BF011) **= `ITEM_INDEX`** (DB); ItemID (BF011) **= `ITEM_ID`** (DB)
- [ ] `ITEM_CATEGORY1/2` = **classe REAL** (rifle M/R, etc.) — primária de terceiros não quebrou
- [ ] `BigIconName`/`SmallIconName` próprios + `BUYWEAPON_INFO_*.DTX` presente; `ItemIcon_<INDEX>` para o bag
- [ ] Caminhos de modelo/skin no BF005 = EXATO o que está no REZ de assets
- [ ] Butes recompilados com **CRLF**, magic `54 83 B2 E1` conferido
- [ ] Camada 4 aplicada: BF005+BF011 no `cf_hostsrv\rez\RB001.REZ` + `Restart-Service cf_hostsrv`
- [ ] Refresh de catálogo feito (gDBGW→gamesrv→cgamesrv→CONNECT_CNT=0)
- [ ] Teste: **shop → bag → partida** OK + **regressão da primária** OK
