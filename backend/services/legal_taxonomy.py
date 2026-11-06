"""Colloquial-to-legal taxonomy bridge and factual completeness detector.

The taxonomy is used before retrieval to map everyday complaints to the legal
clusters in the corpus, and after retrieval to decide whether the system has
enough facts to answer with citations (Tier 1) or should ask for clarification
(Tier 2) / explain that the matter is out of scope (Tier 3).
"""

import re
from typing import Any, Dict, List, Optional

LEGAL_DOMAIN_CLUSTERS: Dict[str, Dict[str, Any]] = {
    "DISKRIMINASI_DAN_KONSUMEN": {
        "label": "Diskriminasi Ras/Etnis, HAM & Perlindungan Konsumen",
        "candidate_docs": [
            "UU 40/2008", "UU 8/1999", "UU 39/1999", "KUHP Baru",
        ],
        "triggers": [
            "direndahkan", "disepelekan", "dianggap tidak memiliki uang",
            "dianggap gak punya duit", "dianggap miskin", "dibeda-bedakan",
            "pilih kasih", "utamakan bule", "warga lokal dianaktirikan",
            "ditolak masuk", "diusir", "minimum spend beda", "tidak dilayani",
            "rasis", "rasisme", "hina suku", "hina etnis", "diskriminasi",
            "diskriminatif", "tidak adil", "perlakuan berbeda",
            "penolakan layanan", "hak konsumen", "konsumen",
            "perlindungan konsumen", "pelaku usaha", "etnis",
            "consumer protection", "racial discrimination",
        ],
        "inject_keywords": [
            "perlakuan berbeda", "penolakan layanan", "diskriminasi", "ras",
            "etnis", "hak konsumen", "pelaku usaha", "perlindungan konsumen",
        ],
        "required_elements_hint": (
            "Sebutkan lokasi/jenis tempat usaha (restoran, beach club, hotel), "
            "pihak yang melakukan penolakan, dan bentuk pembedaan layanannya."
        ),
        "authority": "Dinas Pariwisata Provinsi Bali atau BPSK",
        "rewrites": [
            "Wisatawan lokal ditolak masuk dan dibedakan syarat minimum spend dengan WNA di beach club Bali",
            "Pelaku usaha restoran di Bali menolak melayani pengunjung karena dianggap tidak memiliki uang",
            "Staf tempat wisata melakukan penghinaan ras dan etnis kepada pengunjung lokal",
        ],
    },
    "KAWASAN_SUCI_DAN_ADAT": {
        "label": "Pelindungan Pura, Kawasan Suci & Ketertiban Adat (termasuk Nyepi)",
        "candidate_docs": [
            "SE Gubernur 4/2023", "Pergub Bali 25/2020", "Perda Bali 4/2019",
            "Kompilasi Nyepi",
        ],
        "triggers": [
            "masuk pura", "pakai bikini", "baju terbuka", "tidak pakai kamben",
            "tidak pakai sarung", "panjat pohon", "pohon suci", "pohon keramat",
            "injak banten", "injak sesajen", "keluar saat nyepi",
            "nyalakan lampu nyepi", "berisik saat nyepi", "foto telanjang",
            "foto tidak sopan", "sedang haid masuk pura", "menstruasi",
            "utama mandala", "kawasan suci", "tempat suci", "pratima",
            "pecalang", "desa adat", "catur brata", "nyepi", "busana adat",
            "pura", "upacara adat", "kegiatan keagamaan", "tree", "sacred tree", "sacred", "holy", "temple", "temples", "mount batur", "posed naked", "climbed", "climb", "batur", "sacred site", "plastic trash", "throwing plastic", "trash", "littering", "plastic bottles",
        ],
        "inject_keywords": [
            "kawasan suci", "utama mandala", "pohon keramat", "busana adat",
            "catur brata penyepian", "desa adat", "pecalang", "pelindungan pura",
        ],
        "required_elements_hint": (
            "Sebutkan lokasi spesifik (area Pura, objek sakral, atau desa adat) "
            "dan tindakan yang dilakukan."
        ),
        "authority": "Pecalang, Majelis Desa Adat (MDA), atau Dinas Pariwisata",
        "rewrites": [
            "Wisatawan memakai bikini dan masuk area Utama Mandala Pura Besakih",
            "Wisatawan memanjat pohon suci dan mengotori kawasan pura di Tabanan",
            "Wisatawan keluar hotel dan menyalakan lampu saat Nyepi di Bali",
        ],
    },
    "PUNGUTAN_DAN_KEWAJIBAN_WNA": {
        "label": "Pungutan Wisatawan Asing (Love Bali) & Kepatuhan WNA",
        "candidate_docs": [
            "Perda Bali 6/2023", "Perda 2/2025", "Pergub 2/2024",
            "Pergub 25/2025", "UU 15/2023",
        ],
        "triggers": [
            "pungutan 150 ribu", "pungutan 150000", "retribusi turis",
            "love bali", "bayar pajak turis", "pajak turis",
            "bebas pungutan", "cara bayar pungutan", "wna belum bayar",
            "pungutan wisman", "pungutan wisatawan", "pungutan asing",
            "pungutan", "retribusi", "kitas", "kitap", "golden visa",
            "visa diplomatik", "levy", "tourist levy", "150k", "love bali online", "pay levy", "pay the bali tourist levy", "deport", "deported", "exchange currency", "money changers", "money changer", "kupva", "authorized kupva",
        ],
        "inject_keywords": [
            "pungutan wisatawan asing", "Rp150.000", "pembayaran elektronik",
            "love bali", "pengecualian pungutan", "sanksi administratif",
        ],
        "required_elements_hint": (
            "Sebutkan status kewarganegaraan wisatawan, tujuan kunjungan, dan "
            "apakah sudah memiliki bukti bayar Love Bali."
        ),
        "authority": "Dinas Pariwisata Provinsi Bali atau kanal Love Bali",
        "rewrites": [
            "Wisatawan asing belum membayar pungutan Love Bali Rp150.000 di Bandara Ngurah Rai",
            "Pemegang KITAS meminta pengecualian pungutan wisatawan asing di Bali",
            "Wisatawan asing tidak membayar pungutan dan mendapat sanksi administratif",
        ],
    },
    "IMIGRASI_DAN_KERJA_ILEGAL": {
        "label": "Keimigrasian & Penyalahgunaan Izin Tinggal WNA",
        "candidate_docs": ["UU 6/2011", "SE Gubernur 4/2023"],
        "triggers": [
            "bule jualan", "bule kerja", "bule buka usaha", "bule ngojek",
            "bule jadi fotografer", "bule ngajar surfing", "bule buka rental",
            "visa turis buat kerja", "overstay", "kerja ilegal",
            "bekerja tanpa izin", "deportasi", "izin tinggal", "imigrasi",
            "keimigrasian", "visa", "tenaga kerja asing",
            "warga negara asing bekerja",
        ],
        "inject_keywords": [
            "izin tinggal", "keimigrasian", "bekerja tanpa izin",
            "visa kunjungan", "deportasi", "tindakan administratif",
        ],
        "required_elements_hint": (
            "Sebutkan aktivitas komersial/pekerjaan yang dilakukan WNA dan "
            "lokasi kegiatannya."
        ),
        "authority": "Kantor Imigrasi Kelas I Khusus TPI Ngurah Rai",
        "rewrites": [
            "Warga negara asing bekerja sebagai fotografer di Bali tanpa visa kerja",
            "Warga negara asing berjualan di pantai Bali dengan visa turis",
            "Warga negara asing overstay dan bekerja di rental motor Bali",
        ],
    },
    "RUANG_DIGITAL_DAN_ITE": {
        "label": "Ujaran Kebencian, Pencemaran Nama Baik & Konten Viral (ITE)",
        "candidate_docs": ["UU ITE", "KUHP Baru"],
        "triggers": [
            "viral di medsos", "hina bali", "caci maki di tiktok",
            "fitnah di instagram", "sebar hoaks", "ujaran kebencian",
            "ancaman online", "doxing", "pencemaran nama baik", "sara",
            "konten viral", "medsos", "tiktok", "instagram", "ite",
            "informasi elektronik", "transaksi elektronik", "media sosial",
            "permusuhan", "golongan", "kuhp",
        ],
        "inject_keywords": [
            "informasi elektronik", "pencemaran", "kebencian", "sara",
            "media sosial", "transmisi elektronik", "ujaran kebencian",
        ],
        "required_elements_hint": (
            "Sebutkan apakah unggahan memuat tuduhan terhadap individu/tempat "
            "usaha tertentu atau provokasi antargolongan (SARA)."
        ),
        "authority": "Kominfo atau Unit Cyber Crime Kepolisian",
        "rewrites": [
            "Akun media sosial menyebarkan ujaran kebencian SARA terhadap warga Bali",
            "Unggahan Instagram memfitnah pemilik restoran di Bali",
            "Konten TikTok menyebarkan hoaks dan ancaman kepada pedagang lokal",
        ],
    },
    "STANDAR_WISATA_DAN_KETERTIBAN": {
        "label": "Kepariwisataan, Akomodasi & Ketertiban Umum",
        "candidate_docs": ["UU 18/2025", "Perda Bali 5/2020"],
        "triggers": [
            "villa bodong", "penginapan ilegal", "ugal-ugalan",
            "knalpot brong", "gak pakai helm", "tanpa helm", "mabuk di jalan",
            "bikin rusuh", "bikin ulah", "pemandu wisata liar",
            "daya tarik wisata", "standar usaha", "ketertiban umum",
            "pengelola wisata", "kepariwisataan", "pariwisata",
            "akomodasi", "pemandu wisata", "izin usaha pariwisata",
            "tata tertib wisatawan", "scooter", "scooters", "without license", "rented scooters", "riding", "rented", "deport", "deported", "illegal business", "licensed local guides", "local guides", "telanjang", "tanpa busana", "tanpa pakaian", "naked", "nude", "tour guide", "tourist guide", "licensed guide",
        ],
        "inject_keywords": [
            "daya tarik wisata", "standar usaha pariwisata", "ketertiban umum",
            "keselamatan", "perizinan", "pengelola wisata",
        ],
        "required_elements_hint": (
            "Sebutkan jenis usaha wisata atau bentuk gangguan ketertiban umum "
            "yang terjadi."
        ),
        "authority": "Dinas Pariwisata Provinsi Bali atau Satpol PP",
        "rewrites": [
            "Villa di Bali beroperasi tanpa izin dan tidak memenuhi standar usaha pariwisata",
            "Wisatawan mengendarai motor tanpa helm dan ugal-ugalan di jalan raya Kuta",
            "Pemandu wisata liar mengganggu ketertiban di daya tarik wisata Bali",
        ],
    },
    "REGISTRY_ONLY": {
        "label": "Instrumen Registry-Only / Perlu Verifikasi Lokal",
        "candidate_docs": [
            "SE Gubernur 7/2025", "SE Kapolri 6/2015", "SKB ITE 2021",
            "Awig-awig Desa Adat",
        ],
        "triggers": [
            "se 7/2025", "se gubernur 7 2025", "se kapolri", "skb ite",
            "awig-awig desa adat penglipuran", "awig-awig tenganan",
            "pararem desa adat",
        ],
        "inject_keywords": [
            "surat edaran gubernur", "awig-awig", "pararem", "pedoman ite",
        ],
        "required_elements_hint": (
            "Sebutkan instrumen/desa adat spesifik dan dasar kewenangannya; "
            "teks resmi instrumen ini belum tersedia di korpus." 
        ),
        "authority": "Majelis Desa Adat (MDA) atau instansi penerbit",
        "rewrites": [
            "Apa kewajiban wisatawan asing menurut SE Gubernur Bali 4/2023?",
            "Apa aturan busana adat di Pura menurut Pergub Bali 25/2020?",
            "Apa sanksi pelanggaran kawasan suci menurut Perda Bali 5/2020?",
        ],
    },
}

LOCATION_TERMS = (
    "bali", "indonesia", "pura", "besakih", "uluwatu", "tanah lot",
    "lempuyang", "ubud", "kuta", "seminyak", "canggu", "denpasar", "badung",
    "gianyar", "tabanan", "karangasem", "buleleng", "jembrana", "klungkung",
    "bangli", "bandara", "pelabuhan", "pantai", "beach club", "restoran",
    "hotel", "villa", "kafe", "pasar", "jalan raya", "terminal", "desa adat",
    "medsos", "tiktok", "instagram", "whatsapp", "facebook", "twitter",
    "pohon suci", "kawasan suci", "area pura", "temple", "temples", "shrine", "mount", "batur", "site", "sacred site", "beach", "airport", "cafe", "restaurant", "nusa penida", "jalan", "jalanan", "jalan-jalan", "tempat umum", "ruang publik", "public", "street", "road",
)

ACTION_TERMS = (
    "ditolak", "diusir", "tidak dilayani", "dibedakan", "dipungut",
    "memungut", "menagih", "memaksa", "membayar", "tidak membayar", "bayar",
    "memanjat", "masuk", "menginjak", "mengotori", "membuang", "bekerja",
    "berjualan", "ngojek", "memfitnah", "mengancam", "menghina", "menyebar",
    "mengunggah", "mabuk", "ugal", "tanpa helm", "melanggar", "keluar",
    "menyalakan", "berisik", "memakai", "mengenakan", "merusak", "mencuri",
    "menodai", "menolak", "mengejek", "mengucapkan", "berteriak", "memukul",
    "menganiaya", "overstay", "bikin ulah", "mengganggu", "berbuat",
    "melakukan", "mengemudi", "membawa", "dipukul", "dihina", "climb", "climbed", "climbing", "posed", "naked", "nude", "nudity", "riding", "ride", "rented", "rent", "deport", "deported", "deportation", "expel", "throw", "trash", "illegal", "without license", "damage", "damaging", "telanjang", "throwing", "littering", "tanpa busana", "tanpa baju", "buka baju", "topless", "mabuk", "drunk", "tanpa helm", "no helmet",
)

LEGAL_QUERY_TERMS = (
    "aturan", "aturannya", "sanksi", "kewajiban", "larangan", "hukum",
    "dasar hukum", "pasal", "regulasi", "peraturan", "ketentuan", "prosedur",
    "tata cara", "persyaratan", "mekanisme", "hukuman", "pidana", "denda",
    "apa", "apakah", "bagaimana", "berapa", "mengapa", "kenapa", "mandatory", "required", "is it mandatory",
)

REGISTRY_ONLY_TRIGGERS = {
    "se 7/2025": "Surat Edaran Gubernur Bali No. 7 Tahun 2025",
    "se gubernur 7 2025": "Surat Edaran Gubernur Bali No. 7 Tahun 2025",
    "se gubernur 7/2025": "Surat Edaran Gubernur Bali No. 7 Tahun 2025",
    "se kapolri": "SE Kapolri tentang Penanganan Ujaran Kebencian",
    "skb ite": "SKB Pedoman Implementasi UU ITE",
    "awig-awig": "Awig-awig Desa Adat",
    "pararem": "Pararem Desa Adat",
    "perarem": "Perarem Desa Adat",
}

REGISTRY_ONLY_PATTERNS = (
    (
        r"\bse\s+(?:gubernur\s+)?(?:bali\s+)?7(?:\s*/\s*|\s+)2025\b",
        "Surat Edaran Gubernur Bali No. 7 Tahun 2025",
    ),
    (
        r"\bsurat\s+edaran\s+gubernur\s+bali\s+(?:nomor\s+)?7\s+tahun\s+2025\b",
        "Surat Edaran Gubernur Bali No. 7 Tahun 2025",
    ),
    (
        r"\bse\s+kapolri\b",
        "SE Kapolri tentang Penanganan Ujaran Kebencian",
    ),
    (
        r"\bskb\s+ite\b",
        "SKB Pedoman Implementasi UU ITE",
    ),
    (
        r"\bawig[-\s]?awig\b",
        "Awig-awig Desa Adat",
    ),
    (
        r"\b(?:pararem|perarem)\b",
        "Pararem Desa Adat",
    ),
)


def _normalize(text: str) -> str:
    return " ".join((text or "").lower().split())


def _contains_any(text: str, terms: tuple) -> bool:
    return any(term in text for term in terms)


def _matched_terms(text: str, terms: List[str]) -> List[str]:
    return [term for term in terms if term in text]


def detect_registry_only(text: str) -> Optional[str]:
    normalized = _normalize(text)
    for pattern, label in REGISTRY_ONLY_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return label
    for trigger, label in REGISTRY_ONLY_TRIGGERS.items():
        if trigger in normalized:
            return label
    return None


def assess_factual_completeness(text: str) -> Dict[str, Any]:
    normalized = _normalize(text)
    out_of_scope_phrases = (
        "weather", "forecast", "cuaca", "prakiraan", "ramalan cuaca",
        "berapa lama visa turis berlaku", "masa berlaku visa",
        "how long is tourist visa valid", "visa validity",
    )
    is_out_of_scope_query = _contains_any(normalized, out_of_scope_phrases)
    matched_clusters = []
    matched_terms: List[str] = []
    if not is_out_of_scope_query:
        for cluster_id, cluster in LEGAL_DOMAIN_CLUSTERS.items():
            if cluster_id == "REGISTRY_ONLY":
                continue
            hits = _matched_terms(normalized, cluster["triggers"])
            if hits:
                matched_clusters.append(cluster_id)
                matched_terms.extend(hits)

    registry_only = detect_registry_only(normalized)
    if registry_only:
        matched_clusters.append("REGISTRY_ONLY")
        matched_terms.append(registry_only)

    has_location = _contains_any(normalized, LOCATION_TERMS)
    has_action = _contains_any(normalized, ACTION_TERMS)
    is_question = "?" in normalized or normalized.startswith(
        ("apa", "apakah", "bagaimana", "berapa", "kapan", "di mana",
         "siapa", "mengapa", "kenapa", "what", "how", "where", "who")
    )
    is_direct_legal_query = _contains_any(normalized, LEGAL_QUERY_TERMS)
    has_actor = any(
        term in normalized
        for term in (
            "wisatawan", "wna", "wni", "bule", "warga", "pengunjung",
            "turis", "pelaku usaha", "staf", "petugas", "pemandu", "pedagang",
            "akun", "hotel", "restoran", "beach club", "tourist", "tourists", "foreigner", "foreigners", "authorities", "driver", "orang", "seseorang", "anomali", "manusia", "someone", "person", "people", "guy", "girl", "stranger",
        )
    )

    is_factually_complete = False
    if matched_clusters == ["REGISTRY_ONLY"]:
        is_factually_complete = False
    elif matched_clusters:
        if is_question or is_direct_legal_query:
            is_factually_complete = True
        elif has_location and has_action and has_actor:
            is_factually_complete = True
        elif has_location and has_action and len(normalized.split()) >= 12:
            is_factually_complete = True

    missing_elements: List[str] = []
    if not has_location:
        missing_elements.append(
            "Lokasi/venue kejadian (pura, hotel, beach club, jalan raya, "
            "media sosial, atau desa adat)."
        )
    if not has_action:
        missing_elements.append(
            "Tindakan konkret yang terjadi (ditolak masuk, dipungut biaya, "
            "memanjat, bekerja tanpa izin, atau melanggar Nyepi)."
        )
    if not has_actor:
        missing_elements.append(
            "Pihak yang melakukan atau terdampak (wisatawan, pelaku usaha, "
            "staf, warga lokal, atau akun media sosial)."
        )
    if registry_only:
        missing_elements.append(
            "Instrumen/desa adat spesifik dan dasar kewenangannya; teks resmi "
            "instrumen ini belum tersedia di korpus."
        )
    if not matched_clusters:
        missing_elements.append(
            "Bidang hukum yang dituju (pungutan, kawasan suci, keimigrasian, "
            "diskriminasi/konsumen, ITE, atau standar wisata)."
        )

    primary_cluster = (
        matched_clusters[0] if matched_clusters else None
    )
    cluster = LEGAL_DOMAIN_CLUSTERS.get(primary_cluster, {})
    has_nyepi_term = any(
        "nyepi" in term.lower() or "catur brata" in term.lower()
        for term in matched_terms
    )
    query_expansion_keywords = []
    for cluster_id in matched_clusters[:2]:
        for keyword in LEGAL_DOMAIN_CLUSTERS[cluster_id]["inject_keywords"]:
            if "nyepi" in keyword.lower() or "catur brata" in keyword.lower():
                if not has_nyepi_term:
                    continue
            query_expansion_keywords.append(keyword)
    query_expansion = " ".join(query_expansion_keywords)

    if registry_only:
        tone = "Instrumen Registry-Only / Perlu Verifikasi Lokal"
    elif not matched_clusters:
        tone = "Di Luar Cakupan Hukum"
    elif not is_factually_complete:
        tone = "Keluhan Subjektif Tanpa Konteks Lokasi"
    elif is_question:
        tone = "Pertanyaan Hukum"
    else:
        tone = "Kronologi Faktual"

    return {
        "is_out_of_scope": is_out_of_scope_query,
        "candidate_clusters": matched_clusters,
        "candidate_labels": [
            LEGAL_DOMAIN_CLUSTERS[cluster_id]["label"]
            for cluster_id in matched_clusters
        ],
        "matched_terms": list(dict.fromkeys(matched_terms)),
        "has_location": has_location,
        "has_action": has_action,
        "has_actor": has_actor,
        "is_question": is_question,
        "is_direct_legal_query": is_direct_legal_query,
        "is_factually_complete": is_factually_complete,
        "registry_only_match": registry_only,
        "missing_elements": missing_elements,
        "query_expansion": query_expansion,
        "tone": tone,
        "authority": cluster.get("authority", ""),
        "required_elements_hint": cluster.get("required_elements_hint", ""),
        "suggested_query_rewrites": cluster.get("rewrites", []),
    }


def choose_epistemic_mode(
    top_score: float,
    taxonomy: Dict[str, Any],
) -> str:
    """Return VERIFIED_GROUNDED, NEEDS_CLARIFICATION, or OUT_OF_SCOPE_GUIDANCE."""
    if taxonomy.get("registry_only_match"):
        return "NEEDS_CLARIFICATION"
    if top_score >= 0.50 and taxonomy.get("is_factually_complete"):
        return "VERIFIED_GROUNDED"
    if taxonomy.get("candidate_clusters"):
        return "NEEDS_CLARIFICATION"
    if top_score >= 0.15:
        return "NEEDS_CLARIFICATION"
    return "OUT_OF_SCOPE_GUIDANCE"


IN_SCOPE_EXAMPLES = [
    "Bagaimana kewajiban membayar pungutan wisatawan asing Rp150.000 di Bali?",
    "Apa aturan berbusana dan larangan memanjat pohon suci saat masuk Pura di Bali?",
    "Apa sanksi bagi warga negara asing yang bekerja di Bali tanpa izin tinggal?",
]

TRIP_BRIEF_REWRITES = [
    "Liburan ke Pura Besakih dan menginap di Ubud selama 3 hari",
    "Sewa motor di Canggu dan berkunjung ke pantai selama seminggu",
    "Perjalanan ke Bali saat Nyepi bersama keluarga",
]

CLUSTER_NEXT_STEPS = {
    "DISKRIMINASI_DAN_KONSUMEN": [
        "Tuliskan kronologi: jenis tempat usaha, siapa yang menolak atau membedakan, dan bentuk perlakuan yang diterima.",
        "Simpan bukti tertulis seperti kebijakan minimum spend, tangkapan layar percakapan, struk, atau keterangan saksi.",
        "Sampaikan pengaduan ke Dinas Pariwisata Provinsi Bali atau BPSK; jangan menyebarkan data pribadi pihak lain.",
    ],
    "KAWASAN_SUCI_DAN_ADAT": [
        "Sebutkan nama pura atau desa adat, waktu kejadian, dan tindakan yang dilakukan.",
        "Dokumentasikan bukti tanpa mengganggu upacara atau mengambil foto secara intrusif.",
        "Hubungi Pecalang, Majelis Desa Adat (MDA), atau Dinas Pariwisata untuk kanal resmi.",
    ],
    "PUNGUTAN_DAN_KEWAJIBAN_WNA": [
        "Sebutkan status kewarganegaraan, tanggal kunjungan, dan apakah sudah membayar melalui Love Bali.",
        "Simpan bukti pembayaran elektronik atau kode referensi pungutan.",
        "Hubungi kanal resmi Love Bali atau Dinas Pariwisata Provinsi Bali.",
    ],
    "IMIGRASI_DAN_KERJA_ILEGAL": [
        "Sebutkan jenis aktivitas atau pekerjaan, lokasi, dan status izin tinggal orang tersebut.",
        "Simpan bukti aktivitas secara aman tanpa melakukan konfrontasi.",
        "Laporkan ke Kantor Imigrasi Kelas I Khusus TPI Ngurah Rai.",
    ],
    "RUANG_DIGITAL_DAN_ITE": [
        "Sebutkan platform, isi unggahan, waktu, dan pihak yang dituju.",
        "Simpan tautan serta tangkapan layar sebelum unggahan dihapus.",
        "Laporkan ke Kominfo atau Unit Cyber Crime Kepolisian setempat.",
    ],
    "STANDAR_WISATA_DAN_KETERTIBAN": [
        "Sebutkan jenis usaha atau kegiatan wisata dan lokasi kejadian.",
        "Catat bentuk pelanggaran atau gangguan ketertiban yang terjadi.",
        "Hubungi Dinas Pariwisata Provinsi Bali atau Satpol PP.",
    ],
}

GENERIC_NEXT_STEPS = [
    "Tuliskan kronologi singkat: apa yang terjadi, di mana, kapan, dan siapa yang terlibat.",
    "Simpan bukti objektif tanpa menyebarkan data pribadi atau identitas pihak lain.",
    "Gunakan kanal resmi yang disebut di bawah untuk memperoleh arahan lebih lanjut.",
]

OUT_OF_SCOPE_NEXT_STEPS = [
    "Sampaikan keluhan langsung kepada pihak terkait, misalnya pengelola hotel, restoran, atau maskapai.",
    "Gunakan platform ulasan atau mekanisme layanan pelanggan untuk urusan komersial biasa.",
    "Untuk keadaan darurat, hubungi layanan umum yang berwenang di Indonesia, misalnya 112.",
]


def _unique_rewrites(items: List[str], fallback: List[str]) -> List[str]:
    output: List[str] = []
    for item in list(items) + list(fallback):
        cleaned = " ".join((item or "").split())
        if cleaned and cleaned not in output:
            output.append(cleaned)
        if len(output) == 3:
            break
    return output


def build_deterministic_guidance(
    taxonomy: Dict[str, Any],
    mode: str,
    lang: str = "id",
) -> Dict[str, Any]:
    """Build safe, useful guidance without relying on the LLM."""
    clusters = [
        cluster for cluster in taxonomy.get("candidate_clusters", [])
        if cluster != "REGISTRY_ONLY"
    ]
    primary_cluster = clusters[0] if clusters else ""
    authority = taxonomy.get("authority") or "Dinas Pariwisata Provinsi Bali"

    if mode == "OUT_OF_SCOPE_GUIDANCE":
        if lang == "en":
            return {
                "missing_context_diagnosis": [
                    "This topic does not contain an element of Bali tourism or public-order regulation covered by the Pramana corpus.",
                ],
                "what_user_should_do_next": [
                    "Raise the issue directly with the business or service provider involved.",
                    "Use customer-service channels or review platforms for ordinary commercial matters.",
                    "For emergencies, contact the appropriate public emergency service in Indonesia, such as 112.",
                ],
                "suggested_query_rewrites": list(IN_SCOPE_EXAMPLES),
                "relevant_authority_or_channel": (
                    "No tourism-regulation channel applies to this topic."
                ),
            }
        return {
            "missing_context_diagnosis": [
                "Topik ini tidak memuat unsur regulasi pariwisata atau ketertiban umum Bali yang tersedia di korpus Pramana.",
            ],
            "what_user_should_do_next": list(OUT_OF_SCOPE_NEXT_STEPS),
            "suggested_query_rewrites": list(IN_SCOPE_EXAMPLES),
            "relevant_authority_or_channel": (
                "Tidak ada kanal regulasi pariwisata yang relevan untuk topik ini."
            ),
        }

    if taxonomy.get("unsupported_reference"):
        if lang == "en":
            return {
                "missing_context_diagnosis": [
                    "The article number or amount in your message does not appear in the Pramana corpus.",
                    "The concrete incident details are also incomplete.",
                ],
                "what_user_should_do_next": [
                    "Check the article number on the official JDIH portal or the issuing institution's website.",
                    "Describe what happened, where, and who was involved without relying on an unverified article number.",
                    "Use one of the in-scope examples below to ask a question the corpus can support.",
                ],
                "suggested_query_rewrites": list(IN_SCOPE_EXAMPLES),
                "relevant_authority_or_channel": (
                    "JDIH Bali or the institution that issued the regulation."
                ),
            }
        return {
            "missing_context_diagnosis": [
                "Nomor pasal atau nominal yang Anda sebut tidak ditemukan di korpus Pramana.",
                "Kronologi peristiwa konkret (lokasi, tindakan, dan pihak yang terlibat) belum lengkap.",
            ],
            "what_user_should_do_next": [
                "Periksa nomor pasal pada portal JDIH resmi atau situs instansi penerbit.",
                "Tuliskan peristiwa secara konkret tanpa bertumpu pada nomor pasal yang belum terverifikasi.",
                "Gunakan salah satu contoh pertanyaan di bawah yang dapat dijawab korpus.",
            ],
            "suggested_query_rewrites": list(IN_SCOPE_EXAMPLES),
            "relevant_authority_or_channel": (
                "JDIH Bali atau instansi penerbit regulasi terkait."
            ),
        }

    if taxonomy.get("registry_only_match"):
        diagnosis = [
            "Instrumen yang Anda sebut berstatus registry-only atau bersumber dari desa adat, sehingga teks resminya belum tersedia untuk dikutip di korpus Pramana.",
            "Pramana tidak akan mengarang nomor pasal atau sanksi dari instrumen yang belum diverifikasi.",
        ]
        next_steps = [
            "Sebutkan instrumen atau desa adat spesifik beserta dasar kewenangannya.",
            "Minta salinan resmi instrumen tersebut kepada instansi atau desa adat yang menerbitkan.",
            "Gunakan pertanyaan yang dapat dijawab korpus, misalnya kewajiban wisatawan menurut SE Gubernur Bali 4/2023.",
        ]
        authority = "Majelis Desa Adat (MDA) atau instansi penerbit instrumen"
        rewrites = _unique_rewrites(
            taxonomy.get("suggested_query_rewrites", []),
            IN_SCOPE_EXAMPLES,
        )
    else:
        diagnosis = list(taxonomy.get("missing_elements", []))[:3]
        if not diagnosis:
            diagnosis = [
                "Cerita Anda belum memuat lokasi, tindakan konkret, dan pihak yang terlibat secara lengkap.",
            ]
        next_steps = CLUSTER_NEXT_STEPS.get(primary_cluster, GENERIC_NEXT_STEPS)
        rewrites = _unique_rewrites(
            taxonomy.get("suggested_query_rewrites", []),
            IN_SCOPE_EXAMPLES,
        )

    if lang == "en":
        return {
            "missing_context_diagnosis": [
                "The input does not yet contain enough concrete facts to map to a specific article.",
            ],
            "what_user_should_do_next": [
                "Write a short chronology: what happened, where, when, and who was involved.",
                "Keep objective evidence without exposing other people's personal data.",
                "Use the official channel listed below for further guidance.",
            ],
            "suggested_query_rewrites": list(rewrites),
            "relevant_authority_or_channel": (
                "Dinas Pariwisata Provinsi Bali (Bali Tourism Office) or the relevant official channel."
            ),
        }

    return {
        "missing_context_diagnosis": diagnosis,
        "what_user_should_do_next": list(next_steps),
        "suggested_query_rewrites": list(rewrites),
        "relevant_authority_or_channel": authority,
    }


def build_triage_summary(
    taxonomy: Dict[str, Any],
    mode: str,
    lang: str = "id",
) -> str:
    """Deterministic, empathetic triage summary used when the LLM is absent."""
    clusters = [
        cluster for cluster in taxonomy.get("candidate_clusters", [])
        if cluster != "REGISTRY_ONLY"
    ]
    primary_cluster = clusters[0] if clusters else ""
    labels = taxonomy.get("candidate_labels") or []
    label = labels[0] if labels else "bidang hukum terkait"
    missing = "; ".join(taxonomy.get("missing_elements", [])[:3])

    if mode == "OUT_OF_SCOPE_GUIDANCE":
        if lang == "en":
            return (
                "This topic falls outside the Bali tourism and public-order "
                "regulations available in the Pramana corpus. Pramana will not "
                "invent a legal basis. You can still use the practical, "
                "non-legal steps below, or try one of the in-scope examples."
            )
        return (
            "Topik ini berada di luar cakupan regulasi pariwisata dan "
            "ketertiban umum Bali yang tersedia di korpus Pramana. Pramana "
            "tidak akan mengarang dasar hukum. Anda tetap dapat memakai saran "
            "praktis non-hukum di bawah atau mencoba salah satu contoh "
            "pertanyaan yang masuk cakupan."
        )

    if taxonomy.get("unsupported_reference"):
        if lang == "en":
            return (
                "Your message cites an article number or amount that does not "
                "appear in the Pramana corpus. Pramana cannot confirm that "
                "reference and will not repeat it as fact. Please check the "
                "official JDIH text and describe the concrete incident so the "
                "system can map the correct legal domain."
            )
        return (
            "Pesan Anda menyebut nomor pasal atau nominal yang tidak ditemukan "
            "di korpus Pramana. Pramana tidak dapat mengonfirmasi rujukan "
            "tersebut dan tidak akan mengulanginya sebagai fakta. Periksa "
            "naskah resmi di JDIH dan jelaskan peristiwa konkretnya agar sistem "
            "dapat memetakan bidang hukum yang tepat."
        )

    if taxonomy.get("registry_only_match"):
        if lang == "en":
            return (
                "The instrument you mentioned is registry-only or comes from a "
                "local customary authority, so its official text is not yet "
                "available for citation in the Pramana corpus. Pramana will not "
                "invent an article number or sanction. The general legal domain "
                "may still be relevant, but the specific instrument requires "
                "local verification."
            )
        return (
            "Instrumen yang Anda sebut berstatus registry-only atau berasal "
            "dari kewenangan adat setempat, sehingga teks resminya belum "
            "tersedia untuk dikutip di korpus Pramana. Pramana tidak akan "
            "mengarang nomor pasal atau sanksi. Bidang hukumnya bisa jadi "
            "relevan, tetapi instrumen spesifiknya memerlukan verifikasi lokal."
        )

    if primary_cluster == "DISKRIMINASI_DAN_KONSUMEN":
        if lang == "en":
            return (
                "Your message describes an experience of being demeaned or "
                "treated as if you had no money. A subjective feeling cannot "
                "yet be mapped to a specific article without the location, the "
                "actor, and the concrete act. If this happened as a refusal of "
                "service or different treatment based on race or ethnicity at "
                "a tourism business, consumer-protection and anti-discrimination "
                "rules may be relevant. Add the missing facts so Pramana can "
                "map the legal basis accurately."
            )
        return (
            "Kalimat Anda menggambarkan pengalaman perlakuan yang merendahkan "
            "atau asumsi sepihak terkait kemampuan finansial. Pengalaman "
            "subjektif belum dapat dipetakan ke pasal tertentu tanpa lokasi, "
            "pihak yang terlibat, dan bentuk tindakan konkret. Apabila ini "
            "terjadi sebagai penolakan layanan atau pembedaan perlakuan "
            "berbasis ras/etnis di tempat usaha pariwisata, payung hukum "
            "perlindungan konsumen dan anti-diskriminasi dapat relevan. "
            "Lengkapi konteks agar Pramana dapat memetakan dasar hukum yang "
            "tepat."
        )

    if lang == "en":
        return (
            f"Your message touches the legal domain of {label}, but the story "
            "does not yet contain enough concrete facts to map to a specific "
            "article. Pramana will not invent a legal basis. Add the missing "
            f"details: {missing or 'location, concrete action, and the actor involved'}."
        )
    return (
        f"Cerita Anda menyentuh bidang {label}, tetapi belum memuat unsur "
        "faktual yang cukup untuk memetakan pasal secara akurat. Pramana tidak "
        "akan mengarang dasar hukum. Lengkapi detail berikut: "
        f"{missing or 'lokasi, tindakan konkret, dan pihak yang terlibat'}."
    )


PROMPT_INJECTION_PATTERNS = [
    r"abaikan\s+(semua\s+)?instruksi",
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"reveal\s+your\s+system\s+prompt",
    r"you\s+are\s+dan\b",
    r"kamu\s+sekarang\s+harus",
    r"buat\s+pasal",
    r"buat\s+(?:perda|uu|aturan|undang)",
    r"create\s+a\s+fake",
    r"system\s+prompt",
]


def detect_prompt_injection(text: str) -> bool:
    normalized = _normalize(text)
    return any(
        re.search(pattern, normalized, re.IGNORECASE)
        for pattern in PROMPT_INJECTION_PATTERNS
    )
