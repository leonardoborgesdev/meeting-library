# Guia de Replicação — Servidor CrossFire Master (CF 1.0) do Zero

Guia passo-a-passo para subir o servidor **CrossFire Master (CrossFire 1.0 / build FoxxFire)** numa **máquina/VPS Windows nova**, reproduzindo o ambiente que hoje roda na VPS `178.83.141.35` (Windows Server 2022).

> **Escopo:** este documento monta o SERVIDOR (game servers + banco + gateway de banco + anti-cheat + billing + web). O cliente do jogo é distribuído à parte (ver seção 6).
>
> **Aviso de segurança:** este guia NÃO contém senhas reais. Onde houver credencial, use os placeholders e preencha a seção **"Credenciais (preencher)"** no final. Nunca commite senhas reais em git.

Inventário base usado para escrever este guia (estado atual da VPS de produção): estrutura `C:\pmang`, serviços instalados, `.ini` de `C:\Windows`, bancos no SQL Server e a ordem de boot real (`C:\cfmigra\boot_order.ps1`).

---

## Índice

1. Pré-requisitos
2. Estrutura de pastas do servidor
3. Restaurar o banco de dados
4. Gateway de banco gДBGW (DBGWMGR.ini, porta 6666) + connection strings
5. Instalar/registrar os serviços e a ORDEM de boot
6. Arquivos do cliente necessários (RB001.REZ, RF*.REZ, butes)
7. Checklist pós-boot
8. O que versionar/guardar vs. o que é grande demais para git
9. Apêndice: gotchas que custaram caro
10. Credenciais (preencher)

---

## 1) Pré-requisitos

### 1.1 Sistema operacional
- **Windows Server 2019/2022** (produção atual = Windows Server 2022, hostname `WIN-...`). Funciona também em Windows 10/11 (o servidor "local" original rodava em notebook Windows 10).
- Acesso administrativo (RDP/RustDesk + OpenSSH habilitado se for operar remoto).
- Conta `Administrator` (ou equivalente local admin).

### 1.2 SQL Server
- **SQL Server 2016+ Express ou Standard** (Express basta para 1 instância). Habilitar:
  - **Autenticação mista** (SQL + Windows).
  - **TCP/IP** habilitado em `127.0.0.1:1433` (SQL Server Configuration Manager → Network Configuration → Protocols → TCP/IP → Enable; IPAll Port `1433`; reiniciar o serviço `MSSQLSERVER`).
- Os binários do gateway conectam por **TCP em `127.0.0.1,1433`** — sem TCP habilitado, o gДBGW não conecta.
- `sqlcmd` **não vem no PATH** numa VPS limpa. Para automação use o `.NET SqlClient` via PowerShell, ou instale o "SQL Server Command Line Utilities".

### 1.3 Redistribuíveis / runtimes (CRÍTICO)
Os binários são executáveis nativos antigos (build ~2010–2013, VS2010). Instale ANTES de subir os serviços:
- **Visual C++ Redistributable 2010 (x86 e x64)** — as DLLs do servidor são `*_VS2010.dll`.
- **Visual C++ Redistributable 2008/2005 (x86)** — o cliente/algumas DLLs dependem de `msvcr80`/`msvcr90`.
- **.NET Framework 4.x** — o billing daemon (`BOQV3MicroGamesTx.exe`) é .NET (componente gRPC na porta 40051).
- **NSSM** (`nssm.exe`) — usado para rodar como serviço os processos que são *console apps* (gДBGW, web `php -S`). Produção: `C:\Windows\nssm.exe`.
- **PHP + XAMPP** (opcional, só para o site/launcher web) — `C:\xampp`, com `C:\xampp\tmp` criado (senão `session_start` reclama). O Apache do XAMPP NÃO é usado; o site roda via `php -S`.
- **bill.MSI** (componente do billing) — ver seção 5.7. Sem ele o billing sobe com "Running Thread = 0" e o EC fica "aguardando".

### 1.4 Defender / antivírus (CRÍTICO)
O Windows Defender de um servidor novo **corrompe binários antigos de game server** (ex.: remove ~20 KB do `ClanServer.exe` → crash imediato). Antes de copiar binários:
```powershell
Add-MpPreference -ExclusionPath "C:\pmang"
Add-MpPreference -ExclusionPath "C:\cfmigra"
Add-MpPreference -ExclusionProcess "ClanServer.exe"
```
Depois valide os tamanhos dos `.exe` (ex.: `ClanServer.exe` íntegro = **536576 bytes**, MD5 `2CEAEA12ADEC9E3A4135809E847459AE`).

---

## 2) Estrutura de pastas do servidor

Raiz: **`C:\pmang`**. Subpastas e o que cada uma é:

| Caminho | O que é |
|---|---|
| `C:\pmang\crossfire\` | Game servers do CrossFire (cada serviço em sua subpasta). |
| `C:\pmang\crossfire\cf_loginsrv\` | **Login server** (autenticação; portas 13005/13006). |
| `C:\pmang\crossfire\cf_gms\` + serviço `GameMgmtServer` | **Game Management Server** (matchmaking/registro dos game servers; porta 14001). |
| `C:\pmang\crossfire\cf_gamesrv\` | **Game server** (matchmaking/sala; porta 5174). Tem `ServerInfo.ini` etc. |
| `C:\pmang\crossfire\cf_cgamesrv\` | **Channel/Lobby + LOJA** (porta 10011). É quem carrega o catálogo da loja. |
| `C:\pmang\crossfire\cf_hostsrv\` | **Host da sala** (`GameServerManager` + N×`ServerApp`; porta 14001/5174). **Tem a PRÓPRIA cópia de `rez\RB001.REZ`** — valida armas na partida (ver seção 6). |
| `C:\pmang\crossfire\cf_clansvr\` | **ClanServer** (porta 35100). Hoje instável (crash residual conhecido). |
| `C:\pmang\crossfire\cf_alserver\` | **AutoLeague server** (porta 35200). |
| `C:\pmang\crossfire\cf_buddyrelay\` | **Buddy/relay** de amigos (porta 6500). |
| `C:\pmang\crossfire\cf_billsrv\` | **Billing** (eCoin/cash). Daemon `BOQV3MicroGamesTx.exe`, serviço `BOQBillMicroGamesTx` (porta 40051 + 23800). Contém `MSI\bill.MSI`, `BOQN3MG.dll`, `_README.txt`, `HELPFUL\*.png`. |
| `C:\pmang\gDBGW\` | **Gateway de banco** (gДBGW.exe + DLLs `*_VS2010.dll`; porta 6666). Lê `gDBGW.ini` (local) + `DBGWMGR.ini`/`CFDBLib.ini` (em `C:\Windows`). `PWCrypto\` cifra senhas de DB. |
| `C:\pmang\HGW\` | **Anti-cheat principal (XTrap)** — `HGW.exe` (portas 16666 cliente / 16667 / 15000). |
| `C:\pmang\HGWM\` | **Anti-cheat manager** — `HGWM.exe` (porta 16668). O game server valida o hash do cliente contra o HGWM ao ENTRAR no canal. |
| `C:\pmang\Lib\` | DLLs compartilhadas (`B*_VS2010.dll`, `DBGWManager.dll`, `BOQN3MG.dll`, `PMSConn*.dll`, `libmysql.dll`). |
| `C:\pmang\PMS\` | Subsistema PMS (HA/MA/MC/PSC/utility) + `mktasks.bat`. |
| `C:\pmang\SGGM\` | SGGM agent/client/server (telemetria/segurança). |
| `C:\pmang\db\` | `.mdf/.ldf` em uso + `restore2023\` (backup original do banco, ex.: `CF_PH_GAME.BAK`). |
| `C:\pmang\dl\` | Pasta de **downloads do cliente** (servida em `download.crossfiremaster.online`): `CFMaster_1.0_v26.zip`, `CFMaster_RUNTIME_FIX.zip`, `CFMaster_Launcher.exe`, `version.ini`, `RB001_ORIGINAL.REZ`. |
| `C:\pmang\launcher_app\` | App do launcher (Electron casca fina). |
| `C:\pmang\cloudflared.exe` + `cf_tunnel_token.txt` | Túnel Cloudflare para o site (opcional). |
| `C:\cfmigra\` | **Pacote/scripts de migração e operação** (boot_order.ps1, watchdog.ps1, harden_fix.ps1, recover_login.ps1, cf_ec_*.ps1, db\, nssm.exe). |
| `C:\Windows\DBGWMGR.ini` / `CFDBLib.ini` / `gDBGW.ini` | **Configs que o gДBGW lê de C:\Windows** (NÃO ficam em C:\pmang — ver seção 4). |
| `C:\xampp\htdocs\` | Site/launcher/banner web (opcional). |
| `C:\dbclone\` | Backups `.bak` do banco (pontos de restauração). |

---

## 3) Restaurar o banco de dados

O servidor usa **8 bancos** no SQL Server (confirmado no inventário):

| Banco | Função |
|---|---|
| `CF_PH_GAME` | **Principal** — usuários, itens (`CF_ITEM_INFO`), inventário, lista de servidores (`CF_MIN_CU`), procs de compra/gacha. |
| `CF_PH_GUILD` | Clãs (`CF_CLAN_*`, `GSP_CLAN_*`). |
| `CF_PH_LOG` | Logs de jogo (EXP/level-up/conexão/partida). **Precisa das funções e tabelas de log** ou o save de EXP/loadout faz rollback (ver Apêndice). |
| `MYGAME_MEMBER` | Membros/auth (no gДBGW é o `CF_AUTHDB`). |
| `HGW` | Banco do anti-cheat. |
| `MICROGAMESBILL_DB` | **Billing** (eCoin/cash: `TAccountMst.CashReal`, `TCashMst.RemainCashAmt` por `UserNo=USN`). |
| `PMSDB_PH` | Subsistema PMS. |
| `CF_WEB` | Banco do site (avisos `SITE_NOTICE`, etc.). Opcional se não for subir o site. |

> Bancos extra que existem na VPS mas **não** fazem parte do CFMaster 1.0 e podem ser ignorados na replicação: `CF_CN_*`, `CF_PH_GAME_0607` (cópias de referência/diff), `CF30_*`, `G4BOX_SA_BILL_DB`, `BillDestiny`.

### 3.1 Restaurar a partir de `.bak`
Use um backup conhecido-bom. Ponto de restauração recomendado: **`game_TUDO_OK_*.bak`** (armas + onboarding + compras OK).

```sql
-- Exemplo para CF_PH_GAME (repetir para cada banco com seu .bak)
RESTORE DATABASE CF_PH_GAME
  FROM DISK = N'C:\dbclone\game_TUDO_OK_20260612_1933.bak'
  WITH MOVE 'CF_PH_GAME'      TO N'C:\pmang\db\CF_PH_GAME.mdf',
       MOVE 'CF_PH_GAME_log'  TO N'C:\pmang\db\CF_PH_GAME_log.ldf',
       REPLACE, RECOVERY;
```
Repita com os `.bak` de `CF_PH_GUILD` (`guild.bak`), `CF_PH_LOG` (`log.bak`), e os bancos de billing/auth/HGW/PMS conforme seus arquivos. Ajuste os nomes lógicos via `RESTORE FILELISTONLY FROM DISK='...'` se divergirem.

### 3.2 Criar o login `cf` (e `hgw`) e mapear nos bancos
O gДBGW autentica como **`cf`** nos bancos de jogo (DB1–DB4) e como **`hgw`** no banco HGW. Ambos `sysadmin` em produção.

```sql
-- Login de jogo
CREATE LOGIN cf  WITH PASSWORD = '<DB_CF_PASSWORD>',  CHECK_POLICY = OFF;
ALTER SERVER ROLE sysadmin ADD MEMBER cf;

-- Login do anti-cheat (obrigatório — gДBGW usa hgw para o banco HGW)
CREATE LOGIN hgw WITH PASSWORD = '<DB_HGW_PASSWORD>', CHECK_POLICY = OFF;
ALTER SERVER ROLE sysadmin ADD MEMBER hgw;
```

> Em produção `cf` e `hgw` usam a MESMA senha (`<DB_CF_PASSWORD>`). Mantenha como preferir, mas as connection strings da seção 4 precisam bater.

### 3.3 Consertar usuários órfãos (após restore)
Bancos restaurados de outra instância ficam com usuário órfão:
```sql
USE CF_PH_GAME;  ALTER USER cf  WITH LOGIN = cf;
USE CF_PH_GUILD; ALTER USER cf  WITH LOGIN = cf;
USE CF_PH_LOG;   ALTER USER cf  WITH LOGIN = cf;
USE MYGAME_MEMBER; ALTER USER cf WITH LOGIN = cf;
USE HGW;         ALTER USER hgw WITH LOGIN = hgw;
-- repetir p/ MICROGAMESBILL_DB, PMSDB_PH, CF_WEB
```

### 3.4 Ajustes obrigatórios pós-restore em `CF_PH_GAME`
A tabela `CF_MIN_CU` lista os servidores/canais que o cliente vê. Após restore:
```sql
USE CF_PH_GAME;
-- Apontar para o IP público desta máquina (substitua o IP antigo)
UPDATE CF_MIN_CU SET IP = '<SERVER_PUBLIC_IP>';
-- Tirar de "manutenção" (CONNECT_CNT < 0 ou != 0 = aparece em manutenção)
UPDATE CF_MIN_CU SET CONNECT_CNT = 0;
```
Esperado: 2 linhas (SERVER 01 = porta 5174, SERVER 02 = porta 10011), ambas com o IP público desta máquina.

---

## 4) Gateway de banco gДBGW (porta 6666) + connection strings

O **gДBGW** é o intermediário entre TODOS os game servers e o SQL Server. Os game servers nunca falam SQL direto — eles mandam queries numeradas (Q1–Q400) para o gДBGW, que executa no banco e devolve. Ele é **console app** → roda via **NSSM** (serviço `gDBGW`).

### 4.1 Os 3 arquivos que o gДBGW lê de `C:\Windows` (PEGADINHA)
Esses três NÃO ficam em `C:\pmang` — sem eles o gДBGW dá `gDBGW ERR INVALIDFILE`:

1. **`C:\Windows\gDBGW.ini`** — porta + mapeamento de bancos e credenciais (cifradas). Estrutura real (creds redigidas):
   ```ini
   [PORT]
   DBGW = 6666
   [DBNAME]
   NAME1 = 127.0.0.1,1433/CF_PH_GAME
   NAME2 = 127.0.0.1,1433/CF_PH_GUILD
   NAME3 = 127.0.0.1,1433/CF_PH_LOG
   NAME4 = 127.0.0.1,1433/MYGAME_MEMBER
   NAME5 = 127.0.0.1,1433/HGW
   [DBALIAS]
   ALIAS1 = CF_GAMEDB
   ALIAS2 = CF_GUILDDB
   ALIAS3 = CF_LOGDB
   ALIAS4 = CF_AUTHDB
   ALIAS5 = HGW_DB
   [DBUIDINFO]
   DBENCUID1..5 = <UID cifrado>   ; DB1-4 = login 'cf', DB5 = login 'hgw'
   [DBPWDINFO]
   DBENCPWD1..5 = <senha cifrada>
   [INUM]
   NUM1..5 = 10                   ; nº de conexões por pool
   ```
   > As senhas/UIDs são **cifrados** com o utilitário `C:\pmang\gDBGW\PWCrypto\pwCrypto.exe`. Gere os blobs com a senha real (`<DB_CF_PASSWORD>` / `<DB_HGW_PASSWORD>`) e cole nos campos `DBENC*`. NÃO coloque senha em texto puro aqui.
   > **Nota:** há também uma cópia de `gDBGW.ini` em `C:\pmang\gDBGW\` (idêntica). Mantenha as duas em sincronia; a de `C:\Windows` é a que vale.

2. **`C:\Windows\DBGWMGR.ini`** — **catálogo de queries Q1–Q400** (~110 KB). É o "dicionário" de toda query SQL que os game servers podem disparar (compra de item, save de partida, gacha, clã, VVIP etc.). **Copie do servidor de origem como está** — editar só quando for adicionar/ajustar uma query (ex.: tabelas de log do CF_PH_LOG, VVIP). Sem ele, nenhuma operação de banco funciona.

3. **`C:\Windows\CFDBLib.ini`** — conector dedicado do **HGW** (anti-cheat). Estrutura real (senha redigida):
   ```ini
   [DBInfo]
   UseEncrypt=0
   LOG_DRIVE=C
   AliasCount=1
   AliasName1=HGW_DB
   AsyncThreadCount1=5
   DBType1=mssql
   DBName1=HGW
   DBUser1=hgw
   DBPwd1=<DB_HGW_PASSWORD>     ; texto puro (UseEncrypt=0)
   DBSvr1=127.0.0.1
   DBPort1=1433
   ```

### 4.2 Connection strings de automação (PowerShell / scripts)
Para scripts de operação (não para os serviços, que usam o gДBGW):
```
Server=127.0.0.1;Database=CF_PH_GAME;User Id=cf;Password=<DB_CF_PASSWORD>;TrustServerCertificate=True;Encrypt=False
```
`sqlcmd` (se instalado):
```
sqlcmd -S 127.0.0.1 -U cf -P <DB_CF_PASSWORD> -C -d CF_PH_GAME -W
```
(`-C` = trust server cert; sem ele dá "certificate chain not trusted".)

### 4.3 Instalar o gДBGW como serviço
```powershell
C:\Windows\nssm.exe install gDBGW "C:\pmang\gDBGW\gDBGW.exe"
C:\Windows\nssm.exe set gDBGW AppDirectory "C:\pmang\gDBGW"
C:\Windows\nssm.exe set gDBGW Start SERVICE_AUTO_START
Start-Service gDBGW
```
**O gДBGW precisa de >12 s para ficar pronto** após iniciar. Só suba os game servers DEPOIS que a porta 6666 estiver `LISTEN`.

---

## 5) Instalar/registrar os serviços e a ORDEM de boot

### 5.1 Tipos de serviço (IMPORTA)
- **Game servers** (`cf_loginsrv`, `cf_gamesrv`, `cf_cgamesrv`, `GameMgmtServer`, `cf_hostsrv`, `cf_clansvr`/`ClanServer`, `cf_alserver`, `cf_buddyrelay`, `HGW`, `HGWM`, `BOQBillMicroGamesTx`) são **service-aware** (chamam `StartServiceCtrlDispatcher`) → instale com **`sc create`** (nativo). **NÃO** use NSSM neles (dá `StartServiceCtrlDispatcher Failed` / erro 1063).
- **Console apps** (`gДBGW`, web `php -S`) → use **NSSM**.

### 5.2 Criar os serviços nativos (exemplo)
```powershell
sc.exe create cf_loginsrv   binPath= "C:\pmang\crossfire\cf_loginsrv\cf_loginsrv.exe"   start= auto
sc.exe create GameMgmtServer binPath= "C:\pmang\crossfire\cf_gms\GameMgmtServer.exe"      start= auto
sc.exe create cf_hostsrv    binPath= "C:\pmang\crossfire\cf_hostsrv\cf_hostsrv.exe"       start= auto
sc.exe create cf_gamesrv    binPath= "C:\pmang\crossfire\cf_gamesrv\cf_gamesrv.exe"       start= auto
sc.exe create cf_cgamesrv   binPath= "C:\pmang\crossfire\cf_cgamesrv\cf_cgamesrv.exe"     start= auto
sc.exe create cf_alserver   binPath= "C:\pmang\crossfire\cf_alserver\cf_alserver.exe"     start= auto
sc.exe create cf_buddyrelay binPath= "C:\pmang\crossfire\cf_buddyrelay\cf_buddyrelay.exe" start= auto
sc.exe create ClanServer    binPath= "C:\pmang\crossfire\cf_clansvr\ClanServer.exe"       start= demand
sc.exe create HGW           binPath= "C:\pmang\HGW\HGW.exe"                               start= auto
sc.exe create HGWM          binPath= "C:\pmang\HGWM\HGWM.exe"                             start= auto
sc.exe create BOQBillMicroGamesTx binPath= "C:\pmang\crossfire\cf_billsrv\BOQV3MicroGamesTx.exe" start= auto
```
> Observação importante de sintaxe `sc.exe`: há um **espaço depois do `=`** (`binPath= "..."`, `start= auto`). Confirme o nome real do `.exe` em cada subpasta antes de criar.
> `ClanServer` deve ficar **`start= demand`** (crash residual conhecido — não deixe em auto-restart para não entrar em crash-loop).

### 5.3 Editar os `.ini` de rede dos game servers
Em cada subpasta os `ServerInfo.ini` (e afins) apontam IPs/portas. Substitua o IP antigo pelo IP público desta máquina e confira:
- `cf_gamesrv\ServerInfo.ini` e `cf_cgamesrv\ServerInfo.ini`:
  - `PHBillingIPandPORT = 127.0.0.1:40051` (billing local).
  - `ClanServerIP = <SERVER_PUBLIC_IP>` (no cgamesrv).
  - Seção `#Channel Name` (nomes dos canais/tema CFMaster).
- `cf_clansvr` → `LISTEN_IP = 0.0.0.0`.
- `HGWM\HGWM.ini` → `[HGW] SERVER1 = <IP de bind do HGW>` e `PORT1 = 16667`. **O HGW pode bindar no IP do Radmin VPN, não em 127.0.0.1** — confira o IP de bind no log `C:\Log\HGW\<data>\HGW\*.log` (linha `# Bind IP : ...`) e use exatamente esse no HGWM.

### 5.4 ORDEM DE BOOT (a sequência IMPORTA)
Subir os serviços fora de ordem **emaranha a malha** loginsrv↔game servers↔GameMgmtServer (erro 10054 / `MGMT_EXCEPTION` / "failed to submit player info"). A forma mais segura é **REBOOT da máquina** com uma tarefa agendada que roda o script de boot no startup.

Ordem real validada (de `C:\cfmigra\boot_order.ps1`):
```powershell
# 1. Infra: SQL, gateway de banco, web
foreach($s in 'MSSQLSERVER','gDBGW','cloudflared','cfweb','cfweb80','cfdl'){ Start-Service $s -EA SilentlyContinue }

# 2. Login + Management + Host (esperar entre cada um)
foreach($s in 'cf_loginsrv','GameMgmtServer','cf_hostsrv'){ Restart-Service $s -Force -EA SilentlyContinue; Start-Sleep 5 }

# 3. Clan (best-effort)
Start-Service ClanServer -EA SilentlyContinue; Start-Sleep 4

# 4. Billing — INSTÂNCIA ÚNICA, ANTES dos game servers de loja
Stop-Service BOQBillMicroGamesTx -Force -EA SilentlyContinue
Start-Service BOQBillMicroGamesTx -EA SilentlyContinue

# 5. Game servers (matchmaking + lobby/loja)
foreach($s in 'cf_gamesrv','cf_cgamesrv'){ Restart-Service $s -Force -EA SilentlyContinue; Start-Sleep 6 }

# 6. Auxiliares
foreach($s in 'cf_buddyrelay','cf_alserver','HGW'){ Restart-Service $s -Force -EA SilentlyContinue; Start-Sleep 3 }
Start-Service iphlpsvc -EA SilentlyContinue
```
Regras de ouro:
- **gДBGW ANTES de tudo** (e pronto, porta 6666 LISTEN).
- **billing ANTES de cf_gamesrv/cf_cgamesrv** (senão `GetUserBalance -1` → EC "aguardando").
- **NÃO** subir game servers antes de loginsrv + GameMgmtServer prontos.

### 5.5 Tarefa de boot (sobe tudo no startup)
```powershell
schtasks /Create /TN cfboot /TR "powershell -ExecutionPolicy Bypass -File C:\cfmigra\boot_order.ps1" /SC ONSTART /RU SYSTEM /RL HIGHEST /F
```

### 5.6 Auto-recovery por serviço (opcional)
```powershell
sc.exe failure BOQBillMicroGamesTx reset= 86400 actions= restart/5000/restart/5000/restart/5000
```
> NÃO faça auto-restart do `ClanServer` (crash-loop). E cuidado: um watchdog que mata/reinicia agressivamente o billing pode CRIAR a dupla instância que derruba a porta 40051.

### 5.7 Billing — passos extras obrigatórios (eCoin/cash)
O billing só funciona com 3 coisas presentes (a migração costuma esquecer):
1. **Instalar o MSI:** `msiexec /i "C:\pmang\crossfire\cf_billsrv\MSI\bill.MSI" /quiet /norestart` (instala o produto `BOQN3MG 128.0.0`). Sem ele: "Running Thread = 0" → "Demon AcceptClients Failed".
2. **Registrar a DLL 32-bit:** `regsvr32 /s C:\pmang\crossfire\cf_billsrv\BOQN3MG.dll` (fica em SysWOW64).
3. **Connection string cifrada no registro:** chave
   `HKLM\SYSTEM\CurrentControlSet\Services\BOQBillMicroGamesTx\Parameters\ConnectionString`
   (blob cifrado para o `MICROGAMESBILL_DB`). Em produção foi gerada via `reg export` da máquina onde funcionava e `reg import` na nova (a cifra NÃO é machine-bound). Sem ela: billing aceita conexão mas retorna erro 1012/450 → "Updating EC information" travado.

Saúde do billing: `Get-Process BOQV3MicroGamesTx | % {$_.Threads.Count}` deve ser **> 25** (zumbi < 10). Sem novo "AcceptClients Failed" no log `.NET` em `C:\pmang\crossfire\cf_billsrv\BOQBillMicroGamesTxLog\<data>\`.

### 5.8 Web/launcher (opcional)
Via NSSM, `php -S`:
- `cfweb` → `php -S 0.0.0.0:8081` docroot `C:\xampp\htdocs\cf` (+ `router.php`).
- `cfweb80` → docroot raiz na porta 80 (serve `/in-game/` e `client-banner-lobby.php` que o cliente pede direto no IP).
- `cfdl` → `php -S 0.0.0.0:8090` docroot `dl` (downloads).
- `Cloudflared` (opcional) → `cloudflared tunnel run --protocol http2 --token <CF_TUNNEL_TOKEN>`.

---

## 6) Arquivos do cliente necessários (rez/butes)

O servidor **não** distribui o jogo inteiro, mas dois pontos do cliente/servidor têm que ficar em sincronia para armas funcionarem:

### 6.1 No CLIENTE (distribuído ao jogador)
- **`RB001.REZ`** — contém os *butes* (tabelas binárias): `BF005.LTC` (armas / `WeaponIndex`) e `BF011.LTC` (itens / `ItemID`, `ItemIndex`). É o que casa o ITEM_ID enviado na compra com o catálogo. Limites de índice do cliente: **BF005 jogável = 0–897**; **BF011 esparso (até ~1059)**.
- **`RF001.REZ` … `RF124.REZ`** — modelos/texturas/ícones (`RF124` = modelos de armas custom). Só cliente.
- **`version.ini`** — aponta `IP1/SERVER1` para `<SERVER_PUBLIC_IP>:13006`; `MinimalVersion=1` (não aumentar sem patch novo, senão tranca todos).
- Distribuídos via `C:\pmang\dl\` (`CFMaster_1.0_v26.zip`, `CFMaster_RUNTIME_FIX.zip`, `CFMaster_Launcher.exe`).

### 6.2 No SERVIDOR (ELO QUE FALTA) — `cf_hostsrv\rez\`
O **`cf_hostsrv`** carrega a **PRÓPRIA cópia** de `C:\pmang\crossfire\cf_hostsrv\rez\RB001.REZ` e **valida a arma equipada na partida** contra ela. Conteúdo dessa pasta (inventário real): `RB001.REZ` (~13 MB), `RF001.REZ … RF123.REZ`, `HOSTAISCRIPT.REZ`, `bf000.lta`, `ClientFx.fxd`, `tutorial.ini`, `NationMsz\`, mais DLLs (`CRes.dll`, `SRes.dll`, `audiere.dll`) e fonte.
- Sintoma clássico se faltar: a arma aparece no shop/inventário mas **"pula pra faca" na partida**.
- Regra: ao adicionar arma custom, injetar os MESMOS butes `BF005`+`BF011` (mesmos índices) no `RB001.REZ` do **servidor** também, e `Restart-Service cf_hostsrv`. **Modelos (RF124) NÃO precisam no servidor** (ele não renderiza; a rez do host vai só até RF123).

### 6.3 Categoria de item (NÃO errar)
`CF_ITEM_INFO.ITEM_CATEGORY1/2` define o SLOT/classe da arma. Se inserir arma copiando template de FACA (`K/K`), a arma vira slot de faca → não aparece como primária. Mapa: rifle=`M/R`, sniper=`M/SR`, smg=`M/SM`, metralha=`M/M`, shotgun=`M/S`, pistola=`S/P`, faca=`K/K`, granada=`D/*`.

---

## 7) Checklist pós-boot

1. **Portas em LISTEN** (esperado, conferido no inventário):
   | Porta | Serviço | Bind |
   |---|---|---|
   | 6666 | gДBGW | 0.0.0.0 |
   | 5174 | cf_gamesrv | IP público |
   | 10011 | cf_cgamesrv | (lobby/loja) |
   | 13005 / 13006 | cf_loginsrv | 0.0.0.0 |
   | 14001 | GameMgmtServer / host | 0.0.0.0 |
   | 16666 / 16667 | HGW | IP de bind do HGW |
   | 16668 | HGWM | (anti-cheat manager) |
   | 40051 | billing | loopback OK |
   | 35100 | ClanServer | loopback OK |
   | 35200 | cf_alserver | IP público |
   | 6500 | cf_buddyrelay | IP público |
   | 80 / 8081 / 8090 | web (opcional) | 0.0.0.0 |
   | 1433 | SQL Server | local |
   ```powershell
   Get-NetTCPConnection -State Listen | ? LocalPort -in 6666,5174,10011,13005,13006,14001,16666,16667,16668,40051,35100,35200,6500 | Sort LocalPort -Unique | ft LocalPort,LocalAddress
   ```
2. **Manutenção desligada:** `CF_MIN_CU.CONNECT_CNT = 0` (e `IP` = IP público desta máquina).
   ```sql
   UPDATE CF_PH_GAME.dbo.CF_MIN_CU SET CONNECT_CNT = 0 WHERE CONNECT_CNT < 0;
   ```
3. **Refresh de catálogo** (a loja sobe vazia/"failed to purchase" se o cf_cgamesrv subiu antes do gДBGW — refazer após CADA reboot):
   ```powershell
   Restart-Service gDBGW -Force        # esperar 6666 + 5174 LISTEN (pode precisar 2x)
   Restart-Service cf_gamesrv -Force
   Restart-Service cf_cgamesrv -Force  # recarrega o catálogo da LOJA
   # depois: UPDATE CF_MIN_CU SET CONNECT_CNT=0 WHERE CONNECT_CNT<0
   ```
   Conferir no log NOVO `C:\Log\crossfire\cf_cgamesrv\<data>\` que NÃO há `Failed gDBGW ManagerInit`.
4. **EC/billing:** abrir Item Shop no cliente e dar Refresh; `cash_*.log` sem `GetUserBalance() Faild`. Se "aguardando": restart LIMPO do billing (Stop-Service + Stop-Process, esperar 40051 livre, Start-Service, esperar ~30–60s, depois `cf_gamesrv` e `cf_cgamesrv`).
5. **Sem transação órfã travando `CF_MIN_CU`** (sintoma: tudo "em manutenção", SELECT em CF_MIN_CU dá timeout):
   ```sql
   SELECT session_id, program_name, blocking_session_id, open_transaction_count
   FROM sys.dm_exec_sessions WHERE open_transaction_count > 0;
   -- achar o SPID dono e KILL <spid>
   ```
6. **Cliente loga, vê servidores fora de manutenção, entra no canal** (HGW/HGWM up = anti-cheat valida o hash).
7. **Save de EXP/loadout:** ganhar EXP numa partida e relogar — deve persistir (depende das tabelas de log do `CF_PH_LOG`, ver Apêndice).

---

## 8) O que versionar/guardar vs. o que é grande demais para git

### 8.1 VERSIONAR em git (configs + scripts + SQL) — pequeno, é a "receita"
- **Configs de C:\Windows** (com senhas redigidas): `gDBGW.ini`, `DBGWMGR.ini` (~110 KB, o catálogo de queries), `CFDBLib.ini`.
- **`ServerInfo.ini` / `*.ini`** de cada game server (`cf_gamesrv`, `cf_cgamesrv`, `cf_loginsrv`, etc.) — com IP parametrizado/placeholder.
- **`HGW.ini`, `HGWM.ini`, `verifier.ini`, `whitelist.ini`**.
- **Scripts de operação** (`C:\cfmigra\*.ps1`/`*.bat`): `boot_order.ps1`, `watchdog.ps1`, `harden_fix.ps1`, `recover_login.ps1`, `cf_ec_relink.ps1`, `cf_ec_final.ps1`, `refresh_catalog2.ps1`, `cf_fixlogdb.ps1`, `cf_mklogtables.ps1`.
- **Scripts SQL de schema/procs/fix** (DDL, definições de procs, fixes): criação de logins, `ALTER USER`, criação das tabelas/funções de log do CF_PH_LOG, fix do `SP_GS_CREATE_USER_NEWBIE_DATA`, fix de categorias, etc.
- **Este guia + manual** (`MANUAL_CFMASTER.md`, runbooks).
- **`version.ini`, `client-manifest.json`** do cliente.

> `.gitignore` deve excluir **senhas reais, .reg do billing, tokens** (`cf_tunnel_token.txt`), e os blobs cifrados se você considerá-los sensíveis. Confirme que zero segredos reais entram no repo.

### 8.2 NÃO versionar em git (grande/binário) — backup externo ou Git LFS
| Item | Tamanho | Onde guardar |
|---|---|---|
| **Banco completo** (`.bak`: `game_*.bak`, `guild.bak`, `log.bak`, billing/auth/HGW/PMS) | ~650 MB cada | Backup externo (blob/storage) ou LFS. Manter pelo menos 1 ponto "TUDO OK". |
| **`.mdf/.ldf`** ativos | GB | Nunca no git (ficam abertos pelo SQL). |
| **Binários dos game servers** (`*.exe`, `*.dll`) | dezenas de MB | Backup externo + checksums (MD5). Validar tamanho após copiar (ex.: `ClanServer.exe` = 536576 bytes). |
| **`RB001.REZ`** (cliente + `cf_hostsrv\rez\`) | ~13 MB | LFS ou backup externo. Guardar `RB001_ORIGINAL.REZ` intocado. |
| **`RF001.REZ … RF124.REZ`** | **vários GB** (RF005 ~274 MB, RF017 ~616 MB…) | Backup externo / pacote do cliente. JAMAIS no git. |
| **Pacotes do cliente** (`CFMaster_1.0_v26.zip`, `CFNovo_Cliente.rar`) | GB | Hospedar em `C:\pmang\dl\` / storage de download. |
| **`bill.MSI`, `BOQN3MG.dll`, runtimes (VC++/.NET), NSSM** | MB | Backup externo (componentes de instalação). |
| **`boq_params.reg`** (connection string cifrada do billing) | KB | **Cofre/secret store** — NÃO no git (é segredo). |
| **Crash dumps / logs** (`C:\Log\...`, `*.dmp`) | GB | Não versionar; rotacionar/limpar. |

> **Estratégia recomendada:** git só com a "receita" (configs redigidas + scripts + SQL) — clonável e pequeno. Um **pacote de bootstrap** separado (storage/LFS) com binários + `.rez` + `.bak` + MSIs + runtimes. Replicar = clonar o repo + baixar o pacote + restaurar o banco + rodar os scripts deste guia.

---

## 9) Apêndice — gotchas que custaram caro

- **Os 3 `.ini` ficam em `C:\Windows`** (gДBGW.ini, DBGWMGR.ini, CFDBLib.ini), não em C:\pmang. Sem eles: `gDBGW ERR INVALIDFILE`.
- **Login `hgw` é obrigatório** (gДBGW usa `cf` para DB1–4 e `hgw` para o HGW DB5).
- **SQL precisa de TCP/IP em 127.0.0.1:1433** habilitado.
- **`CF_MIN_CU`:** trocar IP + `CONNECT_CNT=0`; leitura vazia/timeout normalmente é **lock de transação órfã**, não tabela vazia — checar `sys.dm_tran_locks`/`KILL`.
- **Defender corrompe binários antigos** → exclusões ANTES de copiar; validar tamanhos.
- **NSSM só em console apps** (gДBGW, web). Game servers = `sc create` nativo.
- **PDH (contadores de performance)** podem precisar de `lodctr /R` (64 e 32-bit) num server fresco.
- **CF_PH_LOG precisa dos objetos de log** ou o save de fim de partida faz ROLLBACK (EXP/loadout não salvam): funções `ConvDate`/`ConvVar` + tabelas `CF_CONNECT_LOG`, `CF_LEVELUP_LOG`, `CF_GAME_LOG`, `CF_PLAY_LOG`. Copiar definições do `CF_PH_GAME`/backup; estrutura das tabelas está nas queries Q18/Q19/Q21/Q60 do `DBGWMGR.ini`.
- **Onboarding (nickname/soldado conta nova):** `SP_GS_CREATE_USER_NEWBIE_DATA` precisa inserir TODAS as 15 colunas `LEV_*` (int NOT NULL) + `NB_KIND='N'` em `CF_USER_NEWBIEMISSION_ACHIEVE`; se ficar stub, o onboarding aborta.
- **Limite de itens do binário:** `cf_gamesrv`/`cf_cgamesrv` crasham com catálogo grande (>~2900 itens). Inserir em lotes e validar que as portas 5174/10011 bindam entre cada lote. Estável testado ~2300–2500.
- **gДBGW cacheia a query de carga de item** — após alterar `CF_ITEM_INFO`, reiniciar gДBGW→loginsrv/GMS→cf_gamesrv→cf_cgamesrv (refresh de catálogo).
- **Cliente conecta no IP PÚBLICO** (não loopback) para vários serviços (loginsrv→gДBGW, EC via HTTP porta 80 no IP). Se for fazer hardening de firewall, **excluir o próprio IP** das regras de BLOCK e manter a porta 80 aberta.
- **ClanServer** tem crash residual conhecido (0xC000000D em tarefa periódica) — deixar `start= demand`, sem auto-restart; o jogo funciona sem ele (só a UI de clã fica indisponível).

---

## 10) Credenciais (preencher)

> **Não** salvar este arquivo com senhas reais em git. Preencher numa cópia local protegida / cofre.

| Item | Valor |
|---|---|
| IP público do servidor (`<SERVER_PUBLIC_IP>`) | `______________________` |
| Hostname | `______________________` |
| Usuário Windows (admin) | `______________________` |
| Senha Windows (admin) | `______________________` |
| Senha SSH (se OpenSSH) | `______________________` |
| Login SQL `cf` — senha (`<DB_CF_PASSWORD>`) | `______________________` |
| Login SQL `hgw` — senha (`<DB_HGW_PASSWORD>`) | `______________________` |
| `sa` do SQL (se usado) | `______________________` |
| Connection string cifrada do billing (`boq_params.reg`) | (cofre/secret store) |
| Token do túnel Cloudflare (`<CF_TUNNEL_TOKEN>`) | (cofre/secret store) |
| Conta Cloudflare (DNS/tunnel) | `______________________` |
| Conta GM in-game (nick / USN / authority 'A') | `______________________` |

---

### Referências internas (origem deste guia)
- Memória: `cfmaster-runbook-deploy.md`, `cfmaster-loja-itens-compra.md`, `cfmaster-clan-ec-vps-fixes.md`, `cfmaster-arma-custom.md`, `cfmaster-onboarding-loja-fixes.md`, `cfmaster-primaria-categoria-fix.md`, `cfref-servidor-local.md`, `MEMORY.md`.
- Runbook: `C:\Users\henrique\RUNBOOK_CFMASTER_FIXES_20260612.md` e `C:\pmang\RUNBOOK_CFMASTER_FIXES_20260612.md`.
- Manual: `C:\cfmaster-docs\MANUAL_CFMASTER.md` (na VPS).
- Inventário da VPS de produção (`178.83.141.35`) feito em modo somente-leitura para validar estrutura, serviços, `.ini`, bancos e ordem de boot.
