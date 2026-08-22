from pathlib import Path

APP_NAME = "CivicBridge"
APP_TAGLINE = "Multilingual Public Service Navigator"

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Langues ─────────────────────────────────────────────────────────────────
#
# La premiere version proposait anglais, malais, indonesien. Le jury a releve
# que c'etait insuffisant AU REGARD DU CONCEPT lui-meme, et il avait raison :
# le malais et l'indonesien sont largement intercomprehensibles, donc trois
# entrees dans le menu ne faisaient que DEUX portees reelles.
#
# Plus grave, c'etait le mauvais choix de langues. Un service public malaisien
# publie deja en malais et en anglais : les personnes que ces deux langues
# couvrent savaient deja se debrouiller. Celles qui n'y arrivent pas sont les
# travailleurs migrants (bengali, nepalais, birman), les Malaisiens indiens
# tamoulophones et les sinophones les plus ages.
#
# Le blocage n'a jamais ete technique — la traduction passe par le modele,
# donc une langue = une ligne ici. C'etait un defaut de conception produit :
# avoir choisi les langues qu'on connait plutot que celles des gens qu'on
# pretend servir.
SUPPORTED_LANGUAGES = {
    "English": "en",
    "Malay": "ms",
    "Tamil": "ta",
    "Mandarin": "zh",
    "Bengali": "bn",
    "Nepali": "ne",
    "Burmese": "my",
    "Indonesian": "id",
}

# Traduire automatiquement une consigne administrative officielle vers une
# langue peu dotee n'est pas neutre : une erreur envoie quelqu'un au mauvais
# guichet avec les mauvais papiers, apres avoir pose un jour de conge qu'il ne
# peut pas se permettre. On ne refuse pas de traduire pour autant — on affiche
# l'original anglais a cote, pour qu'un proche bilingue ou un agent puisse
# verifier.
MACHINE_TRANSLATION_NOTICE = (
    "Machine translation. The English version is shown alongside so that "
    "someone who reads English can check it before you act on it."
)

SUPPORT_DOMAINS = {
    "🏥 Healthcare Support": BASE_DIR / "docs" / "NHAP_Official_Guide.pdf",
    "🤝 Social Support": BASE_DIR / "docs" / "CSSG_Official_Guide.pdf",
    "🚑 Emergency Medical Relief": BASE_DIR / "docs" / "EMRP_Official_Guide.pdf",
    "👨‍👩‍👧 Family Care Support": BASE_DIR / "docs" / "FCSA_Official_Guide.pdf",
}

DOMAIN_DESCRIPTIONS = {
    "🏥 Healthcare Support": "National Healthcare Assistance Program (NHAP)",
    "🤝 Social Support": "Community Social Support Grant (CSSG)",
    "🚑 Emergency Medical Relief": "Emergency Medical Relief Program (EMRP)",
    "👨‍👩‍👧 Family Care Support": "Family Care Support Allowance (FCSA)",
}

DEFAULT_LLM_MODEL = "gpt-4o-mini"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

RETRIEVAL_K = 4

SAMPLE_DOCUMENT_PATH = BASE_DIR / "docs" / "NHAP_Official_Guide.pdf"

UI_LABELS = {
    "English": {
        "lang_header": "🌐 Your Language",
        "domain_header": "📋 Support Domain",
        "domain_hint": "Choose a topic to explore.",
        "advanced_header": "⚙️ Advanced: Custom Document",
        "advanced_hint": (
            "Upload your own PDF to temporarily override the built-in "
            "knowledge base. This is optional."
        ),
        "upload_label": "Upload an official PDF",
        "upload_note": "Overrides the selected support domain while active.",
        "question_header": "Ask your question",
        "question_placeholder": "Ask about healthcare, social aid, emergency support, or family care…",
        "submit_btn": "Get Answer →",
        "translate_btn_prefix": "Translate into",
        "info_no_doc": (
            "👈 Select a support domain from the sidebar to get started."
        ),
        "warn_empty": "Please enter a question before submitting.",
        "spinner_loading": "Loading knowledge base…",
        "spinner_answering": (
            "Searching the knowledge base and generating your answer…"
        ),
        "spinner_translating": "Translating…",
        "already_english": "Outputs are already in English.",
        "hero_desc": (
            "CivicBridge helps you understand public-service support across "
            "healthcare, social aid, emergency support, and family care. "
            "Ask in English, Malay, or Indonesian."
        ),
    },
    "Malay": {
        "lang_header": "🌐 Bahasa Anda",
        "domain_header": "📋 Domain Sokongan",
        "domain_hint": "Pilih topik untuk diterokai.",
        "advanced_header": "⚙️ Lanjutan: Dokumen Tersuai",
        "advanced_hint": (
            "Muat naik PDF anda sendiri untuk menggantikan pangkalan "
            "pengetahuan terbina dalam buat sementara. Ini adalah pilihan."
        ),
        "upload_label": "Muat naik PDF rasmi",
        "upload_note": "Menggantikan domain sokongan yang dipilih semasa aktif.",
        "question_header": "Tanya soalan anda",
        "question_placeholder": "Tanya tentang kesihatan, bantuan sosial, sokongan kecemasan, atau penjagaan keluarga…",
        "submit_btn": "Dapatkan Jawapan →",
        "translate_btn_prefix": "Terjemah ke",
        "info_no_doc": (
            "👈 Pilih domain sokongan dari bar sisi untuk bermula."
        ),
        "warn_empty": "Sila masukkan soalan sebelum menghantar.",
        "spinner_loading": "Memuatkan pangkalan pengetahuan…",
        "spinner_answering": (
            "Mencari pangkalan pengetahuan dan menjana jawapan anda…"
        ),
        "spinner_translating": "Menterjemah…",
        "already_english": "Output sudah dalam Bahasa Melayu.",
        "hero_desc": (
            "CivicBridge membantu anda memahami sokongan perkhidmatan awam "
            "merangkumi penjagaan kesihatan, bantuan sosial, sokongan kecemasan, "
            "dan penjagaan keluarga. Tanya dalam Bahasa Inggeris, Melayu, atau Indonesia."
        ),
    },
    "Indonesian": {
        "lang_header": "🌐 Bahasa Anda",
        "domain_header": "📋 Domain Dukungan",
        "domain_hint": "Pilih topik yang ingin dijelajahi.",
        "advanced_header": "⚙️ Lanjutan: Dokumen Kustom",
        "advanced_hint": (
            "Unggah PDF Anda sendiri untuk sementara menggantikan basis "
            "pengetahuan bawaan. Ini bersifat opsional."
        ),
        "upload_label": "Unggah PDF resmi",
        "upload_note": "Menggantikan domain dukungan yang dipilih selama aktif.",
        "question_header": "Ajukan pertanyaan Anda",
        "question_placeholder": "Tanya tentang kesehatan, bantuan sosial, dukungan darurat, atau perawatan keluarga…",
        "submit_btn": "Dapatkan Jawaban →",
        "translate_btn_prefix": "Terjemahkan ke",
        "info_no_doc": (
            "👈 Pilih domain dukungan dari bilah sisi untuk memulai."
        ),
        "warn_empty": "Silakan masukkan pertanyaan sebelum mengirim.",
        "spinner_loading": "Memuat basis pengetahuan…",
        "spinner_answering": (
            "Mencari basis pengetahuan dan menghasilkan jawaban Anda…"
        ),
        "spinner_translating": "Menerjemahkan…",
        "already_english": "Output sudah dalam Bahasa Indonesia.",
        "hero_desc": (
            "CivicBridge membantu Anda memahami dukungan layanan publik di bidang "
            "kesehatan, bantuan sosial, dukungan darurat, dan perawatan keluarga. "
            "Tanyakan dalam Bahasa Inggris, Melayu, atau Indonesia."
        ),
    },
}


def ui_labels_for(language: str) -> dict:
    """
    Libelles d'interface pour une langue, avec repli sur l'anglais.

    UI_LABELS n'est traduit a la main que pour trois langues. Les langues
    ajoutees ensuite servent aux REPONSES — ce qui est l'essentiel — et
    affichent une interface en anglais en attendant que les 18 cles soient
    traduites et relues.

    Un acces direct `UI_LABELS[langue]` leverait un KeyError et casserait
    l'application des qu'on ajoute une langue. Ce repli est ce qui permet
    d'elargir la couverture sans attendre la traduction complete du chrome.
    """
    return UI_LABELS.get(language, UI_LABELS["English"])


def ui_is_translated(language: str) -> bool:
    """Vrai si l'interface elle-meme existe dans cette langue."""
    return language in UI_LABELS
