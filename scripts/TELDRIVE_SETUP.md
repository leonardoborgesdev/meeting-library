# Teldrive (Brazika Drive) — setup & migração dos vídeos de apresentação

## Status (16/06/2026)

- **Upload viável:** SIM. bots=2 e channelId=4401134225 já configurados no app `brazika-drive`.
- **Migração feita:** os 3 mp4 de apresentação já estão no drive em `/meeting-library` e
  `data/presentations.json` LOCAL já tem `teldrive` + `video` apontando pro proxy.
- **Bloqueio restante:** o proxy de stream no `scripts/server.py` usa o header de auth ERRADO
  (Bearer). O Teldrive só aceita Cookie. Precisa de 1 linha de fix (abaixo) pra funcionar em prod.

## Config do Teldrive (confirmado)

```
GET https://drive.brazika.online/api/users/config   (Cookie: access_token=<jwt>)
  -> channelId: 4401134225
  -> bots: 2
```

Token (JWT): vem de `scripts/backup_media_teldrive.py::mint_token()`, que lê a sessão mais
recente no Postgres (`fly ssh console -a brazika-drive-pg`) + `JWT_SECRET` em
`~/Desktop/brazika-drive/.secrets.local`. Em prod (Fly), `mint_token()` usa o secret `TD_TOKEN`
(sem fly ssh).

## URL de streaming CORRETA

```
GET https://drive.brazika.online/api/files/<fileId>/stream
Header: Cookie: access_token=<jwt>     <-- ÚNICO modo que autentica
```

Testes feitos contra um arquivo real:

| Auth                                   | Resultado                          |
|----------------------------------------|------------------------------------|
| `Cookie: access_token=<jwt>`           | **206 video/mp4**  ✅              |
| `Authorization: Bearer <jwt>`          | 401 "missing token or auth hash" ❌ |
| `?access_token=<jwt>` (query)          | 401 ❌                             |
| `/api/files/<id>/stream/<name>` (path) | 404 ❌                             |

Range requests funcionam (206). O path `/stream` está certo; **o que muda é o header**.

## FIX NECESSÁRIO no server.py (não editado por mim — outro agente é dono)

Em `scripts/server.py`, no handler de `/api/presentations/video`, trocar o header de auth
do request ao Teldrive de Bearer para Cookie:

```python
# ANTES (linha ~379) — NÃO autentica, Teldrive devolve 401:
req = _u.Request(url, headers={"Authorization": f"Bearer {tok}"})

# DEPOIS — autentica (206):
req = _u.Request(url, headers={"Cookie": f"access_token={tok}"})
```

Sem esse fix, com o vídeo local ausente (caso de prod sem o mp4 no volume), o proxy cai em
502 "teldrive: HTTP Error 401". Com o mp4 presente no volume, o server serve do disco e o
Teldrive nem é chamado (fallback), então o bug fica latente até o arquivo sumir.

## Secret em prod

Pra o proxy funcionar no Fly (`meeting-library`), o secret `TD_TOKEN` precisa estar setado com
um JWT válido (validade ~30 dias no mint atual). Conferir/renovar:

```bash
# gerar token novo (local, lê Postgres + JWT_SECRET):
TOK=$(python3 -c "import sys;sys.path.insert(0,'scripts');import backup_media_teldrive as td;print(td.mint_token())")
fly secrets set TD_TOKEN="$TOK" -a meeting-library
```

## fileIds migrados (/meeting-library)

| pid                              | mp4                                   | fileId                               |
|----------------------------------|---------------------------------------|--------------------------------------|
| pres_2026-06-16_meeting-library  | pres_2026-06-16_meeting-library.mp4   | 019ed31a-4dbd-797c-b220-b46b153378b4 |
| pres_2026-06-15_brazika-admin    | pres_2026-06-15_brazika-admin.mp4     | 019ed31a-565e-75ef-b64f-5f4a8f2277fc |
| pres_2026-06-14_confere          | pres_2026-06-14_confere.mp4           | 019ed31a-6518-791a-9b14-2ea7718e9860 |

Re-rodar a migração (idempotente, reusa fileIds do mapa): `python3 scripts/migrate_pres_teldrive.py`
