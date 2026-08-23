"""
Verifier l'installation avant de lancer l'application.

    ./.venv/Scripts/python.exe scripts/check_setup.py

Repond a la question « pourquoi ca ne marche pas ? » en une commande, au lieu
de laisser deviner entre une dependance absente, un .env oublie, une cle
revoquee et un solde a zero — quatre causes qui produisent des messages
d'erreur tres differents et egalement obscurs.

La cle n'est JAMAIS affichee, meme partiellement au-dela de son prefixe.
"""

import os
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]

OK, KO, INFO = "  [ok]  ", "  [KO]  ", "  [--]  "
problemes: list[str] = []


def verdict(reussi: bool, message: str, correctif: str = "") -> None:
    print((OK if reussi else KO) + message)
    if not reussi and correctif:
        problemes.append(correctif)


print("\nCivicBridge — verification de l'installation\n" + "-" * 52)

# ── 1. Dependances ──────────────────────────────────────────────────────────
manquantes = []
for module in ("streamlit", "langchain", "langchain_openai", "faiss", "pymupdf", "dotenv"):
    try:
        __import__(module)
    except ImportError:
        manquantes.append(module)

verdict(
    not manquantes,
    f"dependances installees ({sys.version.split()[0]})"
    if not manquantes
    else f"dependances manquantes : {', '.join(manquantes)}",
    "pip install -e .   (dans l'environnement virtuel)",
)

# ── 2. Fichier .env ─────────────────────────────────────────────────────────
chemin_env = RACINE / ".env"
verdict(
    chemin_env.exists(),
    ".env present" if chemin_env.exists() else ".env absent",
    "cp .env.example .env   puis colle ta cle dedans",
)

if chemin_env.exists():
    from dotenv import load_dotenv

    load_dotenv(chemin_env)

# ── 3. La cle ───────────────────────────────────────────────────────────────
cle = os.environ.get("OPENAI_API_KEY", "")

if not cle:
    verdict(False, "OPENAI_API_KEY absente de l'environnement",
            "ajoute OPENAI_API_KEY=... dans .env")
elif cle.startswith("sk-remplace"):
    verdict(False, "OPENAI_API_KEY est encore la valeur d'exemple",
            "remplace-la par ta vraie cle dans .env")
elif not cle.startswith("sk-"):
    verdict(False, "OPENAI_API_KEY ne commence pas par 'sk-'",
            "verifie que tu as colle la cle entiere, sans guillemets")
else:
    # On n'affiche que la longueur : de quoi diagnostiquer un copier-coller
    # tronque sans jamais exposer le secret.
    verdict(True, f"OPENAI_API_KEY presente (prefixe sk-, {len(cle)} caracteres)")

# ── 4. Les guides ───────────────────────────────────────────────────────────
if not manquantes:
    sys.path.insert(0, str(RACINE / "civicbridge"))
    from config.settings import SUPPORT_DOMAINS  # noqa: E402

    absents = [p.name for p in SUPPORT_DOMAINS.values() if not p.exists()]
    verdict(
        not absents,
        f"{len(SUPPORT_DOMAINS)} guides trouves dans civicbridge/docs/"
        if not absents
        else f"guides absents : {', '.join(absents)}",
        "les PDF doivent etre dans civicbridge/docs/",
    )

# ── 5. L'API repond-elle, et le compte a-t-il du credit ? ───────────────────
# Le piege classique : la cle est valide mais le solde est a zero. L'API
# renvoie alors `insufficient_quota`, et on croit que la cle est mauvaise.
if not manquantes and cle.startswith("sk-") and not cle.startswith("sk-remplace"):
    try:
        from openai import OpenAI

        client = OpenAI(api_key=cle)
        # L'appel le moins cher possible : un seul token d'embedding.
        client.embeddings.create(model="text-embedding-3-small", input="ping")
        verdict(True, "l'API repond et le compte a du credit")
    except Exception as e:
        message = str(e)
        if "insufficient_quota" in message or "exceeded your current quota" in message:
            verdict(False, "cle valide, mais le solde du compte est a zero",
                    "Settings -> Billing : depose un montant (5 $ suffisent)")
        elif "invalid_api_key" in message or "Incorrect API key" in message:
            verdict(False, "la cle est refusee par OpenAI",
                    "cree une nouvelle cle : platform.openai.com/api-keys")
        else:
            verdict(False, f"appel a l'API echoue : {message[:90]}", "")

# ── Verdict ─────────────────────────────────────────────────────────────────
print("-" * 52)
if problemes:
    print("\nA corriger, dans cet ordre :\n")
    for i, c in enumerate(problemes, 1):
        print(f"  {i}. {c}")
    print()
    sys.exit(1)

print("\nTout est pret. Lance :\n")
print("  ./.venv/Scripts/streamlit.exe run civicbridge/app.py\n")
print(INFO + "Rappel : pose un plafond de depense sur ton compte OpenAI")
print(INFO + "(Settings -> Limits) avant tout deploiement public.\n")
