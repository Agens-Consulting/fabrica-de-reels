"""Automações de comentário → DM no Instagram, pela API da Zernio, na conta Zernio configurada no .env do projeto.

O motor é o da Zernio (POST /v1/comment-automations): os formulários do n8n fazem o mesmo,
isto é a via direta.

Chave: ZERNIO_API_KEY no .env da raiz do projeto (a conta de Instagram descobre-se pelo @).

Uso:
    .venv/bin/python ferramentas/zernio.py contas
    .venv/bin/python ferramentas/zernio.py listar @a.tua.conta
    .venv/bin/python ferramentas/zernio.py criar @a.tua.conta --palavra GUIA --dm "Aqui tens o guia 👇" \
        --botao-texto "Abrir o guia" --botao-link https://... [--resposta-publica "Enviado por mensagem 📩"] \
        [--post-id <id Zernio de um post agendado> | --platform-post-id <id Instagram>] [--nome "..."] \
        (a resposta pública vai sempre: RESPOSTAS abaixo, a rodar, 40 s depois da DM; --resposta-publica troca a principal)
        [--ref <tarefa ClickUp ou pasta>] [--ensaio]
    .venv/bin/python ferramentas/zernio.py apagar @a.tua.conta <automation_id>
    .venv/bin/python ferramentas/zernio.py responder @a.tua.conta      # liga a resposta pública nas automações que não a têm

Sem --post-id nem --platform-post-id a automação vale para a conta inteira: dispara em qualquer
publicação onde comentem a palavra, e também em DM. Por isso a palavra tem de ser única na conta;
o script recusa repetidas. Com --post-id (post agendado pela Zernio) a automação fica pendente e
arma-se quando o post sair.

(Reconstruído a 04/10/2026 a partir do .pyc, depois de o original ter sido sobrescrito por engano.
Confirmar o comportamento com --ensaio antes do primeiro uso.)
"""
import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.request
from datetime import date

BASE = "https://zernio.com/api/v1"
AQUI = pathlib.Path(__file__).resolve().parent.parent
REGISTO = AQUI / "ctas" / "automacoes-instagram.jsonc"
CHAVES = ("ZERNIO_API_KEY",)   # a conta Zernio desta pessoa (.env do projeto)
# Resposta pública a quem pede o recurso: sempre (comentários sem resposta tiram engagement).
# Seis textos que rodam ao acaso, para o Instagram não ver a mesma frase repetida; publicada uns segundos depois da DM.
RESPOSTA = "Já te enviei por mensagem 📩"
RESPOSTAS = [
    "Está na tua caixa de mensagens. Depois diz-me se ajudou.",
    "Enviado 📩 Se não aparecer, espreita os pedidos de mensagem.",
    "Já seguiu por mensagem. Conta-me como correu.",
    "Mandei-te agora por mensagem ✨",
    "Feito: está nas tuas mensagens 📩",
]
RESPOSTA_CAMPOS = {"commentReply": RESPOSTA, "commentReplyVariations": RESPOSTAS,
                   "publicReplyPolicy": "always", "commentReplyDelaySeconds": 40}


def env():
    vals = {}
    f = AQUI / ".env"
    if f.exists():
        for linha in f.read_text().splitlines():
            linha = linha.strip()
            if linha and not linha.startswith("#") and "=" in linha:
                k, v = linha.split("=", 1)
                vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals


def pedido(chave, metodo, caminho, corpo=None):
    r = urllib.request.Request(BASE + caminho, method=metodo,
                               data=json.dumps(corpo).encode() if corpo is not None else None,
                               headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=60) as x:
            dados = x.read()
            return json.loads(dados) if dados else {}
    except urllib.error.HTTPError as e:
        detalhes = e.read().decode(errors="replace")[:600]
        sys.exit(f"Zernio {metodo} {caminho} → HTTP {e.code}: {detalhes}")


def contas():
    """Todas as contas de Instagram ligadas, em todas as chaves preenchidas."""
    e, todas = env(), []
    for nome in CHAVES:
        chave = e.get(nome)
        if not chave:
            continue
        for a in pedido(chave, "GET", "/accounts").get("accounts", []):
            if a.get("platform") != "instagram":
                continue
            perfil = a.get("profileId")
            if isinstance(perfil, dict):
                perfil = perfil.get("_id")
            todas.append({"chave": chave, "nomeChave": nome, "username": a.get("username"),
                          "accountId": a.get("_id"), "profileId": perfil,
                          "ativa": a.get("isActive", True), "religar": a.get("needsReconnection", False)})
    return todas


def conta(arroba):
    alvo = arroba.lstrip("@").lower()
    todas = contas()
    for c in todas:
        if (c["username"] or "").lower() == alvo:
            if c["religar"]:
                sys.exit(f"@{c['username']} precisa de ser religada na Zernio antes de aceitar automações.")
            return c
    vazias = [n for n in CHAVES if not env().get(n)]
    sys.exit(f"@{alvo} não está em nenhuma chave preenchida. Ligadas: "
             + ", ".join("@" + (c["username"] or "?") for c in todas)
             + (f". Chaves por preencher no .env: {', '.join(vazias)}" if vazias else ""))


def automacoes(c):
    pid = c["profileId"]
    q = f"?profileId={pid}" if pid else ""
    return [a for a in pedido(c["chave"], "GET", "/comment-automations" + q).get("automations", [])
            if a.get("accountId") in (None, c["accountId"])]


def registar(entrada):
    REGISTO.parent.mkdir(parents=True, exist_ok=True)
    linhas = REGISTO.read_text().splitlines() if REGISTO.exists() else ["// Automações criadas por ferramentas/zernio.py (uma por linha)"]
    linhas.append(json.dumps(entrada, ensure_ascii=False))
    REGISTO.write_text("\n".join(linhas) + "\n")


# Palavras que aparecem em comentários normais: uma automação de conta inteira com elas dispara sem parar.
COMUNS = {
    "IA", "AI", "INTELIGENCIA", "INTELIGÊNCIA", "ARTIFICIAL", "SIM", "NAO", "NÃO", "QUERO", "EU", "TOP", "BOM", "BOA",
    "OBRIGADO", "OBRIGADA", "LINK", "INFO", "MAIS", "FUNDO", "PROCESSO", "PROCESSOS", "AGENDA", "LISTA", "EMPRESA",
    "NEGOCIO", "NEGÓCIO", "DADOS", "TAREFA", "TAREFAS", "EQUIPA", "CLIENTE", "CLIENTES", "TEMPO", "DINHEIRO", "AJUDA",
    "GUIA", "VIDEO", "VÍDEO", "POST", "AGENTE", "AGENTES", "CHATGPT", "CLAUDE", "GEMINI", "AUTOMAÇÃO", "AUTOMACAO",
    "DIAGNOSTICO", "DIAGNÓSTICO", "PROMPT", "PROMPTS", "MODELO", "PLANO", "CUSTO", "PREÇO", "PRECO", "GRATIS", "GRÁTIS",
}


def mapa_completo():
    """Todas as automações de todas as contas: [(conta, id, palavras, âmbito, nome)]."""
    out = []
    for c in contas():
        for au in automacoes(c):
            onde = au.get("postId") or au.get("platformPostId") or "conta inteira"
            out.append(("@" + c["username"], au.get("_id") or au.get("id"), [k.upper() for k in au.get("keywords", [])], onde, au.get("name")))
    return out


def validar_palavras(palavras, c, mesmo_recurso=False):
    """Uma palavra = um recurso, em toda a casa. Na mesma conta nunca se repete; noutra conta só com
    --mesmo-recurso (ex.: ROADMAP leva sempre ao AI Readiness & ROI)."""
    erros = []
    for p in palavras:
        if p in COMUNS or len(p) < 4:
            erros.append(f"{p}: palavra comum ou curta demais (dispara em comentários normais). Usa uma palavra rara, ex. ICEBERG, ROADMAP.")
    for conta_, id_, kws, onde, nome in mapa_completo():
        for p in palavras:
            if p in kws and (conta_ == "@" + c["username"] or not mesmo_recurso):
                erros.append(f"{p}: já usada em {conta_} ({onde}, {nome}). Uma palavra = um recurso; noutra conta só com --mesmo-recurso.")
    if erros:
        sys.exit("Palavra recusada:\n  " + "\n  ".join(erros))


def criar(a):
    c = conta(a.conta)
    palavras = [p.strip().upper() for p in a.palavra.split(",") if p.strip()]
    if not palavras:
        sys.exit("Indica pelo menos uma palavra.")
    if not a.forcar:
        validar_palavras(palavras, c, a.mesmo_recurso)
    por_post = bool(a.post_id or a.platform_post_id)
    if not por_post:
        usadas = {}
        for au in automacoes(c):
            if au.get("postId") or au.get("platformPostId"):
                continue
            for k in au.get("keywords", []):
                usadas[k.upper()] = au.get("name") or (au.get("_id") or au.get("id"))
        repetidas = [p for p in palavras if p in usadas]
        if repetidas:
            sys.exit(f"A palavra {', '.join(repetidas)} já está ativa na conta inteira de @{c['username']} "
                     f"(automação {usadas[repetidas[0]]}). Escolhe outra palavra.")
    corpo = {
        "accountId": c["accountId"],
        "name": a.nome or f"{palavras[0]} · {date.today():%d/%m}",
        "trigger": "comment",
        "keywords": palavras,
        "matchMode": "word",
        "typoTolerance": True,
        "dmMessage": a.dm,
        "alsoMatchInDms": not por_post,
    }
    if c["profileId"]:
        corpo["profileId"] = c["profileId"]
    if a.post_id:
        corpo["postId"] = a.post_id
    if a.platform_post_id:
        corpo["platformPostId"] = a.platform_post_id
    corpo.update(RESPOSTA_CAMPOS)
    if a.resposta_publica:
        corpo["commentReply"] = a.resposta_publica
    if a.botao_link:
        link = a.botao_link if a.botao_link.startswith("http") else "https://" + a.botao_link
        corpo["buttons"] = [{"type": "url", "title": a.botao_texto or "Abrir", "url": link}]
        if len(a.dm) > 640:
            sys.exit(f"Com botão a DM tem no máximo 640 caracteres (tem {len(a.dm)}).")
    if a.ensaio:
        print(json.dumps(corpo, ensure_ascii=False, indent=2))
        return
    res = pedido(c["chave"], "POST", "/comment-automations", corpo)
    au = res.get("automation", res)
    registar({"data": date.today().isoformat(), "conta": "@" + c["username"], "id": (au.get("_id") or au.get("id")),
              "palavras": palavras, "ambito": "post" if por_post else "conta inteira (comentário em qualquer post + DM)",
              "post_id": a.post_id, "platform_post_id": a.platform_post_id, "botao": a.botao_link, "ref": a.ref})
    print(json.dumps({"id": (au.get("_id") or au.get("id")), "palavras": palavras, "conta": "@" + c["username"]}, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("contas")
    li = s.add_parser("listar"); li.add_argument("conta")
    cr = s.add_parser("criar"); cr.add_argument("conta")
    cr.add_argument("--palavra", required=True, help="uma ou várias, separadas por vírgula")
    cr.add_argument("--dm", required=True)
    cr.add_argument("--botao-texto"); cr.add_argument("--botao-link")
    cr.add_argument("--resposta-publica"); cr.add_argument("--nome")
    cr.add_argument("--post-id"); cr.add_argument("--platform-post-id")
    cr.add_argument("--ref", help="tarefa ClickUp ou pasta, para o registo")
    cr.add_argument("--ensaio", action="store_true", help="mostra o pedido sem criar")
    cr.add_argument("--mesmo-recurso", action="store_true", help="a palavra já existe noutra conta e entrega o mesmo recurso")
    cr.add_argument("--forcar", action="store_true", help="salta a validação da palavra (só com OK do dono da conta)")
    s.add_parser("mapa")
    ap = s.add_parser("apagar"); ap.add_argument("conta"); ap.add_argument("id")
    rp = s.add_parser("responder", help="põe a resposta pública em todas as automações da conta que não a têm")
    rp.add_argument("conta"); rp.add_argument("--todas", action="store_true", help="também as que já têm resposta")
    a = p.parse_args()

    if a.cmd == "contas":
        for c in contas():
            print(f"@{c['username']}\t{c['accountId']}\t{c['nomeChave']}\t{'religar!' if c['religar'] else 'ok'}")
    elif a.cmd == "listar":
        c = conta(a.conta)
        for au in automacoes(c):
            onde = au.get("postId") or au.get("platformPostId") or "conta inteira"
            print((au.get("_id") or au.get("id")), ",".join(au.get("keywords", [])), onde, au.get("name"))
    elif a.cmd == "criar":
        criar(a)
    elif a.cmd == "responder":
        c = conta(a.conta)
        for au in automacoes(c):
            if au.get("commentReplyVariations") and au.get("publicReplyPolicy") == "always" and not a.todas:
                continue
            campos = dict(RESPOSTA_CAMPOS)
            if au.get("commentReply") and not a.todas:
                campos.pop("commentReply")
            pedido(c["chave"], "PATCH", f"/comment-automations/{au.get('_id') or au.get('id')}", campos)
            print("resposta pública ligada:", ",".join(au.get("keywords", [])))
    elif a.cmd == "mapa":
        linhas = ["# Mapa das automações comentário → DM", "", "Gerado por `ferramentas/zernio.py mapa`. Regras: uma palavra = um recurso na conta (pode repetir-se noutra conta só se entregar o mesmo recurso); nunca palavras comuns (as que aparecem em comentários normais).", "",
                  "| Conta | Palavra(s) | Âmbito | Nome | Risco | Id |", "|---|---|---|---|---|---|"]
        for conta_, id_, kws, onde, nome in sorted(mapa_completo()):
            risco = "⚠️ comum" if any(k in COMUNS or len(k) < 4 for k in kws) else ""
            linhas.append(f"| {conta_} | {', '.join(kws)} | {onde} | {nome} | {risco} | `{id_}` |")
        (AQUI / "ctas" / "automacoes-mapa.md").write_text("\n".join(linhas) + "\n")
        print("\n".join(linhas))
    else:
        c = conta(a.conta)
        pedido(c["chave"], "DELETE", f"/comment-automations/{a.id}")
        print("apagada", a.id)


if __name__ == "__main__":
    main()
