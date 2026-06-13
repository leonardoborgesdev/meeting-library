# CrossFire Master — Catálogo de Erros e Soluções

> Documento técnico consolidado de TODOS os erros encontrados e suas soluções no projeto **CrossFire Master** (CF 1.0, base V2019/PH).
> Compilado a partir das memórias do projeto e do `RUNBOOK_CFMASTER_FIXES_20260612.md`.
> Última consolidação: 2026-06-13.

---

## 0. Ambiente, Acesso e Convenções

### 0.1 Topologia do servidor
- **Servidor CF 1.0 ATIVO:** VPS `178.83.141.35` (Windows Server, hostname `WIN-IK7N6SD2UBU`).
- **PC local de referência** (onde tudo funcionava antes da migração): notebook `DESKTOP-HO22I81`.
- **Banco principal:** `CF_PH_GAME` (Microsoft SQL Server).
- **Cliente:** FoxxFire 1.0.
- **Site:** `crossfiremaster.online` (XAMPP/PHP).

### 0.2 Cadeia de serviços (ordem importa)
```
cliente → HGW(16666) → cf_gamesrv → HGWM(16668)
billing (BOQBillMicroGamesTx / 40051) → cf_gamesrv → cf_cgamesrv
gDBGW(6666) → cf_gamesrv(5174) / cf_cgamesrv(10011)
cf_hostsrv (GameServerManager + N×ServerApp; 14001/5174) = host da sala
ClanServer (clan; LISTEN_IP=0.0.0.0)
cf_loginsrv (13005/13006), GameMgmtServer (GMS)
```
- **gDBGW** (gateway de banco) escuta **6666**. As portas `5174` (srv01) e `10011` (srv02) são dos game servers.
- Estado de manutenção/lobby fica em `CF_MIN_CU.CONNECT_CNT`. `-1` = manutenção/lobby vazio ("1005"). Zerar para aparecer:
  `UPDATE CF_MIN_CU SET CONNECT_CNT=0 WHERE CONNECT_CNT<0`. No boot o cf_gamesrv seta `-1` transitório e volta a `0` sozinho.

### 0.3 Acesso a SQL
- `sqlcmd` **NÃO está no PATH** da VPS. Use uma das formas:
  - `sqlcmd -S 127.0.0.1 -U cf -P <SENHA> -C -d CF_PH_GAME -W` (quando disponível).
  - .NET `System.Data.SqlClient` via PowerShell `-File`. Connection string: `Server=127.0.0.1;Database=CF_PH_GAME;User Id=cf;Password=<SENHA>;Encrypt=False` (ou `TrustServerCertificate=True`).
- (As senhas reais foram OMITIDAS deste documento — consulte os helpers `cf_sql.ps1` / `/tmp/ap.sh` da máquina.)

### 0.4 Gotchas do wrapper SSH/SQL (recorrentes)
- O wrapper SSH é INSTÁVEL: sempre usar **retry loop**. `Start-Process ... -WindowStyle Hidden` detached NÃO executa de forma confiável via SSH→PS aninhado — rodar `.ps1` em foreground com `-File` (UPDATE/INSERT idempotentes).
- `sc.exe` cru e aspas aninhadas/`$()` retornam vazio → usar SEMPRE PowerShell + scripts `.ps1` + scp + `-File`.
- Passar valores com caracteres especiais via `-Q` pelo rexec/EncodedCommand **corrompe** (ex.: `'M|SM'` vira `'M SM'`). Sempre **gerar o `.sql` em arquivo e usar `sqlcmd -i`**.
- `scp` pode falhar **silenciosamente** → SEMPRE validar tamanho/MD5 do arquivo na VPS após a cópia.
- O wrapper `rexec` FALHA com comandos grandes (base64 embutido > ~8 KB) → usar `scp` para arquivos.

### 0.5 Decodificação de ITEM_CATEGORY (referência rápida — crítica)
| Categoria | Classe |
|-----------|--------|
| `M/R`  | Rifle (fuzil) |
| `M/SR` | Sniper |
| `M/SM` | SMG |
| `M/M`  | Metralhadora |
| `M/S`  | Shotgun |
| `S/P`  | Pistola |
| `K/K`  | Faca / melee (de verdade) |
| `D/HE`, `D/FB`, `D/SG` | Granadas |

> **REGRA DE OURO:** ao inserir/clonar armas em `CF_ITEM_INFO`, NUNCA deixar `ITEM_CATEGORY` errada. `ITEM_CATEGORY` define o SLOT/classe; `ITEM_INDEX` define o modelo. Categoria errada quebra o slot primário inteiro (ver §1).

### 0.6 Backups-chave (pontos de restauração)
- `C:\dbclone\game_TUDO_OK_20260612_1933.bak` — **TUDO funcionando** (armas + onboarding + compras). Ponto de restauração bom.
- `C:\dbclone\game_ARMAS_OK_20260612.bak` — só armas OK (antes do onboarding), 632 MB.
- `C:\cfmigra\db\CF_PH_GAME.bak` (06-07) — pré-regressão (referência de diff).
- `C:\dbclone\game.bak` (06-11).
- `C:\pmang\db\restore2023\CF_PH_GAME.BAK` — PH 1.8/2013 (fonte de procs/tabelas faltantes).
- Banco de comparação restaurado: `CF_PH_GAME_0607`.

---

## 1. Primárias não aparecem/salvam na sala (44 facas K/K→M/R)

**Status: RESOLVIDO (2026-06-12). BUG CRÍTICO.**

### 1.1 Sintoma
- TODAS as armas primárias (rifle `M/R`, sniper `M/SR`, smg `M/SM`) param de aparecer/salvar nas bags. Equipa mas não salva; na sala cai para a secundária.
- Pistola (`S/P`), faca e granada funcionam normal.
- **Universal:** todos os players, contas novas, clientes diferentes → é **server-side**.
- Sobrevive a reboot. Começou de repente (19:44 de 06-10, durante o trabalho do M4 Brasil).

### 1.2 Causa raiz
- **44 itens de FACA/melee** (Combat Axe, Kukri, Katana, Machete, KNIFE C0006, Field Shovel, Rose Axe, BC Axe, Christmas Axe, Kris, Chaos Hook, etc.) tiveram `ITEM_CATEGORY1/ITEM_CATEGORY2` trocada de `K/K` (faca) → `M/R` (primária).
- Isso **polui a categoria primária M/R** com itens que têm bute de FACA. O cliente monta a lista de primárias a partir do catálogo do servidor (campos `ITEM_CATEGORY1/2` do `CF_ITEM_INFO`); ao bater numa faca dentro do `M/R`, o **slot primário inteiro corrompe** → nenhuma primária vincula.
- Origem provável: o trabalho do M4 Brasil (clonagem com template de faca Kukri) — ver §9.

### 1.3 Como diagnosticar (assinatura no log)
- Log do gateway `C:\Log\GDBGW\GDBGW_*.txt`: erro **`Out of present range`** na query
  `update CF_USER_SACK set RIFLE_SLOT=...`
  com **valor `9223372036854775791`** (≈ `LLONG_MAX`, decrementa por sack) no 1º campo (`W1=RIFLE_SLOT`).
- Interpretação: o cliente está mandando **LIXO** no slot primário porque não conseguiu vincular a arma.
- Contagem como oráculo de regressão: `0` ocorrências ontem (bom) vs `N` hoje (quebrado).

### 1.4 Diagnóstico definitivo (o que destravou — comparar com backup bom)
1. Achar backup pré-regressão: `msdb.dbo.backupset` ou `.bak` em disco. Usado: `C:\cfmigra\db\CF_PH_GAME.bak` (06-07, 3 dias antes).
2. Restaurar como banco de comparação (NÃO sobrescrever o vivo):
   ```sql
   RESTORE DATABASE CF_PH_GAME_0607 FROM DISK='C:\cfmigra\db\CF_PH_GAME.bak'
     WITH MOVE 'CF_PH_GAME' TO 'C:\dbref\CF_PH_GAME_0607.mdf',
          MOVE 'CF_PH_GAME_log' TO 'C:\dbref\CF_PH_GAME_0607_log.ldf';
   ```
3. Diff do `CF_ITEM_INFO` das armas (`ITEM_TYPE='W'`) entre backup e vivo (campos categoria/index/use_place/sale) → revela as 44 com `K/K`→`M/R`.

### 1.5 Fix exato
Backup da tabela antes: `CF_ITEM_INFO_bak_catfix0612`.
```sql
UPDATE a SET a.ITEM_CATEGORY1='K', a.ITEM_CATEGORY2='K'
FROM CF_PH_GAME.dbo.CF_ITEM_INFO a
JOIN CF_PH_GAME_0607.dbo.CF_ITEM_INFO b ON a.ITEM_ID=b.ITEM_ID
WHERE a.ITEM_TYPE='W'
  AND b.ITEM_CATEGORY1='K' AND b.ITEM_CATEGORY2='K'
  AND (a.ITEM_CATEGORY1<>'K' OR a.ITEM_CATEGORY2<>'K');
```
- Resultado: `M/R` 330→286, `K/K` 13→57.
- Depois: **refresh de catálogo** (ver §4) + cliente FECHAR e reabrir (baixa o catálogo novo).
- Confirmado in-game: rifle salva e aparece.

### 1.6 Como reverter / backup
- Restaurar a tabela do backup `CF_ITEM_INFO_bak_catfix0612` (swap in-place, a tabela é HEAP):
  `BEGIN TRAN; DELETE FROM CF_ITEM_INFO; INSERT INTO CF_ITEM_INFO SELECT * FROM CF_ITEM_INFO_bak_catfix0612; COMMIT;`
- Ou restaurar o banco completo de `C:\dbclone\game_ARMAS_OK_20260612.bak`.

### 1.7 O que NÃO era (descartado por evidência)
- Ano `EFF_END=3000`, contagem de itens, item órfão/índice > 1059, `RB001.REZ` do cliente, binário, query/schema/proc (tudo batia com a referência). **Era só o dado de categoria.**

---

## 2. "Failed to purchase" (loja + lotto) — cf_cgamesrv "Failed gDBGW ManagerInit"

**Status: RESOLVIDO (operacional — recorre a cada reboot).**

### 2.1 Sintoma
- Comprar QUALQUER item na loja/item shop e itens do lotto dá **"failed to purchase"**.
- Itens do lotto giram OK no banco quando testados isoladamente.

### 2.2 Causa raiz
- O **cf_cgamesrv (shop server)** mantém o catálogo da loja **em memória**. Após reboot/restart fora de ordem ele sobe com **`Failed gDBGW ManagerInit`** (não conectou no gateway a tempo) e **recusa toda compra**, mesmo com o banco 100% correto.
- NÃO é dado: as procs `SP_BUY_GPITEM` / `SP_BUY_CASH_ITEM` / `SP_CONFIRM_GACHA` testadas com `EXEC ... ROLLBACK` retornam SUCESSO.

### 2.3 Como diagnosticar
- Log NOVO `C:\Log\crossfire\cf_cgamesrv\<data>\error_cf_cgamesrv_*`:
  - **Quebrado:** contém `Failed gDBGW ManagerInit` (e `gDBGW ERR NOACTIVESVR`).
  - **OK:** aparece `LoadGameModeInfo` / `Room Info` **SEM** `Failed gDBGW ManagerInit`.
- Sintoma enganoso: a proc testada direto no banco retorna positivo (inventory_srl), mas in-game falha → é o shop server, não o dado.

### 2.4 Fix exato
- Executar o **refresh de catálogo** (§4) com o gDBGW JÁ no ar (porta 6666 LISTEN) **ANTES** de reiniciar o cf_cgamesrv.
- Script pronto: `C:\Users\henrique\gachafix\refresh_catalog2.ps1`.
- O CLIENTE precisa fechar e relogar (catálogo é baixado no login).

### 2.5 Como reverter / observação
- Procedimento operacional, não altera dados → nada a reverter.
- **Recorre a cada reboot** — refazer SEMPRE que reiniciar o servidor.

---

## 3. Onboarding: nickname/soldado de conta nova travado (SP_GS_CREATE_USER_NEWBIE_DATA stub)

**Status: RESOLVIDO (2026-06-12).**

### 3.1 Sintoma
- Conta nova não consegue concluir nickname/escolha de soldado. Onboarding "para".
- Contas presas com `CF_USER.DEFAULT_CHAR_ITEM_ID='-'`.

### 3.2 Causa raiz
- `SP_GS_CREATE_USER_NEWBIE_DATA` era um **STUB**: fazia apenas `INSERT INTO CF_USER_NEWBIEMISSION_ACHIEVE(USN)`, mas a tabela tem **15 colunas `LEV_101..LEV_305` (int NOT NULL, sem default) + `NB_KIND` varchar(1)**.
- O insert falhava sempre (`0x80040e2f`), abortando o onboarding.
- O nickname em si (`SP_CREATE_USER`) sempre funcionou — o sintoma vinha do passo do newbie data abortar.

### 3.3 Como diagnosticar
- Log do game server (`C:\Log\crossfire\cf_gamesrv\<data>\1_ERROR_*.log`): `SP_GS_CREATE_USER_NEWBIE_DATA` falha + código `0x80040e2f`.
- Query: contas com `DEFAULT_CHAR_ITEM_ID='-'` sem linha em `CF_USER_NEWBIEMISSION_ACHIEVE`.

### 3.4 Fix exato
- Reescrever o proc inserindo TODAS as colunas: `LEV_*=0` e `NB_KIND='N'` (valor que `SP_GS_GAME_LOGIN` espera).
- Backup do proc original: `C:\proc_backup_SP_GS_CREATE_USER_NEWBIE_DATA.sql`.
- Destravar as 7 contas presas — criar a newbie row faltante (escolhem soldado in-game depois):
  - USN `77910, 77911, 77912, 77924, 77927, 77935, 77936`.

### 3.5 Como reverter / backup
- Restaurar o proc original de `C:\proc_backup_SP_GS_CREATE_USER_NEWBIE_DATA.sql` (`DROP/CREATE`).
- Banco com tudo OK: `C:\dbclone\game_TUDO_OK_20260612_1933.bak`.

### 3.6 Pendente (não regressão)
- Ordem da tela: conta nova vai direto pro personagem; deveria pedir nickname antes. Investigar.

---

## 4. Procedimento: REFRESH DE CATÁLOGO (rodar após CADA reboot)

> Procedimento operacional que conserta: §2 ("failed to purchase"), aplica mudanças de catálogo após edição de `CF_ITEM_INFO`, e tira a manutenção do lobby. **Some a cada reboot.**

### 4.1 Por que existe (cache do gDBGW)
- Após INSERIR/ALTERAR linhas em `CF_ITEM_INFO`, o item NÃO fica comprável só reiniciando os game servers — o **gDBGW cacheia o resultado da query de carga de item** (`Q3` em `C:\Windows\DBGWMGR.ini`).
- Os game servers recarregam a lista ATRAVÉS do gDBGW → se o gDBGW serve cache velho, a compra é rejeitada ANTES do proc (nada no `cash_*.log`).
- Testar o filtro de carga SEM reiniciar:
  ```sql
  SELECT COUNT(*) FROM CF_ITEM_INFO
  WHERE ITEM_ID IN (...) AND (USE_PLACE='A' OR USE_PLACE='C')
    AND SALE_STATUS!='C' AND SALE_START_DATE<=getdate() AND EFF_END_DATE>=getdate();
  -- 0 = não carrega
  ```

### 4.2 Procedimento (ordem obrigatória)
```powershell
Restart-Service gDBGW -Force          # esperar 6666 + 5174 LISTEN (race: pode precisar 2a vez)
Restart-Service cf_gamesrv -Force
Restart-Service cf_cgamesrv -Force    # recarrega o catalogo da LOJA
# tira manutencao (lobby):
sqlcmd ... -Q "UPDATE CF_MIN_CU SET CONNECT_CNT=0 WHERE CONNECT_CNT<0"
```
- Ordem completa com login/GMS quando necessário: `gDBGW → cf_loginsrv/GameMgmtServer → cf_gamesrv → cf_cgamesrv`.
- Script: `C:\Users\henrique\gachafix\refresh_catalog2.ps1`.

### 4.3 Verificações
- Portas **6666 / 5174 / 10011** LISTEN.
- Log do cf_cgamesrv SEM `Failed gDBGW ManagerInit`.
- CLIENTE fecha e reloga.

### 4.4 Gotchas do reload
- **Race do gDBGW:** o gDBGW precisa de **>12 s** para ficar pronto. Se o cf_gamesrv não bindar a 5174 após reload → **religar SÓ o cf_gamesrv** (gDBGW já up).
- O **cf_loginsrv às vezes fica Stopped** após reload → subir manual `Start-Service cf_loginsrv` (precisa 13005 E 13006 escutando).
- O `CONNECT_CNT` do server 02 volta a `-1` → re-zerar.

---

## 5. Missão diária duplicada (race no USP_CF_MISSION_DAY_DETAIL_R)

**Status: RESOLVIDO (pontual, 2026-06-12).**

### 5.1 Sintoma
- Missão diária do dia aparece duplicada (mission_no=1 duplicado; `mission_cnt=1` em vez de `3`).

### 5.2 Causa raiz
- Bug de **race** no `USP_CF_MISSION_DAY_DETAIL_R` (gera as missões sob demanda, sem lock).

### 5.3 Como diagnosticar
- `SELECT * FROM CF_MISSION_DETAIL / CF_MISSION_GROUP WHERE mission_start_date='AAAAMMDD'` → linhas duplicadas com `mission_no` repetido.

### 5.4 Fix exato
```sql
DELETE FROM CF_MISSION_DETAIL WHERE mission_start_date='20260612';
DELETE FROM CF_MISSION_GROUP  WHERE mission_start_date='20260612';
-- regenera limpo na proxima partida
```

### 5.5 Como reverter / backup
- Não há reversão necessária (a tabela regenera sozinha). Para segurança, snapshot do dia antes do DELETE.

---

## 6. EC/eCoin "aguardando" (billing) — múltiplas causas em série

**Status: RESOLVIDO de verdade (saldo + compra). Recorre no reboot (fix rápido validado).**

Funcionava no PC local (`DESKTOP-HO22I81`), quebrou só na VPS. Padrão geral: **arquivos/registro/MSI que a migração não copiou.**

### 6.1 Sintoma
- EC/ZP fica "aguardando" / "Updating EC information" / saldo `0`/`Waiting`. Compra por eCoin falha.
- `0` conexões ESTABLISHED no `40051` em idle é NORMAL (conexão é sob demanda — não é bug).

### 6.2 Causas raiz (descobertas em camadas)
1. **Dupla instância do billing daemon** `BOQV3MicroGamesTx.exe` (serviço `BOQBillMicroGamesTx`): serviço `Automatic` + `boot_order.ps1` + auto-recovery sobem instâncias concorrentes brigando pela porta `40051`. A 2ª falha o `accept()` e mata o programa (`Demon AcceptClients Failed. So Terminate Program`, `Running Thread = 0`).
2. **`bill.MSI` NUNCA instalado na VPS** (passo 2 do `_README.txt`). Sem ele o daemon sobe com `Running Thread = 0` → recusa conexões → cf_gamesrv loga `[CASH INFO]<GetUserBalance() Faild, ERROR CODE -1>`.
3. **Faltava a chave de registro** `HKLM\SYSTEM\CurrentControlSet\Services\BOQBillMicroGamesTx\Parameters\ConnectionString` (connection string criptografada do banco de billing, escrita pelo `-install` interativo que nunca rodou na VPS). Sem ela o erro virava **1012** (aceita a conexão mas não consulta o saldo).

### 6.3 Como diagnosticar
- Log .NET do billing: `C:\pmang\crossfire\cf_billsrv\BOQBillMicroGamesTxLog\<data>\BOQBill-*.txt` → procurar `AcceptClients Failed` / `Running Thread = 0`.
- `Get-Process BOQV3MicroGamesTx | Threads.Count` → saudável **>40** (sob carga ~26-27 também OK); zumbi **<10**.
- `cash_*.log` do cf_gamesrv → `GetUserBalance() Faild, ERROR CODE -1` (sem MSI) / `450` (worker morto) / `1012` (sem ConnectionString).
- Telas de setup (IP/porta/allowed-IP): `cf_billsrv\HELPFUL\*.png`.

### 6.4 Fix exato (3 camadas, todas necessárias)
```powershell
# 1) Instalar o MSI (componente BOQN3MG 128.0.0) + registrar a DLL 32-bit
msiexec /i "C:\pmang\crossfire\cf_billsrv\MSI\bill.MSI" /quiet /norestart
regsvr32 /s C:\pmang\crossfire\cf_billsrv\BOQN3MG.dll   # SysWOW64, 32-bit

# 2) Importar a ConnectionString do PC LOCAL (criptografia NAO e machine-bound)
#    no PC local: reg export ...\Parameters\ConnectionString  -> C:\cfmigra\boq_params.reg
reg import C:\cfmigra\boq_params.reg                     # arquivo: boq_params.reg

# 3) Restart LIMPO do billing (1 instancia)
Stop-Service BOQBillMicroGamesTx
Stop-Process -Force -Name BOQV3MicroGamesTx
# esperar 40051 livre, depois:
Start-Service BOQBillMicroGamesTx
# esperar ~30-60s ate 40051 voltar a LISTEN, ENTAO re-linkar os game servers:
Restart-Service cf_gamesrv
Restart-Service cf_cgamesrv
```
- Pós-MSI a instância sobe com ~49 threads e SEM `AcceptClients Failed`.
- Confirmação: abrir Item Shop → botão **Refresh** → saldo aparece; `cash_cf_gamesrv` loga `[CASH_ITEM_BUY_SUCCESS]`.
- Scripts validados (VPS, `C:\cfmigra`): `cf_bill_clean.ps1`, `cf_ec_final.ps1`, `cf_ec_relink.ps1`.

### 6.5 Recorrência pós-reboot (fix rápido)
- Todo reboot o EC volta "waiting" (worker gRPC 40051 morre: `Running Thread = 0` → `Demon AcceptClients Failed`; piora pela ordem de boot com cf_cgamesrv subindo antes do billing).
- O MSI, `regsvr32` e a ConnectionString PERSISTEM no reboot — NÃO refazer esses.
- **Fix:** restart LIMPO do billing (passo 3 acima). GOTCHA: relink dos game servers SOZINHO não resolve — tem que ser o billing limpo PRIMEIRO.

### 6.6 Como reverter / backups
- ConnectionString: `C:\cfmigra\boq_params.reg`.
- Dados de saldo nunca foram problema: `MICROGAMESBILL_DB` (CashReal/RemainCashAmt ~999M) e `CF_PH_GAME` (GAME_POINT/CASH ~999M).

### 6.7 Pendente (robustez no boot)
- billing + cf_gamesrv + cf_cgamesrv são todos `Automatic` → race no boot. Ideal: deixar SÓ o `boot_order.ps1` controlar a ordem (billing primeiro, single instance), ou cf_gamesrv/cf_cgamesrv como `Manual`, ou watchdog que mata instância dupla.

---

## 7. "Disconnected from server" ao ENTRAR no canal — HGWM (anti-cheat) caído por IP errado

**Status: RESOLVIDO (2026-06-10).**

### 7.1 Sintoma
- Loja/lobby funcionam, mas **ao clicar no servidor para ENTRAR no canal** → "disconnected from server".

### 7.2 Causa raiz
- O serviço **HGWM** (anti-cheat manager, porta `16668`) estava STOPPED/morrendo. O game server precisa dele para validar o hash anti-cheat do cliente ao entrar no canal; sem ele → kick.
- O HGWM morria porque `C:\pmang\HGWM\HGWM.ini` tinha `[HGW] SERVER1=189.1.172.93` (IP de OUTRO servidor) → não conectava no HGW → `16668` nunca bindava.
- Cadeia: `cliente → HGW(16666) → game server → HGWM(16668) → HGW(16667)`.

### 7.3 Como diagnosticar
- Log do game server `C:\Log\crossfire\cf_gamesrv\<data>\error_*.log`: **`NO Valid Check Client's Login Hashed Value!!!!`** + `Server Hashed Value`.
- Log `C:\Log\HGWManager\...`: **`Failed to connect to server : 127.0.0.1, 16668 / Failed to connect HGWM server`**.
- IP de bind real do HGW: `C:\Log\HGW\<data>\HGW\*.log` linha `# Bind IP : 26.149.30.141` (IP do **Radmin VPN**, NÃO 127.0.0.1!). Portas HGW: 16666 (cliente) + 16667 (PortGS→HGWM) + 15000 (watchdog).
- netstat: `Get-NetTCPConnection -Listen | ? OwningProcess -eq (Get-Process HGW).Id`.

### 7.4 Fix exato
```ini
; C:\pmang\HGWM\HGWM.ini  (backup: HGWM.ini.bak_ipfix)
[HGW]
SERVER1=26.149.30.141   ; = IP de bind do HGW (Radmin); PORT1=16667 ja correto
```
```powershell
Restart-Service HGWM        # 16668 binda na hora e fica up
Restart-Service cf_gamesrv
Restart-Service cf_cgamesrv
```
- Script: `C:\Users\henrique\gachafix\fix_hgwm.ps1`.

### 7.5 Como reverter / backup
- Restaurar `HGWM.ini.bak_ipfix`.

### 7.6 Gotcha
- Se o Radmin VPN cair/trocar IP, o HGW re-binda noutro IP e quebra de novo. Manter o Radmin conectado, ou setar bind fixo no HGW.

---

## 8. ClanServer crash (clan "não conecta") — 2 causas em série

**Status: 1ª causa RESOLVIDA; 2ª causa NÃO resolvida (clan TOLERADO desligado por decisão do usuário).**

### 8.1 Sintoma
- Clan "não funciona" / cliente mostra "not connected to clan server" no menu de clan.
- O game server tolera clan down (jogo funciona, só a UI de clan fica indisponível).

### 8.2 Causa raiz #1 — Windows Defender corrompe o binário
- O Defender detecta `ClanServer.exe` como ameaça (ThreatID `2147686570`, exe de game server 2013) e "remedia" **removendo ~20 KB** (`536576` → `516096` bytes), deixando o binário corrompido que crasha instantâneo.
- No PC local o Defender não mexeu → ficou íntegro (`536576`) → funcionava.

#### Fix #1
```powershell
Add-MpPreference -ExclusionPath "C:\pmang\crossfire\cf_clansvr"
Add-MpPreference -ExclusionPath "C:\cfmigra"
Add-MpPreference -ExclusionProcess "ClanServer.exe"
# depois restaurar o binario bom
```
- **MD5 do binário BOM = `2CEAEA12ADEC9E3A4135809E847459AE` (536576 bytes).**
- Cópia canônica: `C:\Users\henrique\Downloads\CFMASTER1.0\cf_clansvr\ClanServer.exe`.
- O ruim (stripado) = `1C2DFA12...` (516096 bytes). Backup do ruim: `ClanServer.exe.bak_vps516096`.
- GOTCHA: scp do binário às vezes falha silencioso → validar tamanho `536576` na VPS; e a cópia só "cola" com a exclusão do Defender ativa (senão re-strip).

### 8.3 Causa raiz #2 — crash residual (NÃO resolvido)
- Com binário íntegro + Defender excluído + PDH reconstruído (`lodctr /R` 64 e 32-bit) + WMI resync, o ClanServer **inicia 100%** (loga "Socket listening Success", "Success load base config/level info/member extend info/all count to exist clan" em `C:\Log\crossfire\ClanServer\INFO\INFO.log`), mas **crasha ~10-30 s depois** numa tarefa periódica interna. Crasha mesmo SOZINHO (game servers parados) → não é conexão.
- **RE de 250+ dumps:** crash 100% determinístico **`0xC000000D` (STATUS_INVALID_PARAMETER)** em **EIP=`0x450BC0`** = sequência CRT `strtol` → `_invalid_parameter` → `RaiseException` (validação de base 2..36). Pilha: `ClanQuery::GetWaitMemberList`, `Handler_DB_CL_CHANGE_CLAN_MARK`, `ClanDBReceiver` + sampler PDH `% Processor Time` → tarefa periódica de sync de clã via gDBGW + sampler CPU chamando `strtol` com argumento inválido.
- NÃO é migração: registro/arquivos/DLLs/inis/PDH/CPU batem 100% local×VPS (mesmos MD5; ClanServer NÃO usa registro `Parameters/ConnectionString`, lê de `.ini`). É **bug do binário** disparado por dado que o `strtol` parseia. `USE_PMS=1` faz crashar AINDA mais cedo (VPS não tem backend PMS).

#### Diagnóstico
- `ERROR.log` vazio (crash sem log). Minidump: `ClanServer.exe_*_0.0.0.0.dmp`.
- Parser de dump + disasm: `C:\cfmigra\parsedmp2.py`, `disasm.py`.

#### Estado tolerado (decisão do usuário "o clan vemos depois")
- ClanServer parado, `start=demand`, recovery=`none` (sem crash-loop).
- GOTCHA crítico: o `CFM_Watchdog` religava o ClanServer (serviço crítico parado) causando crash-loop → deixar o serviço **DISABLED** (não só stopped) para o watchdog não religar.
- Config de rede correta na VPS: `LISTEN_IP=0.0.0.0`; cgamesrv `ServerInfo.ini ClanServerIP=178.83.141.35`; SEM portproxy. Clan do comptecc (clankey=1) preservada.

#### Próximo passo real
- Analisar o minidump com cdb/windbg para achar a função exata, OU obter outro build do `ClanServer.exe` (suíte oficial do Caio).

---

## 9. ARMA CUSTOM — M4A1-C Brasil (as 4 camadas)

**Status: RESOLVIDO (2026-06-13) — M4A1-C Brasil aparecendo na partida (cliente FoxxFire + VPS).**

> Processo validado para adicionar arma custom no CF 1.0. O pacote do dono (`CF M4 BRAZIL.zip`) trazia modelos `.LTB` + texturas `.DTX` + ícones + blocos BF005/BF011 prontos + SQL.

### 9.1 Sintoma do "elo que faltava"
- A arma aparece no shop/inventário/modo-teste e até equipa, MAS na **partida** "pula para a faca" (não spawna). Modelos, índice, categoria, banco — tudo certo, e mesmo assim falha SÓ na partida.

### 9.2 Causa raiz — o SERVIDOR (cf_hostsrv) tem a PRÓPRIA cópia dos butes
- O **cf_hostsrv** (host da sala = processos `GameServerManager` + N×`ServerApp`) carrega o **PRÓPRIO** `C:\pmang\crossfire\cf_hostsrv\rez\RB001.REZ` e VALIDA a arma equipada contra os butes DELE.
- Se essa cópia não tem a arma no índice, o host **rejeita → faca**. O shop é 100% cliente (funciona); a partida é autoritativa do servidor (falha).
- Prova: os 3 `RB001.REZ` do servidor eram MD5-idênticos ao original; os butes BF005/BF011 do servidor são byte-idênticos aos originais do cliente (MD5 BF005 `7ed9fcea`, BF011 `be55f328`) → butes editados do cliente encaixam direto no servidor.

### 9.3 As 4 camadas (TODAS com o MESMO ITEM_ID e índices dentro do limite)
1. **Cliente BUTES** (`RB001.REZ` → `REZ\BUTES\BF011.LTC` + `BF005.LTC`):
   - Bloco `(Item ...)` no **BF011** (`ItemIndex`, `ItemID`, `ItemCode`, `ItemIndexInBute`=`WeaponIndex`, `ItemButeType 3`).
   - Bloco `(Weapon ...)` no **BF005** (`WeaponIndex` em slot `DummyWeapon` livre ≤897).
   - É clone estrutural de uma arma-base que funciona (M4A1 `C0001`); só mudam nome/modelos/skin/`ItemIndex`.
2. **Cliente MODELOS** (`RF124.REZ`): `.LTB`/`.DTX` em `Models\Weapons` (QV- mundo M/F), `Models\PlayerView` (PV- 1ª pessoa: base + `_BL`/`_GR` + `_WOMAN_BL`/`_WOMAN_GR`), `ModelTextures\...`, e ícones em `TEX\UI\WEAPONICON|AMMOICON|KILLMSG`. **Só cliente** (a rez do servidor vai só até RF123).
3. **Servidor BANCO** (`CF_PH_GAME..CF_ITEM_INFO`): `INSERT` clonando a linha-base (C0001), sobrescrevendo `ITEM_ID/CODE/NAME/INDEX`. **NUNCA setar `ITEM_CATEGORY` errada** (quebra o slot primário — ver §1). Categoria certa para rifle = `M/R`.
4. **Servidor BUTES** (`cf_hostsrv\rez\RB001.REZ`): injetar os 2 butes (BF005 + BF011), **MESMOS índices do cliente**, e reiniciar `cf_hostsrv`. **Modelos NÃO precisam no servidor** (ele não renderiza) — só os 2 butes. ← era o elo que faltava.

### 9.4 Índices do cliente — limite por contexto (shop tolera, PARTIDA não)
- **BF005 (armas): array da PARTIDA = 0–897 (cheio).** `WeaponIndex 898` RENDERIZA no shop-preview (carga sob demanda) mas é DROPADO na partida.
- Há **502 slots `DummyWeapon`** livres ≤897 (placeholder: `(Weapon (WeaponIndex N)(WeaponName "DummyWeapon"))`). **Reaproveitar um** (ex.: 140) por **swap atômico de índice** (Brasil 898↔140 dummy) — nada é removido, só os números trocam.
- Achar dummies: `grep -B1 DummyWeapon BF005.LTA | grep WeaponIndex`.
- **BF011 (itens): esparso (502 itens, max foi 1059).** Item da Brasil em 1060 funcionou (shop + inventário + partida, depois do servidor saber). `ItemIndexInBute` do item DEVE = `WeaponIndex` da arma (140).
- Conferir tudo: decompilar e `grep -oE '\(WeaponIndex [0-9]+' | sort -n | tail` / idem `ItemIndex`.

> Resumo do limite: **BF005 ≤897** (partida); **BF011 ≤~1059/1060** (item esparso). Cuidado com o limite do cliente.

### 9.5 Método de diagnóstico decisivo ("funciona no shop, faca na partida")
- Trocar os modelos custom da arma pelos **modelos BASE** (ex.: `m4a1.ltb` / `pv-m4a1`) mantendo índice/item, rebuildar, testar.
- Se AINDA pula para a faca → **NÃO são os modelos**, é bute/índice/servidor. Foi isso que isolou a causa para o lado servidor.
- Descartados também por evidência: versão LTB `09 00` igual às que funcionam; nome de osso `Bone01` igual ao AK47-BEAST; esqueletos/tamanhos normais.

### 9.6 Toolchain
- **Decompilar LTC→LTA:** `cfltc.exe <arq.LTC>` (1 arg), de `C:\Users\henrique\elite_rb001\conv\`.
- **Compilar LTA→LTC (magic CF `54 83 B2 E1`):** `CFLTC_Converter.exe <in.lta> <out.ltc>`, de `C:\Users\henrique\Desktop\cfwarserverfiles\`. Extensões **minúsculas** `.lta/.ltc`; adicionar a pasta ao PATH (chama `LTC.exe`); `echo "" |` no stdin. Conferir magic com `xxd -l4`.
- **REZ:** `cfrez.exe x <rez> <dir>` / `c <rez> <dir>` (precisa `cfrezformat.dll` ao lado).
  - Cliente: round-trip do cfrez é **byte-idêntico** (MD5 igual) → trocar só os 2 LTC e repack é seguro.
  - Servidor (RB001 13 MB, packer oficial): round-trip **NÃO** é byte-idêntico (cresce ~25 KB) mas é **CONTENT-fiel** — validar por **diff de conteúdo** (só BF005/BF011 mudam), NÃO por MD5 do container.
- **Transferir para VPS:** `scp` (o wrapper `rexec` FALHA com base64 grande). `cfrez.exe` + `cfrezformat.dll` ficaram em `C:\` na VPS (reusar para as +200 armas).
- **Restart host:** `Restart-Service cf_hostsrv -Force` (volta como `GameServerManager` + `ServerApp`; portas 14001/5174 LISTEN). Cliente: fechar e reabrir (lê RB001 no boot; cuidado para o patcher/launcher NÃO sobrescrever o RB001).

### 9.7 Backups deste fix
- Cliente: `RB001.REZ.bak_pre_m4_*` (sem M4), `.bak_pre140_*` (arma@898), `.bak_custom140_20260613` (arma@140 custom = atual).
- Servidor: `cf_hostsrv\rez\RB001.REZ.bak_pre_m4_140_20260613`.
- Banco: `CF_ITEM_INFO_bak_pre_m4brasil`.

### 9.8 Pendente (cosmético — arma já 100%)
- O ícone do bag/buy mostra o base. Causa: BF005 da Brasil tem `BigIconName "m4a1"`/`SmallIconName "m4a1"` (base).
- Convenção: `BigIconName "X"` → `TEX/UI/WEAPONICON/BUYWEAPON_INFO_X.DTX`.
- Fix: trocar para `"M4A1_C_BRASIL"` (o `BUYWEAPON_INFO_M4A1_C_BRASIL.DTX` JÁ existe no RF124). Pode faltar o small-icon — verificar/adicionar. Outros customs usam `BigIconName` próprio (ex.: "PSG_1_REDDRAGON", "M4A1-XMAS", "RPK-Gold").

---

## 10. Save de EXP/KD/perfil não salva + disconnect — 3 params DUPLICADOS no DBGWMGR.ini

**Status: RESOLVIDO (2026-06-10).** Bug-raiz que travava rank/clan/Point Mall em cascata.

### 10.1 Sintoma
- EXP/KD não salva → tudo `0/0` → rank travado em TRAINEE → quebra clan (popup "available for Staff Sergeant and higher") e Point Mall (BP 0).
- Também DERRUBA "disconnected from server" ao pontuar.
- Sinal de banco: `CF_USER.LAST_PLAY_DATE='3000-12-31'` em 100% das contas = nunca salvou.

### 10.2 Causa raiz (a real)
- A proc `SP_GS_SCORE` no banco vivo JÁ ESTÁ CERTA (93 params, compatível com o binário 2.1 MB da VPS — **NÃO trocar a proc**; a do `restore2023` é de outro build 4.8 MB e CRASHA).
- O gargalo é o **`C:\Windows\DBGWMGR.ini`** com **3 queries de nome de parâmetro DUPLICADO** que o gDBGW rejeita:
  - **Q148 = `SP_GS_SCORE`** (`PMD`×2) → save trava → rank→clan→Point Mall em cascata.
  - **Q225 = `GSP_CLAN_CREATE`** (`CREATE_LEVEL`×2) → criar clã falha.
  - **Q74 = load inventário/personagem/sack UNION** (`USN`×3, `EEDATE`×3) → carga de inventário/onboarding falha.

### 10.3 Como diagnosticar
- Log `C:\Log\GDBGW\GDBGW_*.txt`: **`GDBGW_Err, Parameter name exists already [QUERY:SP_GS_SCORE][PARAM:PMD]`** (e equivalentes para Q225/Q74), ANTES de chamar a proc.

### 10.4 Fix exato
- Renomear os labels duplicados (são placeholders `?` posicionais, semântica intacta): `PMD→PMDE`, `CREATE_LEVEL→CREATE_LEVEL2`, `USN/EEDATE` 2º/3º → `USN2/EEDATE2/USN3/EEDATE3`.
- Script: `C:\Users\henrique\gachafix\fix_dbgwini_dups.ps1` (LF puro, +6 bytes, aborta se ≠3 trocas, backup `.bak_dups_*`).
- Restart `gDBGW → cf_gamesrv → cf_cgamesrv`.
- Resultado: 0 dups no log, cf_gamesrv estável — destrava o cluster inteiro (save/KD/EXP/rank/clan/Point Mall/onboarding).

### 10.5 GOTCHA GRAVíssimo — encoding coreano
- **NUNCA escrever os arquivos de config do servidor (`DBGWMGR.ini`, `.ini` do gDBGW/HGW) em ASCII/UTF8** — eles contêm comentários em **COREANO (multi-byte)**.
- `[System.IO.File]::WriteAllText(...,ASCII)` ou `.Replace()` + write ASCII **DESTRÓI o coreano** → corrompe a config → o gDBGW misparseia as queries → **cf_gamesrv CRASHA em CRASH-LOOP** (`EXCEPTION_ACCESS_VIOLATION 0x0057C904`, `CGDBGWParser`) → "disconnected from server" toda hora.
- Sintoma: `Get-Item DBGWMGR.ini` fica MENOR que o backup; `Compare-Object` mostra linhas com lixo `A??A...`.
- **Fix para editar esses arquivos: edição no NÍVEL DE BYTES** — `ReadAllBytes`, achar a sequência ASCII alvo (ex.: `|PMK|I|INT|PMD|I|INT|PLEVEL|`), splice, `WriteAllBytes` (sem conversão de encoding). Backup sempre antes.

### 10.6 Como reverter / backup
- Restaurar `C:\Windows\DBGWMGR.ini` do backup `.bak_dups_*` (ou `.bak_pmd`).
- Reverter o ini é também o "desligar" do save (gateway recusa o bind → proc não roda → sem crash, mas sem save = bug original).

### 10.7 Becos sem saída (NÃO repetir)
- NÃO portar `SP_GS_SCORE` 93-param do `restore2023`/`fix_procs.sql`: o **formato de RETORNO não bate** com este binário → `EXCEPTION_ACCESS_VIOLATION 0x0057C904` no 1º score → crash-loop. A proc vívia já é a certa; o problema era só o ini.

---

## 11. Crash de CARGA de item — zero-byte em CF_ITEM_INFO (0x0057CCE3 / 0x0057C904)

**Status: RESOLVIDO (2026-06-08+).** Regra permanente de sanitização.

### 11.1 Sintoma
- cf_gamesrv em **crash-loop a cada ~2 min** (StartPending→Running→Stopped) ao carregar `CF_ITEM_INFO` → "disconnected from server" para todos.

### 11.2 Causa raiz
- Inserts/ativações em massa deixaram células com **string ZERO-BYTE (`DATALENGTH=0`)** em colunas onde o set bom NUNCA tem zero-byte (ex.: `FUNCTION1`, `CHAR_ITEM_ID`, `EVENT_GROUP`).
- O parser `CGDBGWParser::dbreaddata` (query `Q31`/`Q3 = select * from CF_ITEM_INFO`) **desincroniza** num campo zero-byte → `EXCEPTION_ACCESS_VIOLATION` (`0x0057CCE3` na 1ª variação, `0x0057C904` no gateway).
- O set bom só tem zero-byte em `DISPLAY_TYPE`/`ICON_TYPE` (que o loader tolera).

### 11.3 Como diagnosticar
- `C:\Log\crossfire\cf_gamesrv\<data>\1_ERROR_*.log`: `Error String : S|0` + `EXCEPTION_ACCESS_VIOLATION 0x0057CCE3`/`0x0057C904`.
- `Get-Process cf_gamesrv` age baixo (<6 s = crash-loop) + `sc qfailure cf_gamesrv` (RESTART) + Event Log Application `Exception 0xc0000005`.
- ARMADILHA: um scan que olha SÓ `FUNCTION1-5` falha (acha 5, corrige, mas continua crashando porque as culpadas eram `CHAR_ITEM_ID`/`EVENT_GROUP`).

### 11.4 Fix exato (REGRA permanente)
- Sanitizar **TODA** coluna varchar/char (cursor em `sys.columns`):
  ```sql
  UPDATE CF_ITEM_INFO SET [col]='-' WHERE col IS NULL OR DATALENGTH([col])=0;  -- para cada coluna varchar
  ```
  - Para `ITEM_INFO` usar `'N'` (o `'-'` esconde da loja: `Q61` filtra `ITEM_INFO != '-'`).
  - Sanitizar também `SHORT_NAME` com char fora de `0x20-0x7E`:
    `... WHERE SHORT_NAME LIKE '%[^ -~]%' COLLATE Latin1_General_BIN` → `'-'`.
- Script: `C:\Users\henrique\gachafix\sanitize_all.sql` (corrigiu 3100 células).
- Depois: refresh/reload (gDBGW flush) + garantir 5174 bindar. **Validar com monitor de >3 min** (o crash era ~2 min; 90 s não basta).
- **REGRA:** sempre rodar `sanitize_all.sql` (varchar completo) DEPOIS de qualquer insert/ativação em massa em `CF_ITEM_INFO`.

### 11.5 Como reverter / backup
- `CF_ITEM_INFO_workingbak` (1408, rollback) + `CF_ITEM_INFO_CLEAN` (golden 3030 corrigido).
- Swap (a tabela é HEAP, sem PK/identity): `BEGIN TRAN; DELETE FROM CF_ITEM_INFO; INSERT SELECT * FROM <bak>; COMMIT;`.
- Scripts: `cf_makeclean.ps1`, `cf_fixzero.ps1`, `cf_swapclean.ps1`, `cf_revertitems.ps1`, `cf_isstable.ps1`, `cf_bisect.ps1` (em `C:\cfmigra\`).

---

## 12. Crash de RUNTIME na ENTRADA do canal — valores fora do vocabulário (0x004130F2)

**Status: RESOLVIDO (2026-06-09).**

### 12.1 Sintoma
- Após resolver o crash de carga (§11), o catálogo full CARREGA mas **crasha quando o jogador CLICA no servidor/entra no canal** (monta o pacote da lista de itens). Endereço **`0x004130F2`** (≠ do crash de carga). Não é contagem (2008 itens também crasha), nem comprimento de texto.

### 12.2 Causa raiz
- **Valores fora do vocabulário/range** que o set bom (1408) nunca tem, usados como índice/case ao montar o item para o cliente.

### 12.3 Como diagnosticar / fix exato
- Bisseção por CONEXÃO: `cf_bisect.ps1 -N <k>` (base 1408 + TOP k de CLEAN), swap, restart, jogador clica, contar `ExceptionAddress=0x004130F2` (`cf_crashcount.ps1` / `cf_live.ps1`).
- Anomalias corrigidas (UPDATE para o valor do set bom):
  - `Function6`: bom = `-1..0`; novos tinham `1..70` → `SET Function6=0 WHERE Function6>0` (86 linhas).
  - `USE_TYPE2='F'` → `'N'`; `USE_TYPE3='O'` → `'E'`.
  - `ITEM_CATEGORY1 '1'/'6'`, `ITEM_CATEGORY2 '7'/'SFT'/'SHT'`, `SALE_PLACE 'A'/'W'`, `DISPLAY_TYPE 'C'/'P'`, `USE_PLACE 'W'` → remapeados para o valor good mais comum (`cf_enumfix.ps1`).
  - Clamp `GET_LIMIT_LEV>75→75`, `USE_EFFECT4>20300→20300`. `PRICE 999999999` é sentinela OK.
- Scripts: `cf_enumfix.ps1`, `cf_func6fix.ps1`, `cf_usetypefix.ps1`, `cf_fullnum.ps1`, `cf_numscan.ps1`.

### 12.4 Como reverter / backup
- `CF_ITEM_INFO_workingbak` (1408). `1408+150` CONFIRMADO jogável.

---

## 13. Limite de itens do binário — crash com catálogo grande

**Status: CONHECIDO / mitigado por lotes.**

### 13.1 Sintoma
- Com **2915 itens** o cf_gamesrv/cf_cgamesrv entra em **CRASH-LOOP** (portas 5174/10011 nunca bindam, `_err.log` VAZIO = crash duro sem log).
- Com **1984** sobe normal (mas a query Q3 leva ~9 s → startup lento, o Windows Service pode dar timeout/Stopped).

### 13.2 Causa raiz
- Limite de quantidade no executável (teto entre 1984 e 2915; provável ~2048/2500) ao carregar `CF_ITEM_INFO` via Q3 na init.

### 13.3 Fix / regra
- **NÃO inserir centenas de itens de uma vez** — fazer em LOTES e validar que o game server SOBE e BINDA as portas (5174/10011) entre cada lote.
- Subir com paciência: `Start-Service` + esperar ~20 s, religar se Stopped.

### 13.4 Como reverter
- `DELETE FROM CF_ITEM_INFO WHERE ITEM_ID IN (<novos>)` ou restaurar do `CF_ITEM_INFO_bak_*`, depois restart gDBGW + gamesrv + cgamesrv.
- Servidor estável testado em ~1984–2484 itens. Cuidado ao passar de ~2900.

---

## 14. "Failed to purchase" SELETIVO — mismatch cliente×servidor / vínculo por ITEM_ID do BF011

**Status: RESOLVIDO (diagnóstico definitivo + loja "fechada").**

### 14.1 Sintoma
- Comprar item específico dá "failed to purchase" (não todos — alguns funcionam).

### 14.2 Causa raiz
- O vínculo da compra é pelo **`ITEM_ID` exato do bloco `(Item ...)` do `BF011.LTC`** (cliente), NÃO pelo `ItemCode` (que é só rótulo).
- Se o servidor NÃO tem linha em `CF_ITEM_INFO` com aquele `ITEM_ID` exato → falha NO CLIENTE, antes de chegar no servidor (nada no `cash_*.log`, nenhum `sp_buy`).
- Versão diferente do catálogo: ~50% dos `ITEM_ID`s do servidor original apontam para itens diferentes do cliente FoxxFire → o cliente manda a compra com tipo/preço errado → no log `[ExecuteQuery Failed][sp_buy_gpitem|...] Cannot insert NULL into GAME_POINT`.

### 14.3 Como diagnosticar
- XEvents (sessão de captura): os que funcionam mostram `exec sp_buy_cash_item`; os que falham mostram **ZERO chamada de proc** (rejeitado antes do banco).
- Fonte da verdade = tabela do cliente FoxxFire: `C:\Users\henrique\Desktop\cf\LTC\EXCEL\Item.xlsx` / `Item.csv` / `ITEM_fresh.xlsx` (8231 itens).

### 14.4 Fix exato (escala)
- Parsear o BF011 inteiro (parser **window-based** confiável: `build_full2.ps1` → `all_items_full.csv`; NÃO usar block-split que subconta), cruzar com o servidor e inserir as linhas faltantes com os `ITEM_ID` exatos, usando **template por (ItemType, Cash)** de um item já presente no servidor (garante que o `ITEM_TYPE` do servidor bate com o que o cliente manda — crítico para GP: `SP_BUY_GPITEM` checa `item_type=@p_item_type`).
- Resultado: loja "fechada" — só faltam 6 itens de serviço de clã (adiados pelo dono) + placeholders hardcoded (`ItemID "1"`/`"2"`) não-compráveis por design.
- Scripts: `parse_bf011.ps1`, `build_full2.ps1`, `release_all.ps1` (em `C:\Users\henrique\gachafix\`). Backup `CF_ITEM_INFO_bak_release`.

### 14.5 Casos relacionados / fixes pontuais
- **SALE_TYPE sem proc:** só `'G'` (GP) e `'C'` (cash) têm proc. Itens `'F'` (BattlePoints), `'M'` (MasterPoints/[MP]) não têm → "failed to purchase". Fix: remapear (38 itens `'F'→'C'`, backup `CF_ITEM_INFO_bak_buyaudit`) + restart cf_gamesrv. Scripts `cf_buyaudit.ps1` / `cf_fixF.ps1`.
- **Defaults M4A1/M700/MP5 "falha no GP" = `EVENT_GROUP='M'`** (Mileage) travando o GP. Fix: `UPDATE CF_ITEM_INFO SET EVENT_GROUP='-' WHERE ITEM_ID IN(2010000101,2010000301,2010000401)`. Backup `CF_ITEM_INFO_bak_defaults`.

---

## 15. Caixas de Lotto (mega lotto) — caixa ausente / GAUGE esgotado

**Status: RESOLVIDO.**

### 15.1 Sintoma
- "failed to purchase THIS ITEM" ao comprar caixas de lotto de páginas específicas; ou caixa compra mas não gira.

### 15.2 Causa raiz
- A caixa não estava em `CF_ITEM_INFO` (rejeitada antes do banco — ver §14).
- Para **jogar** o lotto: `SP_CONFIRM_GACHA` faz `UPDATE CF_USER_INVENTORY SET GAUGE=GAUGE-1`; se `GAUGE-1<0` → result `-1`/`-6` → "failed to purchase".

### 15.3 Fix exato
- Caixa no servidor (modelo AWM-Pink `9000016301/02/03`): `ITEM_TYPE='F'`, `SALE_TYPE='C'`(eCoin)/`'G'`(GP), `SALE_PLACE='C'`, `FUNCTION4='21'`, `FUNCTION5=<pool/Func5 do BF011>`, **`USE_EFFECT3` = nº de jogadas** (1EA→1, 5EA→5, 10EA→10), `SALE_STATUS='O'`.
  - `INSERT...SELECT FROM '9000016301'` sobrescrevendo os campos acima.
- Recarregar GAUGE esgotado das contas de teste: `GAUGE=99999` (backup `CF_USER_INVENTORY_gaugebak0610`).
- Aplicado: 114+ caixas faltantes inseridas (eCoin + GP), todas com pool válido → compram E abrem.
- Scripts: `parse_lotto.ps1`, `lotto_fill.ps1`, `lotto_analyze.ps1`. Backup `CF_ITEM_INFO_bak_lottofill`.

### 15.4 Gacha-fantasma (gira → prêmio inexistente → falha/crash)
- `CF_GACHA_ITEM` tem linhas com `ITEM_ID` inexistente em `CF_ITEM_INFO`. As com `DISPLAY='Y'` (77) quebram. Fix: `UPDATE CF_GACHA_ITEM SET DISPLAY='N'` nessas. Backups `CF_GACHA_ITEM_bak_*` / `CF_GACHA_ITEM_ghostbak_0610`.

---

## 16. Armas/itens que CRASHAM ou caem para faca — VVIP, personagem, categoria de faca

**Status: RESOLVIDO (com regras).**

### 16.1 Arma VVIP → faca + crash = faltava a tabela CF_VVIP_ITEM_INFO
- **Sintoma:** armas VVIP (El Diablo C0397/2010044901, Savage Beast C0398/2010045001) caem para faca in-game e crashavam o servidor ao conectar o dono.
- **Causa:** faltava a tabela **`CF_VVIP_ITEM_INFO`** (heap 2 colunas int: `ITEM_INDEX`, `FUNCTION_NO`; lida pela `Q305` do `DBGWMGR.ini`) + a proc `GSP_VVIP_KILL_DEATH` (`Q306`). Sem a tabela: `Invalid object name 'CF_VVIP_ITEM_INFO'` → subsistema VVIP não inicializa → arma sem mapeamento → faca (e crash `EXCEPTION_ACCESS_VIOLATION 0x0057C904` no connect do dono).
- **Diagnóstico:** log `1_ERROR` com `Invalid object name 'CF_VVIP_ITEM_INFO'` perto do crash `0x0057C904`; dispara no CONNECT do dono da arma.
- **Fix:** recriar a tabela vazia + a proc do backup original `C:\pmang\db\restore2023\CF_PH_GAME.BAK` (script `C:\Users\henrique\gachafix\fix_render.sql`) + restart da cadeia. Com a tabela presente, dar VVIP no inventário NÃO crasha mais.
- (A regra antiga "não inserir VVIP" está SUPERADA — pode, desde que `CF_VVIP_ITEM_INFO` exista.)

### 16.2 Personagem (type C / client ItemType 2) copiando linha → quebra TODO MUNDO
- **Sintoma:** "invalid item information" + cliente FECHA ao entrar no servidor (todos os jogadores).
- **Causa:** inserir personagem (ex.: DEVGRU 1000002101/A0020) via `INSERT...SELECT` de outro char deixa um char cujas PARTES (dress hair/face/pouch) não existem/pertencem a outro char → `CCharItem::PutOnDress` Error ao montar a lista de personagens para TODOS → cliente recebe dado ruim.
- **Diagnóstico:** `C:\Log\crossfire\cf_gamesrv\<data>\1_ERROR_*.log` → procurar `PutOnDress`.
- **Fix:** `DELETE FROM CF_ITEM_INFO WHERE ITEM_CODE='A0020'`. Backup `CF_ITEM_INFO_bak_predevgrurm`.
- **Regra:** ao liberar "personagens", PULAR type C / client type 2 até ter o pipeline de dress completo.

### 16.3 Arma não renderiza na partida = ITEM_CATEGORY de faca (template Kukri)
- **Sintoma:** "ak47 não apareceu in-match" / arma vira faca; pode dar "invalid item information" ao montar a loja.
- **Causa:** `INSERT...SELECT` do template **Kukri** (`2010019101` = FACA, `K/K`) deixa TODA arma com categoria `K/K` → engine trata como faca/slot errado. (Esta é a mesma família de bug da §1.)
- **Fix:** setar `ITEM_CATEGORY1/2` pela classe real (mapeamento §0.5). Derivar o canônico por client-key (combo do servidor mais comum EXCLUINDO K/K), gerar UPDATEs SÓ para os K/K errados, gerar `.sql` LOCAL e `scp` + `sqlcmd -i` (o `-Q` via rexec mangla `'M|SM'`→`'M SM'`).
- Scripts `build_fixcats_sql.ps1` → `fixcats.sql`. Backup `CF_ITEM_INFO_bak_fixcats`.

### 16.4 Skins premium que caem para faca SEM crash = client-side
- **Sintoma:** El Diablo/Savage Beast/AK47-Knife RedDragon/Golden Winchester/M4A1-Ultimate Silver compram e mostram ícone, mas no spawn o jogador segura FACA.
- **Diagnóstico:** as linhas em `CF_ITEM_INFO` são **idênticas** às armas que renderizam (diff campo-a-campo = zero); inventário saudável; VVIP é red-herring.
- **Conclusão:** dado de servidor 100% correto → problema é **CLIENT-SIDE** (recurso de modelo `.ltb`/`.dtx` ausente no REZ de modelos do cliente IMPLANTADO, ou versão de cliente diferente). NÃO mexer no servidor.
- **Próximo passo:** extrair o REZ de MODELOS do cliente (não o RB001=BUTES) e checar os `.ltb` de `Models\WEAPONS\` dessas skins; comparar com o cliente do servidor que renderiza.

---

## 17. Banner in-game (lateral)

**Status: RESOLVIDO (2026-06-09).**

- **Sintoma:** banner lateral in-game fica branco.
- **Causa:** URL embutida na CLIENTE (`CShell.dll`): o webview pede `/in-game/` (e legado `/client-banner-lobby`) no host **`wolfsait.online`**.
- **Fix:** `fix_hosts_cfmaster.bat` (rodado pelo `!START.bat`) mapeia `wolfsait.online → 178.83.141.35`; `C:\xampp\htdocs\router.php` (porta 80, serviço `cfweb80`) serve `/in-game/` e `/client-banner-lobby` → `client-banner-lobby.php` (puxa `CF_WEB..SITE_NOTICE`).
- **Gotcha:** o jogador precisa rodar `!START.bat` (ou apagar o marcador `.cfm_hosts_ok`) para aplicar o hosts, senão fica branco.

---

## 18. Robustez transacional — XACT_ABORT ("comprou/girou e o item sumiu")

**Status: aplicado em 6/8 procs; 2 pendentes.**

- **Sintoma:** "comprou/girou e o item sumiu" (transação parcial sem rollback).
- **Causa:** procs com `BEGIN TRAN` sem `SET XACT_ABORT ON` → erro no meio deixa transação parcial.
- **Fix:** `SET XACT_ABORT ON` nas procs transacionais. Aplicado em: `SP_CONFIRM_GACHA`, `SP_SEND_GIFT`, `SP_USE_ITEM`, `SP_ACTIVATE_ITEM`, `SP_REPAIR`, `GSP_CF_GIVE_ITEM`.
  - **Faltam 2:** `SP_PACKAGE_ITEM_OPEN`, `SP_GS_GIVE_COMPENSATION` (sem `SET NOCOUNT ON`, a injeção após `AS` falhou — refazer).
  - Já tinham XACT_ABORT (pular): `SP_BUY_GPITEM`, `SP_BUY_CASH_ITEM`, `SP_GIVE_GPITEM`, `SP_CONFIRM_GIFT`, `SP_RESELL`.
- Motor de aplicação: `C:\Users\henrique\fase70-xact-fix\apply-xact-fix-MASSIVO.sql` (TROCAR `USE CF_SA_GAME`→`CF_PH_GAME`). Dump pré-ALTER via `OBJECT_DEFINITION`. Backups em `C:\pmang_FIXBAK_20260610\` e `fase70-xact-fix\*.sql`.

---

## 19. Pendências (precisam decisão/feature — NÃO são regressão)

| Item | Estado | Caminho |
|------|--------|---------|
| **Mercado negro [BP]** | 38 itens viraram `sale_type 'F'→'C'`; `GSP_BUY_FP_ITEM` e `CF_USER_FP` NUNCA existiram | Decidir moeda: (A) `sale_type='G'` GP via `SP_BUY_GPITEM`; (B) reverter 'F' + criar `GSP_BUY_FP_ITEM` (clone debitando FP) + dar FP. NUNCA tocar `ITEM_CATEGORY`. |
| **Missão de novato** | `CF_NEWBIE_MISSION_INFO`/`_REWARD_INFO` VAZIAS em todos os bancos | Implementar 15 missões do zero (sem valores de referência = risco de recompensa errada). É melhoria, não conserto. |
| **6 itens de serviço de clã** | Clan Name/Mark Change (9000028501-03 / 9000028601-03) | Adiados pelo dono até consertar o sistema de clã. |
| **Procs/tabela faltando (só ruído)** | `GSP_CF_USER_INVENTORY_EXPIRED`, `GSP_AL_GET_USER_LEAGUE_CANCEL`, `SP_GS_MISSION_LOG`, `CF_AUTOLEAGUE_REWARD_USER_STORAGE` | Pré-existentes; não travam. |
| **Comandos de GM in-game / torneio** | Relatados pelo dono | A investigar. |

---

## 20. Padrões e lições gerais (transversais)

1. **Diagnóstico-mestre:** comparar **banco vivo × backup pré-problema**. `RESTORE DATABASE ..._0607 WITH MOVE TO C:\dbref\...` e diff de procs (`DATALENGTH(definition)` / `OBJECT_DEFINITION`) e dados. Resolveu §1, §10, §16.1.
2. **Padrão "funciona no PC local, quebra na VPS"** = arquivo/registro/MSI/runtime que a migração não copiou (Defender, PDH, bill.MSI, ConnectionString, encoding). Replicar do local (`DESKTOP-HO22I81`) para a VPS.
3. **`CF_ITEM_INFO` é HEAP** (sem PK/identity, só DEFAULTs) → swap in-place preserva schema: `BEGIN TRAN; DELETE FROM CF_ITEM_INFO; INSERT SELECT * FROM <bak>; COMMIT;`.
4. **Após qualquer edição de catálogo:** rodar `sanitize_all.sql` (varchar completo, §11) + refresh de catálogo (§4) + validar com monitor de **>3 min**.
5. **NUNCA editar `.ini` coreano em ASCII** (§10.5) — edição byte-level.
6. **NUNCA setar `ITEM_CATEGORY` errada** em armas (§1, §16.3).
7. **Inserir itens em LOTES** e validar bind de portas entre lotes (§13).
8. **Backup ANTES de cada operação** (`CF_ITEM_INFO_bak_<motivo>`) e validar `scp`/MD5 na VPS.
9. **`Restart-Service cf_gamesrv` sozinho é seguro** (re-registra no GMS); só restart de loginsrv/GMS fora de ordem emaranha a malha.

---

*Fim do documento.*
