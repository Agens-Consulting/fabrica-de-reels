# Fábrica de Reels — plugin do Claude Code

Trial reels de Instagram em piloto automático. Depois de instalado, escreves `/comecar` e o Claude trata do resto contigo:

- **Todos os dias**, publica sozinho reels de texto sobre B-rolls teus, como *trial reels* (só aparecem a quem ainda não te segue).
- **Quando gravas um vídeo a falar** e o metes na Drive, o Claude edita-o: corta enganos e silêncios, põe legendas, imagens e música, escreve 2-3 hooks. Depois publica-o.
- **Cada reel oferece um recurso grátis** (um PDF com a tua estética) a quem comentar uma palavra; a DM vai sozinha.
- **De 14 em 14 dias** analisa os números, faz um relatório e melhora o que publica.

Funciona em **Mac e Windows**.

## O que precisas

0. **Acesso ao repositório** (é privado): uma conta no GitHub (github.com/signup) e o convite da Agens aceite (chega por email). Para o Git conseguir descarregar o plugin privado, entra no GitHub uma vez no terminal: instala o GitHub CLI (Mac: `brew install gh`; Windows: `winget install GitHub.cli`) e corre `gh auth login` e depois `gh auth setup-git`.

1. **Claude Code** instalado e com sessão iniciada (plano Pro ou Max): https://claude.com/claude-code
   - No Windows, instala também o **Git for Windows** (https://git-scm.com/download/win), que o Claude Code precisa.
2. Conta de **Instagram profissional** (criador ou empresa).
3. Conta na **Zernio** (https://zernio.com): é ela que publica e responde aos comentários. O `/comecar` explica como criar.
4. **Google Drive** ligada ao Claude: em claude.ai → Definições → Conectores → Google Drive → Ligar.
5. Uns 5 GB livres no disco e o computador ligado de manhã.

## Instalar (2 minutos)

Abre o Claude Code num terminal e escreve, uma linha de cada vez:

```
/plugin marketplace add Agens-Consulting/fabrica-de-reels
/plugin install fabrica-de-reels@fabrica-de-reels
```

Fecha e volta a abrir o Claude Code. Depois escreve:

```
/comecar
```
(no menu aparece como `/fabrica-de-reels:comecar`; também podes escrever só "quero começar a fábrica de reels")

e segue as instruções. O onboarding demora 45-60 minutos (instala o que falta, liga a Zernio e a Drive, estuda o teu perfil, aprova temas contigo, cria os primeiros recursos e mostra-te vídeos de ensaio). Podes parar a meio e continuar mais tarde com `/comecar`.

## No dia a dia

| Comando | Para quê |
|---|---|
| `/reels` | Ver o que saiu, o que está agendado, avisos; resolver o que ficou à tua espera; ligar/desligar |
| `/novo-recurso <ideia ou link>` | Criar um recurso grátis novo, com palavra, automação e textos |
| Mandar um vídeo para a pasta **1. RAW** da Drive | O Claude edita-o e publica-o sozinho |
| Mandar B-rolls para a pasta **3. B-rolls** | Entram na fábrica no dia seguinte |

## Atualizar

```
/plugin marketplace update fabrica-de-reels
/plugin update fabrica-de-reels@fabrica-de-reels
```
Reinicia o Claude Code e escreve `/reels` (atualiza a tua pasta sem tocar nos teus dados).

## Privacidade

A tua chave da Zernio e as tuas configurações ficam só no teu computador, no ficheiro `.env` da tua pasta de trabalho. Nada é enviado para quem fez o plugin. As pastas RAW, B-rolls e Músicas da tua Drive ficam partilhadas **por link, só leitura**, para o computador as conseguir ler sozinho: só quem tiver o link as consegue abrir.

## Licenças

Fonte Montserrat (SIL Open Font License). Bandeira 🇵🇹 do Twemoji (CC-BY 4.0, © Twitter/X e colaboradores). Imagens dos vídeos vêm da Pixabay, Openverse e Wikimedia Commons, com as licenças de cada uma.
