# CrossFire Master (CF 1.0 privado) — Arquitetura de Serviços

> Documento técnico de arquitetura do servidor **CrossFire Master**, um servidor privado de
> **CrossFire 1.0** (engine LithTech Jupiter EX, base V2019/PH). Cobre cada serviço, portas,
> processos, dependências, ordem de boot, o gateway de banco (gDBGW), o registro de lobby
> (CF_MIN_CU), o cliente (FoxxFire 1.0), caminhos-chave e logs.
>
> **Finalidade:** referência para **replicar e manter** o servidor. Apenas leitura — nenhuma
> alteração foi feita ao gerar este documento. Senhas reais foram substituídas por placeholders
> (`<SENHA_VPS>`, `<SENHA_SQL>`).
>
> Última verificação ao vivo na VPS: **2026-06-13**.

---

## 1. Visão geral

O CrossFire Master roda em uma **VPS Windows Server 2022** (Kronic Host), hostname
`WIN-IK7N6SD2UBU`, **IP público `178.83.141.35`**. Toda a stack do jogo, o banco SQL Server e o
site PHP rodam na mesma máquina. O notebook local (`DESKTOP-HO22I81`) é apenas backup/cliente.

### 1.1 Componentes macro

| Camada | Componente | Tecnologia |
|---|---|---|
| Cliente | **FoxxFire 1.0** + Launcher Electron | LithTech Jupiter EX (CShell.dll / CrossFire.exe) |
| Front web | Site + downloads + banner in-game | PHP `php -S` (sem Apache), Cloudflare Tunnel |
| Login/lobby | cf_loginsrv, GameMgmtServer, cf_cgamesrv | Game servers nativos C++ (Win32, VC80) |
| Partida | cf_gamesrv (matchmaking) + cf_hostsrv (host de sala) | Game servers nativos C++ |
| Serviços auxiliares | ClanServer, cf_alserver, cf_buddyrelay | Game servers nativos C++ |
| Anti-cheat | HGW (+ HGWM) | nProtect / HackShield + HGW |
| Billing (EC/ZP) | BOQBillMicroGamesTx | Daemon .NET + nativo (gRPC 40051) |
| Gateway de banco | **gDBGW** | Console-app C++ (proxy de queries → SQL) |
| Persistência | SQL Server (MSSQLSERVER) | SQL Server, 5 bancos de jogo + auxiliares |

### 1.2 Princípio arquitetural central — o gateway gDBGW

**Nenhum game server fala SQL diretamente.** Todos os acessos a banco passam pelo **gDBGW**
(porta **6666**), que recebe pedidos por **ID de query** (`Q1`..`Q400`) e procs, executa contra o
SQL Server local (`127.0.0.1:1433`) e devolve o resultado serializado. As queries/procs ficam
catalogadas em `C:\Windows\DBGWMGR.ini`. Isso significa que **muitos bugs de "dado correto mas
comportamento errado" são na verdade do gateway** (cache de query, parâmetro duplicado, parser
desincronizado por célula zero-byte). Ver seções 5 e 9.

### 1.3 Caminhos-chave (na VPS)

| Item | Caminho |
|---|---|
| Game servers (binários) | `C:\pmang\crossfire\*` |
| ClanServer (build 2023 em uso) | `C:\cftest_clansvr\ClanServer.exe` |
| gDBGW (binário) | `C:\pmang\...` (rodado via NSSM, ver 4.5) |
| Configs do gateway/anti-cheat | `C:\Windows\gDBGW.ini`, `C:\Windows\DBGWMGR.ini`, `C:\Windows\CFDBLib.ini` |
| NSSM | `C:\Windows\nssm.exe` |
| Site web | `C:\xampp\htdocs\cf` (+ `htdocs\router.php` raiz porta 80) |
| Downloads | `C:\pmang\dl` |
| Scripts de operação | `C:\cfmigra\` (boot_order.ps1, watchdog.ps1, fixes) |
| Logs do gateway | `C:\Log\GDBGW`, `C:\Log\DBGWManager` |
| Logs de jogo | `C:\Log\crossfire\<servico>\<data>\` |
| Backups de banco | `C:\dbclone\`, `C:\cfmigra\db\`, `C:\pmang\db\restore2023\` |

---

## 2. Mapa de portas (estado ao vivo verificado 2026-06-13)

| Porta | Proto | Bind | Processo | Função | Exposição |
|---|---|---|---|---|---|
| **80** | TCP | 0.0.0.0 | php (router raiz) | HTTP — cliente busca EC/cash via CRS + banner in-game | **PÚBLICA (crítica)** |
| **6666** | TCP | 0.0.0.0 | gDBGW | **Gateway de banco** (todos os servers conectam aqui) | interna (self-IP) |
| **13005** | TCP | 0.0.0.0 | cf_loginsrv | Login MGMT (LMS — bridge interno login↔game) | pública (CF_TCP) |
| **13006** | TCP | 0.0.0.0 | cf_loginsrv | Login do cliente | **pública (cliente conecta aqui)** |
| **5174** | TCP | 178.83.141.35 | cf_gamesrv | Game server / matchmaking — **lobby server 01** | pública |
| **10011** | TCP | 178.83.141.35 | cf_cgamesrv | Channel/lobby/loja — **lobby server 02** | pública |
| **14001** | TCP | 0.0.0.0 | GameMgmtServer | Game Management (registro de game servers) | interna |
| **35100** | TCP | 0.0.0.0 | ClanServer | Servidor de clã | loopback/interna |
| **35200** | TCP | 178.83.141.35 | cf_alserver | Auto-League (torneio automático) | pública (CF_TCP) |
| **6500** | TCP | 178.83.141.35 | CF_BuddyRelay | Relay de amigos (buddy) | pública |
| **40051** | TCP | 0.0.0.0 | BOQV3MicroGamesTx | Billing (gRPC, saldo EC/ZP) | loopback (conexão sob demanda) |
| **16666** | TCP | 26.149.30.141¹ | HGW | Anti-cheat ↔ cliente | pública (CF_TCP) |
| **16667** | TCP | 26.149.30.141¹ | HGW | Anti-cheat HGW ↔ HGWM (PortGS) | interna |
| **15000** | TCP | 127.0.0.1 | HGW | Watchdog do HGW | loopback |
| **16668** | TCP | 127.0.0.1 | HGWM | Anti-cheat manager (validação de hash do cliente) | loopback (**Stopped no momento**) |
| **1433** | TCP | 0.0.0.0 | sqlservr | SQL Server | interna (firewall block externo) |
| **8081** | TCP | 0.0.0.0 | php | Origin web do tunnel (`cfweb`) | interna |
| **8090** | TCP | 0.0.0.0 | php | Downloads (`cfdl`) | interna |
| **22 / 3389** | TCP | — | sshd / RDP | Administração | pública (restrita) |
| **12000-12004** | UDP | — | game | Tráfego de partida (CF_UDP) | pública |

¹ **HGW faz bind no IP do Radmin VPN (`26.149.30.141`), NÃO em 127.0.0.1.** Se o Radmin VPN cair
ou trocar de IP, o HGW re-binda noutro IP e quebra a cadeia anti-cheat (ver 6.2 / 9).

> **Gotcha de firewall (DDoS hardening):** vários serviços conectam no **próprio IP público**
> (`178.83.141.35`), não em loopback (loginsrv→gDBGW :6666, cloudflared→:8081, matchmaking :14001).
> As regras BLOCK usam `RemoteAddress` = internet **exceto o self-IP**. Bloquear essas portas para
> "tudo" derruba o loginsrv. A **porta 80 é crítica** (cliente busca EC/cash em
> `http://178.83.141.35/cf/upload/CrossFireServer/`). Scripts: `C:\cfmigra\harden_fix.ps1`,
> `recover_login.ps1`, `fix_port80.ps1`.

---

## 3. Estado ao vivo dos serviços (2026-06-13)

| Status | Serviço | StartType | Processo (PID) | Threads |
|---|---|---|---|---|
| Running | BOQBillMicroGamesTx | Automatic | BOQV3MicroGamesTx (1116) | 26 |
| Running | cf_alserver | Automatic | cf_alserver (7592) | 29 |
| Running | cf_buddyrelay | Automatic | CF_BuddyRelay (860) | 17 |
| Running | cf_cgamesrv | Automatic | cf_cgamesrv (5568) | 24 |
| Running | cf_gamesrv | Automatic | cf_gamesrv (1428) | 48 |
| Running | cf_hostsrv | Automatic | GameServerManager (1520) + 5× ServerApp | 4 + 3 cada |
| Running | cf_loginsrv | Automatic | cf_loginsrv (5760) | 50 |
| Running | ClanServer | Automatic | ClanServer (6960) | 26 |
| Running | GameMgmtServer | Automatic | GameMgmtServer (5168) | 15 |
| Running | gDBGW | Automatic (via NSSM) | gDBGW (1068) | 142 |
| Running | HGW | Automatic | HGW (1856) | 25 |
| **Stopped** | **HGWM** | Automatic | — | — |
| Running | cfweb / cfweb80 / cfdl | Automatic (NSSM) | php | — |
| Running | Cloudflared | Automatic | cloudflared (3032) | 14 |
| Running | MSSQLSERVER | Automatic | sqlservr (7216) | 88 |
| Running | sshd | Automatic | — | — |

> Serviços `cf30_*` e `cfnovo_gdbgw` estão **Disabled** (pertencem ao ambiente CF 3.0 isolado e ao
> servidor "novo", fora de escopo desta arquitetura).

---

## 4. Serviços do jogo — detalhamento

### 4.1 cf_loginsrv — Login + Login Management Server (LMS)

| Campo | Valor |
|---|---|
| Serviço | `cf_loginsrv` (Automatic, serviço `sc` service-aware) |
| Binário | `C:\pmang\crossfire\cf_loginsrv\cf_loginsrv.exe` |
| Portas | **13006** (login do cliente), **13005** (Login MGMT / bridge interno) |
| Config | `cf_loginsrv\ServerInfo.ini` |

**Função:** primeiro ponto de contato do cliente. Autentica a conta (via gDBGW → `MYGAME_MEMBER` /
`CF_PH_GAME`), monta a **lista de servidores** lendo `CF_MIN_CU` (seção 7) e atua como **Login
Management Server (LMS)** — o bridge que mantém o estado de sessão sincronizado entre o login e os
game servers (cf_gamesrv/cf_cgamesrv têm `[BridgeServerExist] LoginMgmt=YES` apontando para
`LoginMgmtIP=127.0.0.1 / LoginMgmtPort=13005`).

**Config relevante (ServerInfo.ini):** `ServerMaxUser=250`, `ClientVersion=1001`,
`ServerServiceForcePort=13005`, `GameDB=CF_GAMEDB`, `DBPoint=CF_AUTHDB`.

**Dependências:** gDBGW (6666) deve estar pronto antes; GameMgmtServer (14001) para a malha de
estado. **Gotcha:** subir os game servers antes do loginsrv/GMS estarem prontos **emaranha a malha
de conexões** → erro `MGMT_EXCEPTION` / "failed to submit player info" / "servidores em
manutenção". Após reload da cadeia, o cf_loginsrv às vezes fica `Stopped` (subir com
`Start-Service cf_loginsrv`; precisa de 13005 **e** 13006 escutando).

### 4.2 cf_gamesrv — Game/Matchmaking Server (lobby server 01)

| Campo | Valor |
|---|---|
| Serviço | `cf_gamesrv` (Automatic) |
| Binário | `C:\pmang\crossfire\cf_gamesrv\cf_gamesrv.exe` (~2.1 MB) |
| Porta | **5174** (bind em `178.83.141.35`) — registrado como **SERVER 01** em CF_MIN_CU |
| Config | `cf_gamesrv\ServerInfo.ini` |

**Função:** servidor de matchmaking/partida do **lobby 01**. Carrega o **catálogo de itens** em
memória no boot (via gDBGW, query **Q3** sobre `CF_ITEM_INFO`), monta a lista de armas/loja enviada
ao cliente, processa o fim-de-partida (handler `UpdateGameResultAndUserPenalty` → `SP_GS_SCORE`,
logs em `CF_PH_LOG`), valida anti-cheat (hash via HGWM) e fala com billing para saldo.

**Config relevante:** `ServerMaxUser=3000`, `ServerServiceForceIP=178.83.141.35`,
`ServerServiceForcePort=5174`, `PHBillingIPandPORT=127.0.0.1:40051`, `SSN=318`, `ClientVersion=7`,
`ClanServerIP=178.83.141.35:35100`, `AutoLeagueServerIP=178.83.141.35:35200`,
`RelayServerIP=178.83.141.35:6500` (buddy), `BOT=1`, `AntiBot=1`, `WeaponHackUser=2`.
**Canais (10):** Room 1, Room 2, Mutation, Ghost, Sniper, Knife, Clan, Rookie (lv 9-26),
Veteran (lv 51-58), Elite (lv 75-99).

**Dependências:** gDBGW (catálogo + saves), GameMgmtServer (registro), billing (saldo), HGWM
(hash check), ClanServer/cf_alserver (toleram down). **Restart de cf_gamesrv sozinho é seguro**
(re-registra no GMS; só desconecta jogadores ~30s).

### 4.3 cf_cgamesrv — Channel/Lobby/Loja Server (lobby server 02)

| Campo | Valor |
|---|---|
| Serviço | `cf_cgamesrv` (Automatic) |
| Binário | `C:\pmang\crossfire\cf_cgamesrv\cf_cgamesrv.exe` |
| Porta | **10011** (bind `178.83.141.35`) — registrado como **SERVER 02** em CF_MIN_CU |
| Config | `cf_cgamesrv\ServerInfo.ini` |

**Função:** servidor de canal/lobby do **server 02**, e principal **host da loja (Item Shop)** —
mantém o catálogo da loja em memória. É onde o saldo **EC/ZP** é consultado sob demanda ao abrir o
Item Shop / telas de seleção. `ServerHighProperty=2` (CMM/canal) vs `=1` do gamesrv (MM).

**Config relevante:** `ServerMaxUser=3100`, `ServerServiceForcePort=10011`, `ClientVersion=6`,
mesmos billing/clan/autoleague/buddy do gamesrv. **Canais (10):** Welcome!, Free, Classic, Ranked,
VIP, Training, Events, Hardcore, Mutation, Ghost.

**Gotcha "failed to purchase":** se o cf_cgamesrv sobe **fora de ordem** (gDBGW ainda não pronto),
loga `Failed gDBGW ManagerInit` e **recusa toda compra** mesmo com banco perfeito. Fix = refresh de
catálogo na ordem (gDBGW→cf_gamesrv→cf_cgamesrv) com o gDBGW já no ar. Some a cada reboot — refazer
(seção 8.2). Script: `C:\Users\henrique\gachafix\refresh_catalog2.ps1`.

### 4.4 cf_hostsrv — Host de Sala (GameServerManager + ServerApp)

| Campo | Valor |
|---|---|
| Serviço | `cf_hostsrv` (Automatic) |
| Binário (manager) | `C:\pmang\crossfire\cf_hostsrv\GameServerManager.exe` |
| Processos | **GameServerManager** (1×) + **N× ServerApp** (5 ao vivo) |
| Diretório | `C:\pmang\crossfire\cf_hostsrv\` (tem `rez\RB001.REZ` próprio) |

**Função:** **host autoritativo das salas/partidas.** O `GameServerManager` orquestra e cada
`ServerApp` hospeda uma sala. Carrega a **própria cópia dos butes** (`cf_hostsrv\rez\RB001.REZ`) e
**valida a arma equipada** contra ela.

**Gotcha crítico (arma custom):** se uma arma existe no shop/inventário (cliente) mas **não está no
RB001.REZ do servidor**, na **partida** o host rejeita → "pula pra faca". Adicionar arma custom
exige injetar os butes `BF005` (arma) + `BF011` (item) no `RB001.REZ` **do servidor** também, com os
mesmos índices do cliente, e `Restart-Service cf_hostsrv -Force`. Modelos (RF124) são só do cliente.
Ver `cfmaster-arma-custom.md`.

### 4.5 gDBGW — Gateway de banco (DB Gateway)

| Campo | Valor |
|---|---|
| Serviço | `gDBGW` (Automatic) — **rodado via NSSM** (`C:\Windows\nssm.exe`), pois é console-app |
| Porta | **6666** (bind 0.0.0.0) |
| Configs | `C:\Windows\gDBGW.ini`, `C:\Windows\DBGWMGR.ini`, `C:\Windows\CFDBLib.ini` |
| Log | `C:\Log\GDBGW\GDBGW_*.txt` |

**Função:** **proxy central de banco.** Todos os game servers (login/game/cgame/host/clan/...)
abrem conexão no 6666 e pedem queries por **ID** (`Q1`..`Q400`) ou por proc. O gDBGW resolve a query
no `DBGWMGR.ini`, executa no SQL Server e serializa o resultado.

**Mapeamento de bancos (`gDBGW.ini`):**

| Slot | Banco (host) | Alias usado pelos servers | Conteúdo |
|---|---|---|---|
| 1 | `127.0.0.1,1433/CF_PH_GAME` | **CF_GAMEDB** | Jogo: usuários, itens, inventário, gacha |
| 2 | `127.0.0.1,1433/CF_PH_GUILD` | **CF_GUILDDB** | Clãs/guildas |
| 3 | `127.0.0.1,1433/CF_PH_LOG` | **CF_LOGDB** | Logs de partida/level-up/conexão |
| 4 | `127.0.0.1,1433/MYGAME_MEMBER` | **CF_AUTHDB** | Contas / autenticação (DBPoint) |
| 5 | `127.0.0.1,1433/HGW` | **HGW_DB** | Anti-cheat HGW |

- `[PORT] DBGW=6666`, `[AUTHSVR] USEAUTHSVR=0`, `[CONNMGNT] PING=1200 RECONN=120`, pool `NUM*=10`.
- Credenciais de DB no .ini são **criptografadas** (`DBENCUID*`/`DBENCPWD*`). Slots 1-4 usam o login
  `cf`; slot 5 (HGW) usa o login `hgw`. **O login `hgw` é obrigatório** — sem ele o gDBGW falha.
- `CFDBLib.ini` configura o conector secundário `HGW_DB` (`DBName=HGW`, `DBUser=hgw`,
  `DBPwd=<SENHA_SQL>`, `127.0.0.1:1433`).

**Gotchas do gDBGW (custaram caro):**
1. Os 3 inis vivem em **`C:\Windows`** (não em `C:\pmang`); sem eles → `gDBGW ERR INVALIDFILE`.
2. **Nunca gravar `DBGWMGR.ini`/inis em ASCII/UTF-8** — eles têm **comentários em coreano
   (multi-byte)**. Reescrever com encoding errado corrompe a config → o gateway misparseia → o
   cf_gamesrv **crasha em loop** (`EXCEPTION_ACCESS_VIOLATION 0x0057C904`, `CGDBGWParser`). Editar
   **no nível de bytes** (`ReadAllBytes`/splice/`WriteAllBytes`).
3. **Cache de query:** após `INSERT`/`UPDATE` em `CF_ITEM_INFO`, o gateway serve o **cache antigo** da
   query de carga de item (Q3) → compra rejeitada antes de chegar no proc. Fix = restart gDBGW e
   recarregar a cadeia.
4. **Parâmetro duplicado** no `DBGWMGR.ini` → `GDBGW_Err, Parameter name exists already` → o bind
   falha e a proc nem roda (foi a causa-raiz histórica do não-save de EXP via SP_GS_SCORE).
5. O gDBGW precisa de **>12 s** para ficar pronto. Se o cf_gamesrv subir antes → `gDBGW ERR
   NOACTIVESVR` → 5174 não binda. Religar só o cf_gamesrv resolve.

### 4.6 GameMgmtServer — Game Management Server (GMS)

| Campo | Valor |
|---|---|
| Serviço | `GameMgmtServer` (Automatic) |
| Binário | `C:\pmang\crossfire\cf_gms\GameMgmtServer.exe` |
| Porta | **14001** (bind 0.0.0.0) |

**Função:** registro/gerência central dos game servers. Os game servers se registram no GMS
(`GameMgmtIP1=127.0.0.1 / GameMgmtPort1=14001 / GameMgmtLastChannel1=10`). É parte da malha
login↔game. Subir fora de ordem causa `MGMT_EXCEPTION`.

### 4.7 ClanServer — Servidor de clã

| Campo | Valor |
|---|---|
| Serviço | `ClanServer` (Automatic) |
| Binário (em uso) | **`C:\cftest_clansvr\ClanServer.exe`** (build 2023, ~1.28 MB — estável) |
| Porta | **35100** (bind 0.0.0.0; `LISTEN_IP=0.0.0.0`) |
| Log | `C:\Log\crossfire\ClanServer\INFO\INFO.log` |

**Função:** criação/listagem/gerência de clãs (lê `CF_PH_GUILD`). Os game servers apontam
`ClanServerIP=178.83.141.35:35100`. O cf_gamesrv **tolera ClanServer down** (jogo funciona, só a UI
de clã fica indisponível).

**Histórico (importante para manutenção):** o build antigo (`cf_clansvr\ClanServer.exe`, 536576
bytes) tinha 2 problemas: (1) **Windows Defender corrompia o binário** removendo ~20 KB → excluir as
pastas no Defender; (2) **crash residual** determinístico `0xC000000D` em `EIP=0x450BC0` (sequência
CRT `strtol` numa tarefa periódica de sync de clã + sampler PDH). A solução adotada foi **trocar pelo
build 2023** em `C:\cftest_clansvr` (1286144 bytes), que **roda estável** (confirmado ao vivo:
Running, 35100 LISTEN). O `boot_order.ps1` sobe esse build após o gDBGW.

### 4.8 BOQBillMicroGamesTx — Billing (saldo EC/ZP)

| Campo | Valor |
|---|---|
| Serviço | `BOQBillMicroGamesTx` (Automatic) |
| Binário/processo | `C:\pmang\crossfire\cf_billsrv\BOQV3MicroGamesTx.exe` |
| Porta | **40051** (gRPC, bind 0.0.0.0) + componente nativo (23800) |
| Banco | `MICROGAMESBILL_DB` (saldo: `TAccountMst.CashReal`, `TCashMst.RemainCashAmt` por `UserNo=USN`) |
| Log | `C:\pmang\crossfire\cf_billsrv\BOQBillMicroGamesTxLog\<data>\BOQBill-*.txt` |

**Função:** servidor de billing que responde **saldo EC/ZP** ao cf_gamesrv/cf_cgamesrv
(`GetUserBalance`) e a compra por dinheiro real no site. Os game servers conectam via
`PHBillingIPandPORT=127.0.0.1:40051`. Established=0 no 40051 em idle é **normal** (conexão sob
demanda).

**Pré-requisitos de instalação (a migração não copiou — caso de replicação):**
1. **`bill.MSI`** instalado (componente **BOQN3MG 128.0.0**): `msiexec /i
   C:\pmang\crossfire\cf_billsrv\MSI\bill.MSI /quiet /norestart`. Sem ele → `Running Thread = 0` →
   `Demon AcceptClients Failed. So Terminate Program` → `GetUserBalance() Faild, ERROR CODE -1`.
2. **`regsvr32 /s C:\pmang\crossfire\cf_billsrv\BOQN3MG.dll`** (SysWOW64, 32-bit).
3. Chave de registro **`HKLM\SYSTEM\CurrentControlSet\Services\BOQBillMicroGamesTx\Parameters\
   ConnectionString`** (connection string criptografada do banco de billing). Sem ela → **erro
   1012** / "Updating EC information" travado. Importável do PC local (não é machine-bound):
   `C:\cfmigra\boq_params.reg`.

**Gotcha recorrente pós-reboot:** o EC volta "waiting". Causa: o worker gRPC 40051 morre
(`Running Thread = 0`), e a ordem de boot pode subir o cf_cgamesrv antes do billing reiniciar. Fix
= **restart limpo do billing** (Stop-Service + Stop-Process, esperar 40051 livre, Start-Service 1
instância, esperar ~30-60 s até bindar, **depois** restart cf_gamesrv + cf_cgamesrv). Scripts:
`C:\cfmigra\cf_ec_relink.ps1`, `cf_ec_final.ps1`. **Risco de dupla instância:** billing + gamesrv +
cgamesrv são todos `Automatic` → race no boot. O `boot_order.ps1` mata instâncias extras de billing.

### 4.9 cf_alserver — Auto-League (torneio automático)

| Campo | Valor |
|---|---|
| Serviço | `cf_alserver` (Automatic) | Binário | `C:\pmang\crossfire\cf_alserver\cf_alserver.exe` |
| Porta | **35200** (bind `178.83.141.35`) |

**Função:** servidor de torneio/ranked automático. Os game servers apontam
`AutoLeagueServerIP=178.83.141.35:35200`. **Gotcha:** a porta 35200 precisa estar no allowlist do
firewall (CF_TCP) — ficou de fora na migração e o default-deny barrava. Proc/tabela de autoleague
(`GSP_AL_GET_USER_LEAGUE_CANCEL`, `CF_AUTOLEAGUE_REWARD_USER_STORAGE`) faltando geram só ruído no log.

### 4.10 cf_buddyrelay — Relay de amigos (Buddy)

| Campo | Valor |
|---|---|
| Serviço | `cf_buddyrelay` (Automatic) | Binário | `cf_buddyrelay\CF_BuddyRelay.exe` |
| Porta | **6500** (bind `178.83.141.35`) |

**Função:** relay da lista de amigos/buddy entre os game servers
(`[NewBuddy] RelayServerIP=178.83.141.35:6500`, buffers recv:send = 600:400, pools de
user/clan/clanmember).

### 4.11 HGW / HGWM — Anti-cheat

| Campo | Valor |
|---|---|
| Serviço | `HGW` (Automatic) / `HGWM` (Automatic, **Stopped ao vivo**) |
| Binários | `C:\pmang\HGW\HGW.exe`, `C:\pmang\HGWM\HGWM.exe` |
| Portas HGW | **16666** (cliente), **16667** (PortGS→HGWM), **15000** (watchdog) |
| Porta HGWM | **16668** (validação de hash do game server) |
| Logs | `C:\Log\HGW`, `C:\Log\HGWM`, `C:\Log\HGWManager` |

**Função:** anti-cheat. **Cadeia:** cliente → HGW (16666) → game server → HGWM (16668) → HGW
(16667). O game server faz o **hash check** do cliente ao **entrar no canal** via HGWM; sem HGWM up →
`NO Valid Check Client's Login Hashed Value` → "disconnected from server".

**Gotchas:**
- **HGW faz bind no IP do Radmin VPN (`26.149.30.141`)**, não em 127.0.0.1 (ver `# Bind IP` no log
  do HGW). O `C:\pmang\HGWM\HGWM.ini` precisa de `[HGW] SERVER1=26.149.30.141` (= IP de bind do HGW)
  e `PORT1=16667`. Se o Radmin cair/trocar IP, o HGW re-binda e a cadeia quebra. Fix: `fix_hgwm.ps1`.
- HGWM aparece **Stopped** no estado atual — quando assim, o game server pode derrubar o cliente no
  hash check. Subir com `Start-Service HGWM` (confirmar 16668 LISTEN).

### 4.12 Componentes de infra (NSSM + Cloudflare)

- **gDBGW, cfweb, cfweb80, cfdl** rodam via **NSSM** (`C:\Windows\nssm.exe`) porque são
  console-apps (NSSM não funciona nos game servers — eles são service-aware → `StartServiceCtrlDispatcher Failed`).
- **cfweb** = `php -S` porta 8081 (docroot `C:\xampp\htdocs\cf` + router.php) — origin do tunnel.
- **cfweb80** = `php -S` **porta 80** (docroot raiz + `router.php`) — serve o **banner in-game** e o
  endpoint CRS de EC/cash que o cliente pede direto no IP.
- **cfdl** = `php -S` porta 8090 (downloads).
- **Cloudflared** = serviço `Cloudflared`, binPath
  `C:\pmang\cloudflared.exe tunnel --protocol http2 --retries 10 --grace-period 30s --logfile
  C:\pmang\cloudflared.log run --token <TOKEN_TUNNEL>`. Tunnel `cfmaster`
  (id `0f105212-dafd-4b6d-9c6d-5783ddeecabe`) → publica `crossfiremaster.online`. Loopback de admin
  do connector em 20241. **Gotcha 502:** ter dois connectors (VPS + notebook) causa round-robin →
  502 intermitente; manter só o connector da VPS. `--protocol http2` estabilizou o túnel.

---

## 5. Bancos de dados (SQL Server `MSSQLSERVER`, `127.0.0.1:1433`)

Logins SQL: `cf` (sysadmin) e `hgw` (sysadmin) — senhas = `<SENHA_SQL>`. Bancos presentes ao vivo:

| Banco | Alias gDBGW | Papel |
|---|---|---|
| **CF_PH_GAME** | CF_GAMEDB | **Banco principal de jogo** (CF_USER, CF_ITEM_INFO, CF_USER_INVENTORY, CF_GACHA_*, CF_MIN_CU, CF_USER_SACK, procs SP_BUY_*/SP_GS_*) |
| **CF_PH_GUILD** | CF_GUILDDB | Clãs/guildas (GUILD, GUILD_MEMBER, GUILD_LAYER_MARK, CF_CLAN_*) |
| **CF_PH_LOG** | CF_LOGDB | Logs (CF_GAME_LOG, CF_PLAY_LOG, CF_LEVELUP_LOG, CF_CONNECT_LOG + funções ConvDate/ConvVar) |
| **MYGAME_MEMBER** | CF_AUTHDB | Contas / autenticação |
| **HGW** | HGW_DB | Anti-cheat |
| **MICROGAMESBILL_DB** | (billing direto) | Saldo EC/ZP (TAccountMst, TCashMst) |
| CF_WEB | (site PHP) | Site (SITE_NOTICE, etc.) |
| CF_PH_GAME_0607 | — | Backup restaurado (referência de diff pré-regressão) |
| CF_CN_GAME / CF_CN_GUILD / CF_CN_LOG | — | Pacote de referência CN (não usado in-game) |
| G4BOX_SA_BILL_DB / BillDestiny / PMSDB_PH | — | Bancos do ambiente SA/PMS (não usados pelo 1.0) |
| master / model / msdb / tempdb | — | Sistema |

> **Lição de migração:** o gamesrv usa funções/tabelas em **vários** bancos, não só CF_PH_GAME.
> A migração precisa popular `CF_PH_LOG` (ConvDate/ConvVar + CF_GAME_LOG/CF_PLAY_LOG/CF_LEVELUP_LOG/
> CF_CONNECT_LOG) e `CF_PH_GUILD`, senão o save de fim-de-partida faz **rollback** → EXP/loadout não
> persistem.

**SQL na VPS:** `sqlcmd` não está no PATH; usar `.NET SqlClient` via PowerShell
(`Server=127.0.0.1;Database=CF_PH_GAME;User Id=cf;Password=<SENHA_SQL>;TrustServerCertificate=True;Encrypt=False`)
ou `sqlcmd -S 127.0.0.1 -U cf -P <SENHA_SQL> -C -d CF_PH_GAME -W` (o `-C` trust cert é necessário).

---

## 6. Fluxos

### 6.1 Fluxo de login → partida (caminho do cliente)

```
Cliente FoxxFire (CrossFire.exe)
  │ 1. Launcher Electron → launcher.php (crossfiremaster.online) → "Play"
  │ 2. Login TCP 13006 ────────────► cf_loginsrv ──(gDBGW 6666)──► MYGAME_MEMBER/CF_PH_GAME
  │ 3. cf_loginsrv lê CF_MIN_CU ────► devolve lista de servidores (01:5174, 02:10011)
  │ 4. Cliente escolhe servidor ───► cf_gamesrv 5174 / cf_cgamesrv 10011 (bind IP público)
  │    (LMS 13005 sincroniza sessão; GameMgmtServer 14001 registra)
  │ 5. Abrir Item Shop ────────────► cf_cgamesrv ──► billing 40051 (GetUserBalance EC/ZP)
  │                                              └─► gDBGW Q3 (catálogo CF_ITEM_INFO)
  │ 6. Entrar no canal/sala ───────► hash check via HGW 16666 → HGWM 16668
  │ 7. Partida ────────────────────► cf_hostsrv (GameServerManager → ServerApp), UDP 12000-12004
  │ 8. Fim de partida ─────────────► cf_gamesrv → SP_GS_SCORE + CF_PH_LOG (via gDBGW)
  └─ EC/cash CRS ──────────────────► http://178.83.141.35/cf/upload/CrossFireServer/ (porta 80)
```

### 6.2 Cliente (FoxxFire 1.0) — como conecta

- **Cliente:** FoxxFire 1.0 (LithTech Jupiter EX; `CrossFire.exe` + `CShell.dll`/`CRes.dll`).
  Pacotes: `CFMaster_1.0_v26.zip`, `CFMaster_Launcher.exe` (Electron, casca fina que carrega
  `crossfiremaster.online/launcher.php`). Download em `download.crossfiremaster.online`
  (pasta `C:\pmang\dl`).
- **Endpoint de login:** `version.ini` aponta `178.83.141.35:13006`. `MinimalVersion=1` (não
  aumentar sem patch novo, senão tranca todos os clientes).
- **Catálogo/loja:** o cliente baixa o catálogo no login; mudanças no servidor só aparecem após
  refresh de catálogo **e** o cliente fechar/relogar.
- **Butes (RB001.REZ):** define armas/itens no cliente (BF005=armas, BF011=itens). Índices da
  partida: **BF005 0-897** (898 renderiza no shop mas dropa na partida); BF011 esparso (até ~1059).
  Modelos em `RF124.REZ` (só cliente).
- **Banner in-game:** o webview do lobby pede `wolfsait.online/in-game/`; o `!START.bat` do cliente
  mapeia `wolfsait.online → 178.83.141.35` no hosts, e o `router.php` (porta 80) serve o banner.
- **Anti-cheat client-side (XTrap):** fecha o jogo no start se detectar acesso remoto
  (RustDesk/AnyDesk/OBS) ou faltar runtime VC++ (msvcr80). Dois clientes no mesmo PC também caem.

---

## 7. CF_MIN_CU — registro de lobby servers

Tabela em **`CF_PH_GAME..CF_MIN_CU`**. É a lista de servidores/canais que o cf_loginsrv e o
GameMgmtServer leem para montar a tela de seleção. Estado ao vivo (2026-06-13):

| SERVER | SERVER_NAME | SERVER_WEB_NAME | CONNECT_CNT | LIMIT_CNT | IP | PORT | EVENT |
|---|---|---|---|---|---|---|---|
| 01 | [BR] CrossFire Master | CFM | 1 | 2900 | 178.83.141.35 | **5174** (cf_gamesrv) | 0 |
| 02 | [BR] CrossFire Master #2 | CFM2 | 0 | 3000 | 178.83.141.35 | **10011** (cf_cgamesrv) | 0 |

**Regras / gotchas:**
- `CONNECT_CNT = -1` significa **manutenção** (servidor não aparece / "1005"). No boot o cf_gamesrv
  seta -1 transitório e volta a 0 sozinho; se ficar negativo: `UPDATE CF_MIN_CU SET CONNECT_CNT=0
  WHERE CONNECT_CNT<0`.
- O `IP` deve ser o **público** (`178.83.141.35`) — trocado na migração de `26.14.187.132`.
- **Lock órfão:** uma transação órfã do gDBGW pode travar CF_MIN_CU (SELECT dá Execution Timeout) →
  loginsrv/GMS não montam a lista → tudo em manutenção + game servers em flap. Diagnóstico:
  `sys.dm_tran_locks`/`sys.dm_exec_sessions` (`open_transaction_count>0`); fix: `KILL <spid>`.
  Leitura de CF_MIN_CU vazia/timeout ≠ tabela vazia → checar lock antes de assumir dados perdidos.
- `SSN=318` é o identificador do servidor usado nos game servers e em queries (`CF_REF_CODE`).

---

## 8. Boot / ordem de inicialização

### 8.1 Forma correta (validada): REBOOT da VPS

Subir os serviços fora de ordem **emaranha a malha** (loginsrv↔game↔GMS) → `MGMT_EXCEPTION` /
"failed to submit player info". A forma correta é **reboot da VPS**: a tarefa agendada **`cfboot`**
(onstart) roda `C:\cfmigra\boot_order.ps1`. Sequência efetiva do script:

1. `Start-Sleep 30` (aguarda OS estabilizar).
2. Sobe infra: `MSSQLSERVER`, `gDBGW`, `cloudflared`, `cfweb`, `cfweb80`, `cfdl`.
3. **Espera a porta 6666 (gDBGW) ficar LISTEN** (até 3 min) + 6 s de folga.
4. Restart na ordem: `cf_loginsrv` → `GameMgmtServer` → `cf_hostsrv` (5 s entre cada).
5. `Start-Service ClanServer` (build 2023, após gDBGW).
6. **Billing limpo, instância única:** Stop-Service + Stop-Process BOQV3MicroGamesTx, espera 40051
   livre, Start-Service, mata instâncias extras (mantém a mais antiga).
7. **Game servers (linkam no billing já no ar):** `cf_gamesrv` → `cf_cgamesrv` (6 s entre cada).
8. Auxiliares: `cf_buddyrelay` → `cf_alserver` → `HGW` (3 s entre cada) + `iphlpsvc`.

### 8.2 Pós-reboot — checklist manual (gotchas conhecidos)

Após o boot automático, costumam **não subir sozinhos** e precisam de atenção:
- `sshd`, `BOQBillMicroGamesTx`, `ClanServer`, **`HGWM`** — verificar e `Start-Service` se preciso.
- **Refresh de catálogo** (some a cada reboot): `Restart-Service gDBGW -Force` (esperar 6666+5174
  LISTEN) → `Restart-Service cf_gamesrv -Force` → `Restart-Service cf_cgamesrv -Force` →
  `UPDATE CF_MIN_CU SET CONNECT_CNT=0 WHERE CONNECT_CNT<0`. Confirmar no log do cf_cgamesrv que
  aparece `LoadGameModeInfo`/`Room Info` **sem** `Failed gDBGW ManagerInit`. Cliente reloga.
- **EC waiting:** restart limpo do billing antes dos game servers (seção 4.8).
- Painel GM web `crossfiremaster.online/pages/wpanel/servers.php` faz start/stop/restart por serviço
  e "iniciar todos na ordem".

---

## 9. Logs

| Componente | Caminho |
|---|---|
| Gateway gDBGW | `C:\Log\GDBGW\GDBGW_*.txt` (erros de bind/parser; `Out of present range`, `Parameter name exists already`) |
| gDBGW Manager | `C:\Log\DBGWManager\` |
| Game servers | `C:\Log\crossfire\<servico>\<data>\` (ex.: `cf_gamesrv\<data>\1_ERROR_*.log`, `error_*.log`, `cash_*.log`) |
| ClanServer | `C:\Log\crossfire\ClanServer\INFO\INFO.log` (+ ERROR.log) |
| Anti-cheat | `C:\Log\HGW\<data>\HGW\*.log` (linha `# Bind IP`), `C:\Log\HGWM\`, `C:\Log\HGWManager\` |
| Billing | `C:\pmang\crossfire\cf_billsrv\BOQBillMicroGamesTxLog\<data>\BOQBill-*.txt` |
| PMS | `C:\Log\PMSConn\` |
| Cloudflared | `C:\pmang\cloudflared.log` |

**Assinaturas de log úteis:**
- `update CF_USER_SACK set RIFLE_SLOT=... Out of present range` com valor `9223372036854775791` =
  categoria de item poluindo o slot primário (faca K/K virou M/R). Ver `cfmaster-primaria-categoria-fix.md`.
- `EXCEPTION_ACCESS_VIOLATION 0x0057C904 / 0x0057CCE3` (CGDBGWParser) = célula zero-byte em
  `CF_ITEM_INFO` (sanitizar todas as colunas varchar) ou ini corrompido em encoding errado.
- `0x004130F2` = valor de item fora do vocabulário ao montar o pacote para o cliente (crash na
  entrada do canal, não na carga).
- `GetUserBalance() Faild, ERROR CODE -1 / 450 / 1012` = billing (MSI / worker morto / ConnectionString).
- `NO Valid Check Client's Login Hashed Value` + `Failed to connect HGWM server` = HGWM down/IP errado.
- `Failed gDBGW ManagerInit` / `gDBGW ERR NOACTIVESVR` = game server subiu antes do gDBGW pronto.

---

## 10. Acesso e operação (resumo)

- **VPS:** SSH (OpenSSH) como `Administrator@178.83.141.35`, senha `<SENHA_VPS>` (RDP/RustDesk
  também). Lockout de conta desabilitado; `MaxStartups` **não** pode estar dentro de bloco `Match`
  no `sshd_config` (quebra o sshd).
- **Wrapper local (somente leitura):** `sh /tmp/vps.sh '<comando PowerShell>'`. Para scripts com
  quoting complexo/regex, **escrever `.ps1` local + `scp` (`/tmp/scpto.sh`) + `powershell -File`** —
  comandos inline com parênteses/aspas aninhadas falham pelo encadeamento SSH→PowerShell.
- **SQL:** `cf` / `<SENHA_SQL>` (sysadmin), `hgw` / `<SENHA_SQL>` (sysadmin), `127.0.0.1:1433`.
- **NSSM:** `C:\Windows\nssm.exe` (gerencia gDBGW, cfweb, cfweb80, cfdl).
- **Backups bons de banco:** `C:\dbclone\game_TUDO_OK_20260612_1933.bak` (tudo OK),
  `C:\cfmigra\db\CF_PH_GAME.bak` (06-07, referência de diff), `C:\pmang\db\restore2023\CF_PH_GAME.BAK`.

---

## 11. Inventário rápido (serviço → binário → porta)

| Serviço | Binário | Porta(s) | Banco principal |
|---|---|---|---|
| cf_loginsrv | `crossfire\cf_loginsrv\cf_loginsrv.exe` | 13006, 13005 | MYGAME_MEMBER / CF_PH_GAME |
| cf_gamesrv | `crossfire\cf_gamesrv\cf_gamesrv.exe` | 5174 (srv 01) | CF_PH_GAME / CF_PH_LOG |
| cf_cgamesrv | `crossfire\cf_cgamesrv\cf_cgamesrv.exe` | 10011 (srv 02) | CF_PH_GAME |
| cf_hostsrv | `crossfire\cf_hostsrv\GameServerManager.exe` (+ ServerApp) | host de sala | — (usa RB001.REZ) |
| GameMgmtServer | `crossfire\cf_gms\GameMgmtServer.exe` | 14001 | CF_PH_GAME |
| gDBGW | (NSSM) → console-app gDBGW | **6666** | todos (1-5) |
| ClanServer | `C:\cftest_clansvr\ClanServer.exe` | 35100 | CF_PH_GUILD |
| BOQBillMicroGamesTx | `crossfire\cf_billsrv\BOQV3MicroGamesTx.exe` | 40051 | MICROGAMESBILL_DB |
| cf_alserver | `crossfire\cf_alserver\cf_alserver.exe` | 35200 | CF_PH_GAME |
| cf_buddyrelay | `crossfire\cf_buddyrelay\CF_BuddyRelay.exe` | 6500 | CF_PH_GAME |
| HGW | `C:\pmang\HGW\HGW.exe` | 16666, 16667, 15000 | HGW |
| HGWM | `C:\pmang\HGWM\HGWM.exe` | 16668 | HGW |
| cfweb / cfweb80 / cfdl | (NSSM) `php -S` | 8081 / 80 / 8090 | CF_WEB / CF_PH_GAME |
| Cloudflared | `C:\pmang\cloudflared.exe ... run --token <TOKEN>` | (tunnel) | — |
| MSSQLSERVER | SQL Server | 1433 | — |

---

*Documento gerado por inspeção somente-leitura da VPS (178.83.141.35) e da memória do projeto.
Verificação ao vivo: serviços, processos, portas LISTEN, CF_MIN_CU, gDBGW.ini, DBGWMGR.ini,
ServerInfo.ini, binPaths e boot_order.ps1.*
