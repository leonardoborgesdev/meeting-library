#!/usr/bin/env python3
# build_walkthrough.py <call_id>
# Gera no formato do skill video-walkthrough do Morfeu333:
#   library/walkthroughs/<id>/frames/frame_NNNNs.jpg  (~55 frames)
#   library/walkthroughs/<id>/WALKTHROUGH.md          (índice + transcript frame-synced)
# Segmentação fiel ao skill: usa AAI words (pausa>600ms OU fim de frase) quando há
# library/transcripts/<id>.json; senão cai pro .speakers.txt (utterances).
import sys, os, json, math, subprocess, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
MES = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
PAUSE = 600  # ms

def fmt(s): s=int(s); return f"{s//60}:{s%60:02d}"

def segments_from_words(words):
    segs=[]; cur=[words[0]]
    for w in words[1:]:
        gap = w.get('start',0) - cur[-1].get('end',0)
        sentence_end = cur[-1].get('text','').endswith(('.', '!', '?'))
        if gap > PAUSE or sentence_end:
            segs.append(cur); cur=[w]
        else:
            cur.append(w)
    if cur: segs.append(cur)
    return [(seg[0].get('start',0)/1000.0, ' '.join(w.get('text','') for w in seg)) for seg in segs]

def segments_from_speakers(path):
    out=[]
    for line in open(path):
        m=re.match(r"\[(\d+)s\]\s*Speaker\s*([A-Z]):\s*(.*)", line.strip())
        if m: out.append((float(m.group(1)), f"({m.group(2)}) {m.group(3)}"))
    return out

def main(cid):
    data=json.load(open("data/calls.json"))
    c=next((x for x in data["calls"] if x["id"]==cid), None)
    if not c: print("id não encontrado"); return 1
    video=c.get("video")
    if not video or not os.path.exists(video): print("sem vídeo local"); return 1

    # segmentos: words (fiel) > speakers (fallback)
    jp=f"library/transcripts/{cid}.json"; sp=(c.get("transcript") or "").replace(".txt",".speakers.txt")
    segs=[]
    if os.path.exists(jp):
        try:
            w=json.load(open(jp)).get("words") or []
            if w: segs=segments_from_words(w)
        except Exception: pass
    if not segs and os.path.exists(sp): segs=segments_from_speakers(sp)
    if not segs: print("sem transcrição"); return 1

    outdir=f"library/walkthroughs/{cid}"; frames=f"{outdir}/frames"; os.makedirs(frames, exist_ok=True)
    dur=float(subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration","-of","default=nw=1:nk=1",video],
        capture_output=True, text=True).stdout.strip() or 0)
    interval=max(1, math.ceil(dur/55))

    for f in os.listdir(frames):
        if f.endswith(".jpg"): os.remove(os.path.join(frames,f))
    subprocess.run(["ffmpeg","-nostdin","-loglevel","error","-y","-i",video,
        "-vf",f"fps=1/{interval},scale=640:-1","-q:v","3",f"{frames}/f_%04d.jpg"])
    seq=sorted(f for f in os.listdir(frames) if f.startswith("f_")); frame_ts=[]
    for i,f in enumerate(seq):
        ts=i*interval; os.rename(os.path.join(frames,f), os.path.join(frames,f"frame_{ts:04d}s.jpg")); frame_ts.append(ts)
    if not frame_ts: frame_ts=[0]
    def nearest(sec): return min(frame_ts, key=lambda t: abs(t-sec))

    sections={}
    for sec,txt in segs: sections.setdefault(nearest(sec), []).append((sec,txt))

    dd=c["date"].split("-"); date_h=f"{int(dd[2])} {MES[int(dd[1])-1]} {dd[0]}"
    dur_h=f"{int(dur//60)} min {int(dur%60)}s"
    quem=" · ".join(c.get("participantes",[]) or ["Lucas F. N. Alves"])
    topicos=" · ".join(c.get("assunto",[]) or [])
    vrel="../../videos/"+os.path.basename(video)

    L=[f"# 🏗️ Walkthrough — {c['title']}\n",
       f"> **Gravação:** {date_h} · {dur_h}  ",
       f"> **Apresentado por:** {quem}  ",
       f"> **Tópicos:** {topicos}\n",
       f'<video src="{vrel}" controls width="100%"></video>\n', "---\n", "## 📋 Índice\n"]
    for ts in sorted(sections):
        first=sections[ts][0][1][:60]
        L.append(f"- [{fmt(ts)}](#{fmt(ts).replace(':','')}) — {first}…")
    L.append("\n---\n")
    for ts in sorted(sections):
        L.append(f"### ⏱️ {fmt(ts)}")
        L.append(f"![Frame {fmt(ts)}](frames/frame_{ts:04d}s.jpg)\n")
        for sec,txt in sections[ts]:
            L.append(f"**`{fmt(sec)}`** {txt}")
        L.append("\n---\n")
    L.append("*Gerado automaticamente com AssemblyAI universal-2 + ffmpeg*")
    open(f"{outdir}/WALKTHROUGH.md","w").write("\n".join(L))

    c["walkthrough"]=f"{outdir}/WALKTHROUGH.md"; c["frames_dir"]=frames
    json.dump(data, open("data/calls.json","w"), ensure_ascii=False, indent=2)
    print(f"✓ walkthrough {cid}: {len(frame_ts)} frames, {len(sections)} seções, {len(segs)} segmentos")
    return 0

if __name__=="__main__":
    sys.exit(main(sys.argv[1]))
