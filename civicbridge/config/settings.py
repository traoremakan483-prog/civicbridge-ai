import os
from pathlib import Path

APP_NAME = "CivicBridge"
APP_TAGLINE = "Multilingual Public Service Navigator"

BASE_DIR = Path(__file__).resolve().parent.parent

SUPPORTED_LANGUAGES = {
    "English": "en",
    "Malay": "ms",
    "Indonesian": "id",
}

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
        "upload_active_note": "Custom document active — built-in domain overridden.",
        "question_header": "Ask your question",
        "question_placeholder": "Ask about healthcare, social aid, emergency support, or family care…",
        "submit_btn": "Get Answer →",
        "translate_btn_prefix": "Translate into",
        "info_no_doc": "👈 Select a support domain from the sidebar to get started.",
        "warn_empty": "Please enter a question before submitting.",
        "spinner_loading": "Loading knowledge base…",
        "spinner_answering": "Searching the knowledge base and generating your answer…",
        "spinner_translating": "Translating your answer…",
        "already_in_lang": "Output is already in English.",
        "already_english": "Outputs are already in English.",
        "hero_desc": (
            "CivicBridge helps you understand public-service support across "
            "healthcare, social aid, emergency support, and family care. "
            "Ask in English, Malay, or Indonesian."
        ),
        "what_help_header": "What CivicBridge can help with",
        "example_questions_header": "Example Questions",
        "empty_state_msg": "Start by selecting a support domain and asking a question.",
        "guidance_line": "Select a support domain, then ask your question.",
        "credibility_note": "Answers are generated from curated official-style source guides.",
        "example_questions": [
            "Who is eligible for healthcare assistance?",
            "What documents do I need to apply?",
            "What financial help is available for low-income households?",
            "How long does emergency support take to process?",
            "Can single parents apply for family care support?",
        ],
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
        "upload_active_note": "Dokumen tersuai aktif — domain terbina dalam digantikan.",
        "question_header": "Tanya soalan anda",
        "question_placeholder": "Tanya tentang kesihatan, bantuan sosial, sokongan kecemasan, atau penjagaan keluarga…",
        "submit_btn": "Dapatkan Jawapan →",
        "translate_btn_prefix": "Terjemah ke",
        "info_no_doc": "👈 Pilih domain sokongan dari bar sisi untuk bermula.",
        "warn_empty": "Sila masukkan soalan sebelum menghantar.",
        "spinner_loading": "Memuatkan pangkalan pengetahuan…",
        "spinner_answering": "Mencari pangkalan pengetahuan dan menjana jawapan anda…",
        "spinner_translating": "Menterjemah jawapan anda…",
        "already_in_lang": "Output sudah dalam Bahasa Melayu.",
        "already_english": "Output sudah dalam Bahasa Melayu.",
        "hero_desc": (
            "CivicBridge membantu anda memahami sokongan perkhidmatan awam "
            "merangkumi penjagaan kesihatan, bantuan sosial, sokongan kecemasan, "
            "dan penjagaan keluarga. Tanya dalam Bahasa Inggeris, Melayu, atau Indonesia."
        ),
        "what_help_header": "Apa yang boleh dibantu oleh CivicBridge",
        "example_questions_header": "Contoh Soalan",
        "empty_state_msg": "Mulakan dengan memilih domain sokongan dan bertanya soalan.",
        "guidance_line": "Pilih domain sokongan, kemudian tanya soalan anda.",
        "credibility_note": "Jawapan dijana daripada panduan sumber gaya rasmi yang dikurasi.",
        "example_questions": [
            "Siapa yang layak mendapat bantuan penjagaan kesihatan?",
            "Apakah dokumen yang diperlukan untuk memohon?",
            "Apakah bantuan kewangan yang tersedia untuk isi rumah berpendapatan rendah?",
            "Berapa lama sokongan kecemasan diproses?",
            "Bolehkah ibu atau bapa tunggal memohon sokongan penjagaan keluarga?",
        ],
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
        "upload_active_note": "Dokumen kustom aktif — domain bawaan digantikan.",
        "question_header": "Ajukan pertanyaan Anda",
        "question_placeholder": "Tanya tentang kesehatan, bantuan sosial, dukungan darurat, atau perawatan keluarga…",
        "submit_btn": "Dapatkan Jawaban →",
        "translate_btn_prefix": "Terjemahkan ke",
        "info_no_doc": "👈 Pilih domain dukungan dari bilah sisi untuk memulai.",
        "warn_empty": "Silakan masukkan pertanyaan sebelum mengirim.",
        "spinner_loading": "Memuat basis pengetahuan…",
        "spinner_answering": "Mencari basis pengetahuan dan menghasilkan jawaban Anda…",
        "spinner_translating": "Menerjemahkan jawaban Anda…",
        "already_in_lang": "Output sudah dalam Bahasa Indonesia.",
        "already_english": "Output sudah dalam Bahasa Indonesia.",
        "hero_desc": (
            "CivicBridge membantu Anda memahami dukungan layanan publik di bidang "
            "kesehatan, bantuan sosial, dukungan darurat, dan perawatan keluarga. "
            "Tanyakan dalam Bahasa Inggris, Melayu, atau Indonesia."
        ),
        "what_help_header": "Apa yang dapat dibantu CivicBridge",
        "example_questions_header": "Contoh Pertanyaan",
        "empty_state_msg": "Mulailah dengan memilih domain dukungan dan mengajukan pertanyaan.",
        "guidance_line": "Pilih domain dukungan, lalu ajukan pertanyaan Anda.",
        "credibility_note": "Jawaban dihasilkan dari panduan sumber resmi yang telah dikurasi.",
        "example_questions": [
            "Siapa yang berhak mendapatkan bantuan kesehatan?",
            "Dokumen apa yang diperlukan untuk mendaftar?",
            "Bantuan keuangan apa yang tersedia untuk rumah tangga berpenghasilan rendah?",
            "Berapa lama proses dukungan darurat?",
            "Apakah orang tua tunggal bisa mengajukan dukungan perawatan keluarga?",
        ],
    },
}
