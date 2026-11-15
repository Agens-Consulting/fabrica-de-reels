"""Agenda posts no Zernio pela API REST (chave ZERNIO_API_KEY do .env do projeto).

Uso:
  .venv/bin/python ferramentas/zernio_posts.py contas
  .venv/bin/python ferramentas/zernio_posts.py reel --conta <accountId> --video corte.mp4 --capa capa.png \
      --legenda legenda.txt --quando "2026-10-06T19:00:00" [--fuso Europe/Lisbon] \
      [--teste MANUAL|SS_PERFORMANCE]   # publica como trial reel (só não-seguidores)
  .venv/bin/python ferramentas/zernio_posts.py posts [--estado scheduled]
  .venv/bin/python ferramentas/zernio_posts.py imagem --conta <id> --imagem x.png --legenda l.txt --quando ...
  .venv/bin/python ferramentas/zernio_posts.py story --conta <id> --imagem 01.png --quando ...

O MCP só cria posts simples; isto faz o que ele não faz: upload de ficheiros locais,
data e hora exatas com fuso, e capa própria do Reel (instagramThumbnail).
"""
import argparse, json, mimetypes, pathlib, sys, urllib.request, uuid

BASE = "https://zernio.com/api/v1"


CHAVE_ENV = None  # nome da chave no .env; None = ZERNIO_API_KEY

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import config as _cfg  # noqa: E402


def chave():
    return "Bearer " + _cfg.get(CHAVE_ENV or "ZERNIO_API_KEY")


def api(metodo, caminho, corpo=None, extra=None):
    h = {"Authorization": chave(), "Content-Type": "application/json", **(extra or {})}
    r = urllib.request.Request(BASE + caminho, method=metodo, headers=h,
                               data=json.dumps(corpo).encode() if corpo is not None else None)
    try:
        with urllib.request.urlopen(r, timeout=120) as x:
            return json.load(x)
    except urllib.error.HTTPError as e:
        sys.exit(f"{metodo} {caminho} → {e.code}: {e.read().decode()[:500]}")


def carregar(ficheiro):
    f = pathlib.Path(ficheiro)
    tipo = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
    p = api("POST", "/media/presign", {"filename": f.name, "contentType": tipo})
    r = urllib.request.Request(p["uploadUrl"], method="PUT", data=f.read_bytes(), headers={"Content-Type": tipo})
    urllib.request.urlopen(r, timeout=600).read()
    return p["publicUrl"]


def story(conta, imagem, quando, fuso="Europe/Lisbon"):
    """Story de Instagram (imagem 1080x1920): sem legenda, sem stickers nem links (a API não os põe)."""
    url = carregar(imagem)
    corpo = {"mediaItems": [{"type": "image", "url": url}],
             "platforms": [{"platform": "instagram", "accountId": conta, "platformSpecificData": {"contentType": "story"}}],
             "scheduledFor": quando, "timezone": fuso}
    res = api("POST", "/posts", corpo, {"Idempotency-Key": str(uuid.uuid5(uuid.NAMESPACE_URL, "story:" + str(imagem) + quando))})
    post = res.get("post", res)
    return {"id": post.get("_id"), "status": post.get("status"), "scheduledFor": post.get("scheduledFor")}


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--chave", help="variável do .env com a chave Zernio (ex. ZERNIO_API_KEY)")
    s = a.add_subparsers(dest="cmd", required=True)
    s.add_parser("contas")
    po = s.add_parser("posts"); po.add_argument("--estado", default="")
    r = s.add_parser("reel")
    r.add_argument("--conta", required=True); r.add_argument("--video", required=True)
    r.add_argument("--capa"); r.add_argument("--legenda", required=True)
    r.add_argument("--quando", required=True); r.add_argument("--fuso", default="Europe/Lisbon")
    r.add_argument("--teste", choices=["MANUAL", "SS_PERFORMANCE"],
                   help="trial reel: MANUAL (promoves na app) ou SS_PERFORMANCE (o IG promove se correr bem)")
    im = s.add_parser("imagem")
    im.add_argument("--conta", required=True); im.add_argument("--imagem", required=True)
    im.add_argument("--legenda", required=True); im.add_argument("--quando", required=True)
    im.add_argument("--fuso", default="Europe/Lisbon")
    st = s.add_parser("story")
    st.add_argument("--conta", required=True); st.add_argument("--imagem", required=True)
    st.add_argument("--quando", required=True); st.add_argument("--fuso", default="Europe/Lisbon")
    ca = s.add_parser("carrossel", help="até 10 imagens e/ou vídeos, pela ordem dada")
    ca.add_argument("--conta", required=True); ca.add_argument("--ficheiros", nargs="+", required=True)
    ca.add_argument("--legenda", required=True); ca.add_argument("--quando", required=True)
    ca.add_argument("--fuso", default="Europe/Lisbon"); ca.add_argument("--ensaio", action="store_true")
    a = a.parse_args()
    global CHAVE_ENV
    CHAVE_ENV = a.chave

    if a.cmd == "contas":
        for c in api("GET", "/accounts").get("accounts", []):
            print(c.get("platform"), c.get("username"), c.get("_id"))
    elif a.cmd == "posts":
        q = f"?status={a.estado}" if a.estado else ""
        for p in api("GET", "/posts" + q).get("posts", []):
            print(p.get("_id"), p.get("status"), p.get("scheduledFor"), (p.get("content") or "")[:60].replace("\n", " "))
    elif a.cmd == "story":
        print(json.dumps(story(a.conta, a.imagem, a.quando, a.fuso), ensure_ascii=False))
    elif a.cmd == "carrossel":
        if not 2 <= len(a.ficheiros) <= 10:
            sys.exit("Um carrossel do Instagram tem entre 2 e 10 itens.")
        legenda = pathlib.Path(a.legenda).read_text().strip()
        if a.ensaio:
            print(json.dumps({"itens": a.ficheiros, "quando": a.quando, "legenda": legenda[:120]}, ensure_ascii=False, indent=1)); return
        itens = [{"type": "video" if (mimetypes.guess_type(f)[0] or "").startswith("video") else "image", "url": carregar(f)} for f in a.ficheiros]
        corpo = {"content": legenda, "mediaItems": itens, "platforms": [{"platform": "instagram", "accountId": a.conta}],
                 "scheduledFor": a.quando, "timezone": a.fuso}
        res = api("POST", "/posts", corpo, {"Idempotency-Key": str(uuid.uuid5(uuid.NAMESPACE_URL, "|".join(a.ficheiros) + a.quando))})
        post = res.get("post", res)
        print(json.dumps({"id": post.get("_id"), "status": post.get("status"), "scheduledFor": post.get("scheduledFor")}, ensure_ascii=False))
    elif a.cmd == "imagem":
        url = carregar(a.imagem)
        corpo = {"content": pathlib.Path(a.legenda).read_text().strip(), "mediaItems": [{"type": "image", "url": url}],
                 "platforms": [{"platform": "instagram", "accountId": a.conta}], "scheduledFor": a.quando, "timezone": a.fuso}
        res = api("POST", "/posts", corpo, {"Idempotency-Key": str(uuid.uuid5(uuid.NAMESPACE_URL, a.imagem + a.quando))})
        post = res.get("post", res)
        print(json.dumps({"id": post.get("_id"), "status": post.get("status"), "scheduledFor": post.get("scheduledFor")}, ensure_ascii=False))
    else:
        video = carregar(a.video)
        psd = {}
        if a.capa:
            psd["instagramThumbnail"] = carregar(a.capa)
        if a.teste:
            psd["trialParams"] = {"graduationStrategy": a.teste}
        corpo = {
            "content": pathlib.Path(a.legenda).read_text().strip(),
            "mediaItems": [{"type": "video", "url": video}],
            "platforms": [{"platform": "instagram", "accountId": a.conta, "platformSpecificData": psd}],
            "scheduledFor": a.quando, "timezone": a.fuso,
        }
        res = api("POST", "/posts", corpo, {"Idempotency-Key": str(uuid.uuid5(uuid.NAMESPACE_URL, a.video + a.quando))})
        post = res.get("post", res)
        print(json.dumps({"id": post.get("_id"), "status": post.get("status"), "scheduledFor": post.get("scheduledFor")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
