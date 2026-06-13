# 07 — Bots (AI) não andam dentro da sala/mapa — Análise profunda

> **Escopo:** ANÁLISE/PESQUISA apenas. Nada foi modificado no cliente nem no servidor (read-only).
> **Data:** 2026-06-13 · **Servidor:** VPS `178.83.141.35` (`C:\pmang\crossfire`) · **Host de sala:** `cf_hostsrv` (processos `GameServerManager` + N×`ServerApp`).
> **Sintoma reportado:** os bots ENTRAM na sala mas NÃO se movem no mapa.

---

## 0. TL;DR (resumo executivo)

No CrossFire existem **DOIS sistemas de "AI" completamente distintos**, e o sintoma "bot não anda" aponta para o primeiro:

1. **BOTS de sala normal** (o "Add Bot" numa sala de TD/SD comum) — controlado pelas tabelas **`BotRoomDifficulty.CFT`, `BotLevel.CFT`, `BotCharacter.CFT`, `BotNameSet.CFT`**. **Essas 4 tabelas NÃO existem no servidor** (`cf_hostsrv\rez\RB001.REZ`). O servidor só tem `BOTNAME.CFT` (uma lista de nomes, formato antigo). Sem `BotLevel` (que define `view_range`, `view_angle`, `hearing_range`, `tracing_rate`, `attack_speed`, `accuracy`, `personality`...) **o bot spawna mas não tem parâmetros de comportamento/percepção → fica parado**. Essa é a **hipótese principal**.

2. **AI de modo dedicado** (Challenge / AI Wave / Zombie / Mutation-AI) — controlado por **`AIControl<N>.CFT`, `AIMod<N>.CFT`, `AICharacter.CFT`, `AIPattern.CFT`, `AIEvent.CFT`** + os mapas dedicados de AI que carregam **dados de navegação `<MAPA>_DZ.LTC` + `<MAPA>_AN.DAT`** dentro de `RB001.REZ\REZ\BUTES`. **Esse sistema FUNCIONA hoje** — o log de 09/06 mostra uma partida de AI rodando rounds normalmente no mapa `AI_Att_20110729_Effect_01.DAT` (ver §5). Logo, o "andar do AI" em si está OK; o que falta é o subsistema **BOT de sala normal**.

**Conclusão de causa mais provável:** faltam no servidor as tabelas **Bot\*** (loadout + comportamento/percepção do bot de sala normal) e, possivelmente, os **dados de navegação de AI (`_DZ.LTC`/`_AN.DAT`) para os mapas comuns** onde se quer adicionar bots (mapas normais não foram feitos para AI e geralmente NÃO têm `_DZ` → sem navmesh o bot não tem para onde andar). O pack de referência **CF BR Ilusion (`ILUSION_BOTS_MAPS`)** deve trazer exatamente esses dois conjuntos. **O pack ainda NÃO chegou** (ver §9, cheque final).

---

## 1. Como o sistema de AI/bots do CrossFire funciona

### 1.1 Onde os dados moram
- **Tabelas de regra (CFT):** ficam **dentro do `RB001.REZ`**, na pasta interna `TABLE\`. São **lidas pelo SERVIDOR de sala (`cf_hostsrv`)** — é o host que é autoritativo sobre spawn/movimento/IA (o cliente só renderiza). Os mesmos arquivos `TABLE\*.CFT` também existem no cliente, mas o que decide o comportamento do bot é a cópia do **servidor**. (É o mesmo princípio do "elo que faltava" das armas: a partida é autoritativa do `cf_hostsrv` — ver `cfmaster-arma-custom.md`.)
- **Dados de navegação por mapa (navmesh/waypoint de AI):** ficam **dentro do `RB001.REZ`** em `REZ\BUTES\`, como pares **`<MAPA>_DZ.LTC`** (zona de navegação / waypoints da IA) e **`<MAPA>_AN.DAT`** (dados de animação/ataque da IA naquele mapa). Sem o `_DZ` correspondente, a IA não tem grafo de caminho naquele mapa → não anda.
- **Mundo do mapa (`.DAT`/world):** o `ServerApp` carrega o mundo (`Loading world: <mapa>.DAT`) e, se for mapa de AI, casa com o `_DZ`/`_AN`.

### 1.2 Formato dos CFT
Os `.CFT` são tabelas com cabeçalho **`ce`/`su`** e nomes de coluna **ofuscados por uma cifra de +16 no código ASCII** (decodável: `']Q@O^E]'` → `map_num`). Decodifiquei os cabeçalhos para confirmar a semântica (abaixo).

### 1.3 As tabelas e o que cada uma faz (cabeçalhos decodificados)

**BOTS de sala normal (o que falta no servidor):**
- **`BotRoomDifficulty.CFT`** → colunas: `bot_ai_level`, `bot_room_weapon_set`, `bot_nameset_index`, `bot_slot_1` … `bot_slot_16`. Define, por dificuldade de sala, **quantos bots e qual o nível/loadout de cada slot**.
- **`BotLevel.CFT`** → `bot_ai_level`, `bot_weapon_class`, `bot_personality`, `bot_reaction_rate`, `bot_attack_speed`, `bot_shoot_count`, `bot_accuracy`, `bot_accuracy_recursion_targetlimit`, `bot_accuracy_recursion_targetmove`, **`bot_view_range`**, **`bot_view_angle`**, **`bot_hearing_range`**, **`bot_tracing_rate`**, **`bot_tracing_time`**. **ESTES são os parâmetros de percepção e movimento.** Ausentes → o bot não "enxerga", não "persegue", não se desloca.
- **`BotCharacter.CFT`** → `bot_level`, `bot_weaponType`, `bot_mainWeapon`, `bot_subWeapon`, `bot_knife`, `bot_grenade`, `bot_characterType`, `bot_armors`. Define o personagem/armas do bot.
- **`BotNameSet.CFT`** → conjuntos de nomes por dificuldade (mais rico que o `BotName.CFT` antigo).

**AI de modo dedicado (já funciona hoje):**
- **`AIControl<N>.CFT`** → `mode_index`, `map_num`, `map_level`, `spot_index`, `ai_proto_id`, `ai_num`, `ai_grade_id`, `ai_pattern1`, `ai_move_type_pattern`, `ai_weapon_id`, `start_type`, `start_value`, `respawn_time`, … . **É a tabela de spawn da IA por mapa/modo** (`<N>` = índice do modo/mapa de AI). Liga cada *spot* de spawn a um protótipo de IA, um padrão de movimento e uma arma.
- **`AIMod<N>.CFT`** → `map_num`, `mode_index`, `level_number`, `kill_count_to_win`, `limit_use_c4`, `limit_use_machinegun`, `base_life`, `time_limit_per_level`, `count_show_in_level`, `add_time_to_resurrection`, `power_up_rate_per_level`, `attack_rate_per_level`, `gas_start_point`, … . Regras de cada round do modo AI.
- **`AICharacter.CFT`** → catálogo de personagens/protótipos de IA (modelo, HP, etc.).
- **`AIPattern.CFT`** → `update_delay_time`, `start_movetype`, **`move_property`**, `use_attack`, **`moving_attack`**, `attack_delay_time_min/max`, `targetting_type`, `targetting_delay_time`, `targetting_faild_type/value`, **`runaway_type`**, `runaway_value1/2`. **É o "cérebro" de movimento/ataque** que tanto a AI dedicada quanto (em alguns builds) os bots de sala referenciam via `ai_pattern`.
- **`AIWeapon.CFT`, `AIGrade.CFT`, `AIProtoType.CFT`, `AIEvent.CFT`, `AIDropBox.CFT`, `AIMapSRL.CFT`** (mapeia `map_srl`→`map_id`/`sub_mode`/`level`/`boss_srl`), `AISkill.CFT`, etc.

### 1.4 Por que "andar" depende de navmesh
A IA do CF não anda em mundo livre: ela navega sobre um **grafo de zonas/waypoints pré-computado por mapa** = o arquivo **`<MAPA>_DZ.LTC`** (e usa `_AN.DAT` para as animações/ataques). Mapas "de AI" (Challenge/Zombie) têm esse par; **mapas PvP normais geralmente NÃO têm**. Por isso, colocar bot num mapa normal **sem o `_DZ`** = bot fica parado (não há caminho calculável). Os servidores que têm "bots em mapa normal andando" (como o CF BR Ilusion) **embarcaram dados `_DZ`/waypoints para esses mapas comuns** + as tabelas Bot\*.

---

## 2. Estado ATUAL do servidor (cf_hostsrv) — o que existe

Extraído de `C:\pmang\crossfire\cf_hostsrv\rez\RB001.REZ` (13.033.762 bytes; 282 recursos, 4 dirs). `TABLE\` = 66 arquivos.

**Tabelas de AI presentes no servidor:**
```
AICONTROL125..AICONTROL136  (apenas 12 arquivos)
AIMOD125..AIMOD136          (12)
AICHARACTER.CFT (48.679)  AIPATTERN.CFT (10.481)  AIWEAPON.CFT  AIGRADE.CFT
AIPROTOTYPE.CFT  AIEVENT.CFT  AIDROPBOX.CFT  AIMAPSRL.CFT  AIBOSSSRL.CFT
AIBONUSROUND.CFT  AIEVENTSOUND.CFT  AIMODSYSTEM.CFT  AIREPARATION.CFT
AISKILL.CFT  AISKILLTYPE.CFT  AISYSTEMDATA.CFT
MAP.CFT (188.505)  MAPSPOTWEAPON.CFT (12.823)
BOTNAME.CFT (9.415)   <-- única tabela "Bot*", e é só lista de nomes (formato antigo)
```

**Dados de navegação de AI presentes (`REZ\BUTES\*_DZ.LTC` / `*_AN.DAT`):** existem MUITOS — `AI_ATTACK_VENEZIA_DZ`, `AI_THEATER_DZ`, `AI_CATCH*_DZ`, `AI_CHICAGO_DZ`, `BLACKWIDOW_DZ`, `GHOST*_DZ`, `MEXICO_DZ`, `NANO_*_DZ`, `LOSTCITIES_DZ`, etc. (e os `_AN.DAT` correspondentes). Ou seja, **a base de navmesh de AI dos modos dedicados está lá** — coerente com o fato de o modo AI funcionar.

**Configuração:**
- `cf_hostsrv\Setting.ini` → seção `[GameMgmt]` tem **`#bot=1`** e **`#Number=0`** — ambos **COMENTADOS** (`#`). Pode ser relevante para o gating do recurso de bots (ver §4).
- `cf_hostsrv\GameOption.ini` → seção `[speedhack]` define distâncias de validação (`maxDistNormal`, `maxDistNano3Normal`, `maxDistGhost`...). Não bloqueia AI, mas é onde mora a checagem anti-cheat de movimento.
- `cf_gamesrv` **não tem REZ** próprio — só o `cf_hostsrv` carrega `RB001.REZ`.

---

## 3. O que o pack ARMAS já tem (referência comparativa disponível AGORA)

`...\UPGRADE CF Master\UPGRADE CF Master - ARMAS\ASSETS\RB001\Table\` contém um conjunto de AI **mais novo/completo** que o do servidor:

**Presentes no ARMAS e AUSENTES no servidor (diff direto):**
```
BOTCHARACTER.CFT        <-- FALTA no servidor
BOTLEVEL.CFT            <-- FALTA  (parâmetros de percepção/movimento do bot!)
BOTROOMDIFFICULTY.CFT   <-- FALTA  (quantos bots + loadout por dificuldade)
BOTNAMESET.CFT          <-- FALTA
AICONTROL137..AICONTROL149   (13 arquivos extras)
AIMOD137..AIMOD149           (13)
AI2BOOSTITEM / AI2PLANLIST / AI2REWARDINFO  (sistema "AI2"/Defence)
AICOMBINE / AIJUMARULE / AIPHASE / AIROUNDKICK / AISAFEBOX / AISLIDING
```

**Diferenças de versão (servidor tem versão ANTIGA/MENOR):**
| Arquivo | Servidor | ARMAS |
|---|---|---|
| `AICharacter.CFT` | 48.679 | **115.435** |
| `MAP.CFT` | 188.505 | **302.558** |
| `AIControl125.CFT` | 170.783 | 134.783 (formato/versão diferente) |

> Observação: a ARMAS também traz, em `RF016\MODELS\...` e `RF017\MODELTEXTURES\CHARACTER\AI*`, dezenas de **modelos/texturas de personagens de IA** (AI2, AI3, AI4, AI5, AI_Boss_Arena, AI_WAVE, NANO* etc.) — isso é **cliente** (renderização), não muda o "andar".

**Leitura:** o pack ARMAS contém o **superconjunto de tabelas Bot\*** que o servidor não tem. Mesmo antes do `ILUSION_BOTS_MAPS` chegar, o ARMAS já evidencia que **o servidor está com o subsistema Bot incompleto**. Falta validar se as Bot\* do ARMAS são compatíveis com este binário do `cf_hostsrv` (versão) e, principalmente, **se trazem os `_DZ` dos mapas comuns** (o ARMAS parece focado em armas/modelos; os `_DZ` de mapa comum provavelmente virão no pack Ilusion).

---

## 4. Pista de configuração: `#bot=1` comentado

Em `cf_hostsrv\Setting.ini`:
```
[GameMgmt]
#bot=1
#Number=0
```
Os dois flags estão **desativados (comentados)**. Dependendo do build, esse `bot=1` é o gate que habilita o "Add Bot" de sala normal no host. **A validar quando for corrigir:** se o recurso de bot de sala só liga com `bot=1` ativo. (Não alterar agora — read-only.)

---

## 5. Evidência dos LOGS — o modo AI dedicado JÁ ANDA

`C:\Log\crossfire\ServerApp\20260609\0_0\error_ServerApp_..._05.log` (partida de 09/06):
```
16:45:13.766 [INFO_] Loading world: AI_Att_20110729_Effect_01.DAT
16:45:13.790 [INFO_] Loaded world: AI_Att_20110729_Effect_01.DAT in 0.03s
16:45:23.850 [INFO_] [AI Mission]  StartRound:1
16:45:23.850 [INFO_] [Set AI_MaxBaseLife] BaseLife : 2
16:45:23.853 [INFO_] FindAndSetAIControllerIndex() Started
16:45:23.854 [INFO_] FindAndSetAIControllerIndex() End : 8 77919 Patrick226
16:46:04.355 [INFO_] AI Round Level Start : 2
...               AI Round Level Start : 3,4,5,6,7,8,9,10,11,12   (progressão normal)
16:48:06.765 [INFO_] [AI CalcEP] ... KillScore : 260
```
Interpretação:
- O **mundo carregado era um mapa de AI** (`AI_Att_...`), que tem `AI_ATT_20110729_EFFECT_01_DZ.LTC` + `_AN.DAT` em BUTES. **Navmesh presente → AI funciona, mata, progride round.** Não há erro de `path`, `navmesh`, `waypoint`, `LoadMap` ou `Bute` nos logs.
- `FindAndSetAIControllerIndex()` resolve um índice de controlador de AI (do `AIControl<N>`). Funciona.

**Já no host (GameServerManager), uma sala "comum" com bot:**
`...\GameServerManager\20260612\0\error_..._07.log`:
```
22:52:23.458 [INFO_] User 1 : __BOTS00
22:52:29.934 [INFO_] [ROOM_COUNT] NewRoomCount(4), Normal(1), AI(0), Wave(0).
```
Interpretação:
- Existe um usuário-bot `__BOTS00` e a sala é contada como **`Normal(1)`, `AI(0)`, `Wave(0)`** — ou seja, **NÃO** é uma sala de modo AI; é uma sala normal com bot adicionado. **É exatamente o cenário do sintoma** (bot entra como jogador "fantasma" mas, sem `BotLevel`/navmesh do mapa normal, fica parado).

> **Diferença-chave confirmada pelos logs:** o que ANDA é a **AI de modo dedicado** (mapa com `_DZ`). O que NÃO anda é o **BOT de sala Normal** — que depende das tabelas Bot\* (ausentes) e de `_DZ` no mapa comum (provavelmente ausente).

---

## 6. Hipóteses ordenadas (da mais provável à menos)

1. **(MAIS PROVÁVEL) Faltam as tabelas Bot\* no servidor.** `BotLevel.CFT` (percepção/movimento), `BotRoomDifficulty.CFT` (nº de bots+loadout), `BotCharacter.CFT`, `BotNameSet.CFT` não existem no `cf_hostsrv\rez\RB001.REZ`. Sem `BotLevel`, o bot spawna sem `view_range`/`hearing_range`/`tracing_rate`/`attack_speed` → **fica parado**. → Corrigir injetando as Bot\* (do Ilusion, ou validar as do ARMAS) no `RB001.REZ` do servidor.

2. **(MUITO PROVÁVEL, complementar) Faltam dados de navegação de AI (`<MAPA>_DZ.LTC`/`_AN.DAT`) para os MAPAS COMUNS** onde se quer bot. Mapas PvP normais não foram feitos com navmesh de AI. Sem `_DZ`, mesmo com Bot\* corretas, **não há grafo de caminho → bot não anda**. → O pack Ilusion deve trazer os `_DZ`/waypoints desses mapas (esse é, tipicamente, o "segredo" de um servidor com bots andando em mapa normal). Colocar no `RB001.REZ` do servidor (e o mapa/`.DAT` correspondente no cliente, se for mapa novo).

3. **(PROVÁVEL gate) `bot=1` comentado no `Setting.ini`** do host. Pode ser necessário ativar para o host habilitar/instanciar bots de sala normal com comportamento. → Validar e, se for o caso, descomentar `bot=1` (+`Number`).

4. **(POSSÍVEL) Incompatibilidade de versão das tabelas AI** com este binário. O servidor tem `AICharacter`/`MAP` MENORES e `AIControl125` de outra versão. Se as Bot\* do Ilusion referenciarem `ai_pattern`/`proto_id`/`map_num` que não existem nas tabelas atuais do servidor, o bot pode spawnar sem padrão válido → parado. → Garantir conjunto COESO (Bot\* + AIPattern + AICharacter + MAP do MESMO pack).

5. **(MENOS PROVÁVEL) Cliente sem os dados de mapa/AI.** O cliente é só renderização do movimento que o host manda; se o host não manda movimento (causas 1–4), o cliente não tem o que mostrar. Cliente só vira gargalo se o **MAPA novo** (mundo `.DAT`/modelos de AI) não existir no REZ do cliente — aí o jogador nem entra/vê. Para "bot parado em mapa que o jogador vê normal", o cliente não é a causa raiz.

---

## 7. Cliente × Servidor — onde cada coisa entra

| Item | Cliente (jogador) | Servidor (`cf_hostsrv`) |
|---|---|---|
| Tabelas `Bot*.CFT` (regra/comportamento) | (cópia existe, mas não decide) | **AUTORITATIVO — precisa ter** |
| Tabelas `AIControl/AIMod/AIPattern/AICharacter` | cópia | **AUTORITATIVO — precisa ter** |
| Navmesh de AI `<MAPA>_DZ.LTC` / `_AN.DAT` | — (não usado p/ render) | **precisa ter (no RB001.REZ\REZ\BUTES)** |
| Mundo do mapa `<mapa>.DAT` / modelos de mapa | **precisa ter** (para renderizar/entrar) | precisa para `Loading world` |
| Modelos/texturas dos personagens de AI (RF016/RF017) | **precisa ter** (render) | — |
| `Setting.ini` `bot=1` | — | **servidor** |

**Regra de ouro (igual ao fix de armas):** o **movimento do bot é decidido pelo `cf_hostsrv`**. Portanto as tabelas Bot\* e os `_DZ` têm de entrar no **`RB001.REZ` do servidor**. Modelos/mundo dos mapas novos entram no **cliente**.

---

## 8. PLANO de diagnóstico/correção passo-a-passo (NÃO aplicar agora)

### Fase A — Confirmar a causa (read-only, já 80% feito)
1. ✅ Servidor não tem `BotLevel/BotRoomDifficulty/BotCharacter/BotNameSet` (confirmado).
2. ✅ Modo AI dedicado anda (log 09/06) → navmesh de AI OK nos mapas de AI.
3. ✅ Sala com `__BOTS00` é `Normal`, não `AI/Wave` (confirmado).
4. ⏳ **Reproduzir com captura:** criar uma sala normal num mapa X, add bot, e ler em tempo real `ServerApp\<hoje>\*\error_*.log` procurando: ausência de `BotLevel`, `FindAndSetAIControllerIndex` retornando vazio, ou silêncio total de IA. (Comando de leitura, não de escrita.)
5. ⏳ Decodificar `BotRoomDifficulty`/`BotLevel` do pack Ilusion (quando chegar) e do ARMAS e conferir se as colunas batem com este binário.

### Fase B — Preparar os arquivos (em cópia, fora do servidor)
6. Backupear `cf_hostsrv\rez\RB001.REZ` (ex.: `.bak_pre_bots_<data>`). **Já há toolchain pronta:** `C:\cfrez.exe` + `C:\cfrezformat.dll` na VPS (usados no fix de armas).
7. Extrair o `RB001.REZ` do servidor → injetar em `TABLE\` as **Bot\*** + (se necessário) `AIControl137-149`/`AIMod137-149` e versões coesas de `AICharacter`/`AIPattern`/`MAP`, vindas do **pack Ilusion** (preferir Ilusion ao ARMAS, pois Ilusion = bots comprovadamente andando).
8. Injetar em `REZ\BUTES\` os **`<MAPA>_DZ.LTC` + `<MAPA>_AN.DAT`** dos mapas comuns alvo (vêm do Ilusion).
9. Repack do `RB001.REZ` com o **packer oficial** (round-trip do servidor NÃO é byte-idêntico mas é content-fiel — validar por **diff de conteúdo**, ver `cfmaster-arma-custom.md`).

### Fase C — Config + restart
10. Avaliar descomentar `bot=1` (e `Number`) em `cf_hostsrv\Setting.ini` (backup antes).
11. `Restart-Service cf_hostsrv -Force` (volta como `GameServerManager`+`ServerApp`; conferir portas 14001/5174 LISTEN). Lembrar do README do host: subir `cf_gamesrv` → `cf_hostsrv` → reiniciar `cf_gamesrv`.

### Fase D — Validar
12. Criar sala normal no mapa alvo + add bot → confirmar movimento.
13. Se o pack trouxer **mapas novos de bot**, garantir o **mundo/modelos no cliente** (senão o jogador não entra) e o **`_DZ` no servidor**.
14. Conferir nos logs: sem `EXCEPTION`/crash do `ServerApp`, e presença de movimento/round de bot.

### Itens a NÃO fazer
- Não aplicar tabelas AI soltas/versão divergente sem o conjunto coeso (risco de spawn sem padrão → bot parado, ou crash do `ServerApp`).
- Não mexer no cliente para "fazer bot andar" — a causa é servidor.

---

## 9. O que falta validar quando o `ILUSION_BOTS_MAPS` chegar

**Cheque final executado agora:**
```
Test-Path 'C:\Users\Administrator\Desktop\UPGRADE CF Master\ILUSION_BOTS_MAPS'  =>  False  (AINDA NÃO CHEGOU)
```
Desktop atual da VPS: `BLACK MARKET CFMASTER`, `UPGRADE CF Master`, `UPGRADE_CF_MASTER`, `CF M4 BRAZIL.zip`, `UPGRADE` (arquivo). Sem `ILUSION_BOTS_MAPS`.

**Quando chegar, verificar (read-only primeiro):**
1. **Tem as 4 tabelas Bot\*?** (`BotLevel/BotRoomDifficulty/BotCharacter/BotNameSet`) — e decodificar para conferir colunas vs binário do servidor.
2. **Tem `<MAPA>_DZ.LTC` + `_AN.DAT` para mapas COMUNS** (não só os de AI)? → este é o item que diferencia "bot anda em mapa normal".
3. **Tem mundos/mapas novos** (`.DAT` + modelos) que precisem ir no **cliente**?
4. **Versão coesa** de `AICharacter`/`AIPattern`/`MAP`/`AIControl` (para os `ai_pattern`/`proto_id` referenciados pelas Bot\* existirem)?
5. **Algum `Setting.ini`/config de exemplo** indicando `bot=1` ou flags do host?
6. Conferir se o Ilusion usa **`AIControl<N>` para bots de sala** ou só as Bot\* (alguns servers reaproveitam AIControl para o "bot" — isso muda o que injetar).

---

## 10. Arquivos/caminhos relevantes (referência)

**Servidor (VPS `178.83.141.35`):**
- `C:\pmang\crossfire\cf_hostsrv\rez\RB001.REZ` — REZ autoritativo do host (13 MB). `TABLE\*.CFT` + `REZ\BUTES\*_DZ.LTC`/`*_AN.DAT`.
- `C:\pmang\crossfire\cf_hostsrv\Setting.ini` — `[GameMgmt] #bot=1` (comentado).
- `C:\pmang\crossfire\cf_hostsrv\GameOption.ini` — `[speedhack]` (validação de movimento).
- `C:\pmang\crossfire\cf_gamesrv` — sem REZ próprio.
- Logs: `C:\Log\crossfire\ServerApp\<data>\<inst>\error_*.log` (mostra `Loading world`, `[AI Mission]`, `FindAndSetAIControllerIndex`, `AI Round Level Start`) e `C:\Log\crossfire\GameServerManager\<data>\0\error_*.log` (`[ROOM_COUNT] Normal/AI/Wave`, usuário `__BOTS00`).
- Toolchain já na VPS: `C:\cfrez.exe`, `C:\cfrezformat.dll`.

**Pack de referência disponível (VPS):**
- `C:\Users\Administrator\Desktop\UPGRADE CF Master\UPGRADE CF Master - ARMAS\ASSETS\RB001\Table\` — tem `BotCharacter/BotLevel/BotRoomDifficulty/BotNameSet`, `AIControl125-149`, `AIMod125-149`, `AICharacter` (115 KB), `MAP` (302 KB), `AIPattern`, etc.
- `C:\Users\Administrator\Desktop\UPGRADE CF Master\UPGRADE CF Master - ARMAS\ASSETS\RF016\MODELS\...AI*` e `...\RF017\MODELTEXTURES\CHARACTER\AI*` — modelos/texturas de personagens de IA (cliente).

**Pack pendente:**
- `C:\Users\Administrator\Desktop\UPGRADE CF Master\ILUSION_BOTS_MAPS` — **NÃO existe ainda** (cheque em §9).

**Memória relacionada:**
- `cfmaster-arma-custom.md` — princípio "o `cf_hostsrv` é autoritativo / tem a própria cópia do REZ"; toolchain `cfrez`/`CFLTC`; restart do host.
- `cfmaster-loja-itens-compra.md`, `cfmaster-melhorias-analise.md` — gotchas de REZ/SQL/wrapper SSH.

---

### Apêndice — método de decodificação dos CFT
Cifra de coluna: somar **+16** ao código ASCII de cada char do cabeçalho (`']' (0x5D) +16 = 'm'`). Permite ler os nomes de coluna sem ferramenta externa. Os valores das linhas seguem padrão análogo. (Usado em §1.3 para confirmar `bot_view_range`, `bot_hearing_range`, `mode_index`, `map_num`, etc.)
