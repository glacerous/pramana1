// Svelte 5 reactive i18n state and comprehensive dictionaries

const initialLang =
  typeof localStorage !== 'undefined'
    ? localStorage.getItem('pramana_lang') || 'id'
    : 'id';

export const i18n = $state({
  lang: initialLang,
  t(key, section = 'common') {
    const dict = DICT[i18n.lang] || DICT.id;
    if (section && dict[section] && dict[section][key]) {
      return dict[section][key];
    }
    for (const sec of Object.values(dict)) {
      if (typeof sec === 'object' && sec && key in sec) {
        return sec[key];
      }
    }
    return key;
  }
});

export function setLanguage(newLang) {
  const clean = newLang === 'en' ? 'en' : 'id';
  i18n.lang = clean;
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem('pramana_lang', clean);
  }
}

export const DICT = {
  id: {
    nav: {
      home: 'Beranda',
      tripBrief: 'Trip Brief',
      contextNote: 'Context Note',
      gate: 'Gerbang',
      corpus: 'Korpus',
      settings: 'Pengaturan'
    },
    common: {
      copy: 'Salin Catatan',
      copied: 'Tersalin',
      copySummary: 'Salin Ringkasan',
      openOriginal: 'Buka Naskah Asli',
      openSummary: 'Buka Ringkasan Sumber',
      maskedText: 'Teks tersamarkan:',
      piiRedacted: 'PII disamarkan:',
      entities: 'entitas',
      llmNotice: 'Ringkasan AI tidak diverifikasi Layer-1. Sitasi di bawah adalah teks korpus terverifikasi.',
      unavailableNotice: 'AI tidak tersedia. Sistem tidak menampilkan template sebagai jawaban AI; sitasi terverifikasi tetap ditampilkan.',
      abstainNotice: 'AI memilih abstain karena permintaan tidak dapat dijawab aman dari bukti korpus.',
      templateNotice: 'Template deterministik dipakai karena AI_MODE=optional atau API key tidak tersedia.',
      compilationNotice: 'Kompilasi pedoman, bukan kutipan pasal',
      verbatimNotice: 'Verbatim (ID)',
      summaryNotice: 'Ringkasan, bukan kutipan verbatim',
      penaltiesTitle: 'Sanksi yang tercantum dalam sumber',
      showAudit: 'Tampilkan Diagnostik Verifier',
      hideAudit: 'Sembunyikan Diagnostik Verifier',
      confidence: 'Keyakinan',
      tierLabel: 'TINGKAT',
      supersededBy: 'Disempurnakan oleh:',
      disclaimer: 'Catatan:',
      translationNotice: 'Terjemahan tidak resmi. Naskah bahasa Indonesia adalah versi yang berwenang.',
      aiAssistedNotice: 'Terjemahan dibantu AI, belum ditinjau manusia',
      humanReviewedNotice: 'Terjemahan telah ditinjau manusia',
      originalAuthoritativeLabel: 'Naskah Asli Bahasa Indonesia · Verbatim (ID)',
      supersededBanner: 'Disempurnakan oleh SE Gubernur Bali No. 7/2025; teks tetap dipertahankan sebagai rujukan historis.',
      serverWakingUp: 'Server sedang bangun, harap tunggu beberapa detik...',
      retryBtn: 'Coba Lagi'
    },
    settings: {
      badge: '05 // PREFERENSI PENGGUNA',
      title: 'Pengaturan',
      subtitle: 'Sesuaikan bahasa antarmuka dan riwayat perangkat.',
      langCardTitle: 'BAHASA ANTARMUKA',
      langCardSubtitle: 'Pilih bahasa tampilan untuk seluruh halaman aplikasi.',
      idLabel: 'Bahasa Indonesia',
      idDesc: 'Bahasa resmi dan rujukan naskah peraturan hukum Bali.',
      enLabel: 'English',
      enDesc: 'International traveler guidance and translated summaries.',
      audioCardTitle: 'PANDUAN AUDIO GERBANG',
      audioCardSubtitle: 'Atur suara yang berbicara saat kamu tap atau scan gerbang di tempat wisata.',
      voiceLang: 'BAHASA SUARA',
      speed: 'KECEPATAN SUARA',
      speedSlow: '0.85x (Lambat)',
      speedNormal: '1.0x (Normal)',
      speedFast: '1.15x (Cepat)',
      testVoiceBtn: 'Tes Suara Panduan',
      stopVoiceBtn: 'Hentikan Suara',
      storageCardTitle: 'DATA & PENYIMPANAN PERANGKAT',
      storageCardSubtitle: 'Semua preferensi disimpan secara lokal di browser kamu.',
      storageDesc: 'Pramana tidak menyimpan akun atau data pribadi kamu di server cloud.',
      clearDataBtn: 'Hapus Riwayat Gerbang & Reset Pengaturan'
    },
    landing: {
      heroHeadline1: 'The AI legal context layer',
      heroHeadline2: 'for Bali tourism & governance.',
      tripBtn: 'Susun Trip Brief',
      contextBtn: 'Uji Klaim Viral',
      archTitle: 'Three-Layer Legal Architecture',
      archDesc: 'Setiap permohonan melewati tiga tahap deterministik: penyaringan data pribadi otomatis (Tahap 01), filter spasio-temporal Gerbang Candi Bentar & Kalender Saka (Tahap 02), serta pencocokan kutipan terhadap 42 chunk dari 29 dokumen registry Pramana (Tahap 03). Registry bukan bukti kutipan, dan korpus tidak diverifikasi ulang secara real-time ke JDIH.',
      openCorpusBtn: 'Buka Korpus Regulasi',
      card1Title: 'Rencana Perjalanan & Kalender .ICS',
      card1Desc: 'Ubah draf itinerary menjadi daftar periksa kepatuhan berpasal, samarkan data reservasi tamu (PII), dan unduh pengingat Hari Suci Nyepi (.ics RFC 5545).',
      card1Btn: 'Buka Studio Trip Brief',
      card2Title: 'Verifikasi Klaim Insiden Viral',
      card2Desc: 'Luruskan misinformasi wisata dengan kutipan dari korpus regulasi Pramana yang dicocokkan Layer-1, atau penolakan spekulasi (Layer-2 Abstain). Bukan verifikasi real-time ke JDIH.',
      card2Btn: 'Uji Klaim Viral',
      card3Title: 'Jadwal Deterministik Bali 2026',
      card3Btn: 'Buka Korpus Pramana',
      nyepi: 'Hari Suci Nyepi (Tutup 24J)',
      ogoh: 'Pengerupukan (Ogoh-ogoh)',
      galungan: 'Hari Raya Galungan',
      kuningan: 'Hari Raya Kuningan'
    },
    gate: {
      badge: '03 // PANDUAN LOKASI WISATA',
      title: 'Gerbang Pintar',
      titleAccent: 'Pramana',
      subtitle: 'Kartu kepatuhan langsung di lokasi. Pilih gerbang wisata dan patuhi aturan setempat.',
      tapNote: 'Halaman ini otomatis terbuka saat kamu tap stiker NFC atau scan QR di gerbang masuk tempat wisata.',
      openGate: 'Buka Gerbang',
      scanQrBtn: 'Pindai QR / Tap NFC',
      allGates: 'Semua Gerbang',
      activeChunks: 'aturan aktif',
      historicalChunks: 'catatan historis',
      version: 'Versi aturan',
      aiBrief: 'Panduan Singkat',
      playAudio: 'Dengarkan Audio Panduan',
      stopAudio: 'Hentikan Audio',
      checks: 'Panduan Utama di Lokasi',
      legalBasis: 'Dasar Hukum Resmi',
      share: 'Bagikan Gerbang Ini',
      copyLink: 'Salin Tautan',
      copied: 'Tautan disalin.',
      scope: 'Catatan Kawasan'
    },
    trip: {
      badge: '01 // PANDUAN PRA-PERJALANAN',
      title: 'Panduan Kepatuhan Rute & Kalender Bali',
      subtitle: 'Periksa kepatuhan rencana perjalanan kamu dari penutupan Hari Suci Nyepi 24 jam, aturan kawasan suci pura, dan retribusi wisman.',
      inputSection: 'RENCANA PERJALANAN',
      inputLabel: 'Rencana Aktivitas & Tujuan Kunjungan',
      placeholder: 'Tulis rencana perjalanan, destinasi pura, sewa kendaraan, atau jadwal tiba...',
      startDate: 'Tanggal Tiba',
      endDate: 'Tanggal Pulang',
      travelerType: 'Kategori Wisatawan',
      typeInt: 'Wisatawan Mancanegara / WNA (Wajib Love Bali Rp150.000)',
      typeDom: 'Wisatawan Nusantara / WNI (Bebas Pungutan Wisman)',
      submitBtn: 'Susun Panduan Kepatuhan',
      loadingBtn: 'Memeriksa Korpus Hukum...',
      privacyNote: 'Data reservasi (email, nomor paspor, kode booking) disamarkan otomatis sebelum analisis.',
      downloadIcs: 'Unduh Jadwal Kalender (.ICS)',
      loveBaliLink: 'Portal Resmi Love Bali (Rp150k) ↗',
      priorityCalendar: 'PRIORITAS 01 // PERINGATAN KALENDER',
      priorityLegal: '02 // KETENTUAN HUKUM',
      articlesLabel: 'PASAL',
      copySummary: 'Salin Ringkasan',
      copied: 'Tersalin',
      abstainTitle: 'Tidak Ditemukan Isu Kepatuhan Khusus',
      abstainDesc: 'Pemeriksaan kalender tetap dijalankan. Peringatan Nyepi atau upacara budaya, jika ada, ditampilkan di atas. Tidak ada kutipan pasal yang dipaksakan.',
      presets: [
        {
          label: '01 // Nyepi (18-21 Mar)',
          text: 'Trip ke Ubud dan Seminyak tanggal 18 sampai 21 Maret 2026. Mau sewa motor keliling nonton pawai ogoh-ogoh malam hari dan ke Tanah Lot pas hari H Nyepi.'
        },
        {
          label: '02 // Kawasan Suci Pura',
          text: 'Tiba di Denpasar 10 April. Rencana mengunjungi Pura Besakih dan Tirta Empul naik motor sewaan, lalu masuk area utama tempat sembahyang pakai baju santai pantai.'
        },
        {
          label: '03 // Sewa Motor & Remote',
          text: 'Tinggal di Canggu 1 bulan sambil kerja remote. Mau sewa motor matic 150cc dari vila lokal tanpa SIM internasional dan jalan-jalan ke Kintamani.'
        }
      ]
    },
    context: {
      badge: '02 // PUBLIC CONTEXT VERIFIER',
      title: 'Verifikasi Klaim Insiden & Rujukan Pasal',
      subtitle: 'Masukkan klaim atau video viral seputar insiden wisata di Bali untuk mendapatkan pasal hukum resmi dan fakta objektif.',
      claimNarrative: 'NARASI KLAIM',
      dualGuard: 'Dual-Layer Guard',
      inputLabel: 'Teks Unggahan atau Klaim Pelanggaran',
      placeholder: 'Tempel teks unggahan media sosial, keluhan warga, atau klaim pelanggaran aturan di sini...',
      submitBtn: 'Uji Klaim & Susun Konteks',
      loadingBtn: 'Mencocokkan Korpus Pramana...',
      protocolL1: 'Layer-1 (korpus): Kutipan dicocokkan dengan teks yang tersimpan di korpus lokal Pramana, bukan verifikasi ulang real-time ke JDIH.',
      protocolL2: 'Layer-2 Abstain: Topik di luar cakupan hukum ditolak otomatis tanpa spekulasi.',
      readyBadge: '01 // CATATAN KONTEKS NETRAL (SIAP PUBLIKASI)',
      copyBtn: 'Salin Catatan',
      copiedBtn: 'Tersalin',
      framingTitle: 'Penanda Retorika Sensasional Terdeteksi',
      citationsBadge: '02 // RUJUKAN KORPUS',
      documentsLabel: 'DOKUMEN',
      exactMatch: 'LAYER-1 EXACT MATCH (KORPUS)',
      abstainTitle: 'Tidak Ditemukan Dasar Hukum di Korpus Pramana',
      abstainDesc: 'Sintesis dibatalkan secara deterministik karena tidak ada kecocokan yang melewati ambang relevansi korpus. Keputusan ini bukan pernyataan bahwa perbuatan tersebut sah.',
      presets: [
        {
          label: '01 // Pohon Keramat Pura',
          text: 'Viral di medsos: seorang wisatawan bule memanjat pohon beringin keramat di kawasan pura Tabanan tanpa pakaian dan berteriak kasar kepada warga lokal saat ditegur.'
        },
        {
          label: '02 // Pungutan Rp150.000',
          text: 'Beredar video wisatawan asing berdebat di bandara menolak membayar retribusi turis asing 150000 di loket Love Bali dan mengaku tidak tahu aturan tersebut.'
        },
        {
          label: '03 // Klaim "Kebal Hukum"',
          text: 'Semua bule di Bali kebal hukum dan polisi diam saja! Harusnya langsung dideportasi sekarang juga tanpa pandang bulu!'
        },
        {
          label: '04 // Uji Abstain',
          text: 'Kucing oranye tertidur di atas meja kasir restoran dan meminta ikan tongkol goreng dari pengunjung.'
        }
      ]
    },
    corpus: {
      badge: '04 // REGISTRY DOKUMEN',
      title: 'Korpus Regulasi Bali',
      subtitle: 'Telusuri chunk pasal resmi dari dokumen terdaftar JDIH BPK dan Pemprov Bali.',
      searchPlaceholder: 'Cari pasal, kata kunci...',
      loading: 'Memuat indeks korpus regulasi...'
    }
  },
  en: {
    nav: {
      home: 'Home',
      tripBrief: 'Trip Brief',
      contextNote: 'Context Note',
      gate: 'Smart Gate',
      corpus: 'Corpus',
      settings: 'Settings'
    },
    common: {
      copy: 'Copy Note',
      copied: 'Copied',
      copySummary: 'Copy Summary',
      openOriginal: 'Open Original Document',
      openSummary: 'Open Source Summary',
      maskedText: 'Masked text:',
      piiRedacted: 'PII redacted:',
      entities: 'entities',
      llmNotice: 'AI summary is not Layer-1 verified. Citations below are verified corpus text.',
      unavailableNotice: 'AI unavailable. The system does not present template text as AI output; verified citations remain available.',
      abstainNotice: 'AI abstained because the request cannot be safely answered from corpus evidence.',
      templateNotice: 'Deterministic template used because AI_MODE=optional or API key unavailable.',
      compilationNotice: 'Guidance compilation, not a statutory excerpt',
      verbatimNotice: 'Verbatim (ID)',
      summaryNotice: 'Summary, not a verbatim excerpt',
      penaltiesTitle: 'Sanctions stated in the source',
      showAudit: 'Show Verifier Diagnostics',
      hideAudit: 'Hide Verifier Diagnostics',
      confidence: 'Confidence',
      tierLabel: 'TIER',
      supersededBy: 'Superseded by:',
      disclaimer: 'Note:',
      translationNotice: 'Unofficial English translation. The Indonesian text is the authoritative version.',
      aiAssistedNotice: 'AI-assisted translation, not yet human-reviewed',
      humanReviewedNotice: 'Human-reviewed English translation',
      originalAuthoritativeLabel: 'Original Indonesian Legal Text · Verbatim (ID)',
      supersededBanner: 'Superseded by Bali Governor Circular Letter (SE) No. 7/2025; text kept as historical reference.',
      serverWakingUp: 'Server is waking up, please wait a few seconds...',
      retryBtn: 'Retry'
    },
    settings: {
      badge: '05 // USER PREFERENCES',
      title: 'Settings',
      subtitle: 'Configure interface language and device storage.',
      langCardTitle: 'INTERFACE LANGUAGE',
      langCardSubtitle: 'Choose the display language for the entire application.',
      idLabel: 'Bahasa Indonesia',
      idDesc: 'Official language of Balinese statutory legal texts.',
      enLabel: 'English',
      enDesc: 'International traveler guidance and translated summaries.',
      audioCardTitle: 'ON-SITE AUDIO GUIDE (TTS)',
      audioCardSubtitle: 'Configure the spoken voice when tapping or scanning gate totems on site.',
      voiceLang: 'VOICE LANGUAGE',
      speed: 'SPEECH SPEED',
      speedSlow: '0.85x (Slow)',
      speedNormal: '1.0x (Normal)',
      speedFast: '1.15x (Fast)',
      testVoiceBtn: 'Test Audio Guide',
      stopVoiceBtn: 'Stop Audio Guide',
      storageCardTitle: 'DEVICE DATA & STORAGE',
      storageCardSubtitle: 'All preferences are stored locally on your device browser.',
      storageDesc: 'Pramana does not store your accounts or personal data on cloud servers.',
      clearDataBtn: 'Clear Gate History & Reset Preferences'
    },
    landing: {
      heroHeadline1: 'The AI legal context layer',
      heroHeadline2: 'for Bali tourism & governance.',
      tripBtn: 'Create Trip Brief',
      contextBtn: 'Verify Viral Claim',
      archTitle: 'Three-Layer Legal Architecture',
      archDesc: 'Every request passes three deterministic stages: automated PII redaction (Stage 01), spatio-temporal filtering at Candi Bentar Gates & Saka Calendar (Stage 02), and Layer-1 citation matching against 42 statutory chunks from 29 Pramana registry documents (Stage 03).',
      openCorpusBtn: 'Explore Legal Corpus',
      card1Title: 'Itinerary Compliance & .ICS Calendar',
      card1Desc: 'Convert travel drafts into statute-referenced compliance checklists, mask guest reservation PII, and export Nyepi calendar alerts (.ics RFC 5545).',
      card1Btn: 'Open Trip Brief Studio',
      card2Title: 'Viral Incident Claim Verification',
      card2Desc: 'Clarify viral tourism controversies with Layer-1 matched statutory citations from Pramana corpus or Layer-2 Abstain. Not a real-time JDIH verification.',
      card2Btn: 'Verify Viral Claim',
      card3Title: 'Deterministic Bali Calendar 2026',
      card3Btn: 'Open Legal Corpus',
      nyepi: 'Nyepi Holy Day (24h Lockdown)',
      ogoh: 'Pengerupukan (Ogoh-ogoh Parade)',
      galungan: 'Galungan Festival',
      kuningan: 'Kuningan Ceremony'
    },
    gate: {
      badge: '03 // ON-SITE COMPLIANCE',
      title: 'Smart Gate',
      titleAccent: 'Pramana',
      subtitle: 'Location-specific compliance cards. Select a destination, listen to audio guidance, and respect sacred cultural grounds.',
      tapNote: 'This page automatically opens when you tap an NFC sticker or scan the QR code at destination entrance gates.',
      openGate: 'Open Gate',
      scanQrBtn: 'Scan QR / Tap NFC',
      allGates: 'All Gates',
      activeChunks: 'active rules',
      historicalChunks: 'historical notes',
      version: 'Rule version',
      aiBrief: 'Executive Summary',
      playAudio: 'Play Spoken Audio Guide',
      stopAudio: 'Stop Audio',
      checks: 'Key Rules on Site',
      legalBasis: 'Verified Legal Basis',
      share: 'Share This Gate',
      copyLink: 'Copy Link',
      copied: 'Link copied.',
      scope: 'Zone Scope'
    },
    trip: {
      badge: '01 // PRE-TRAVEL GUIDANCE',
      title: 'Bali Itinerary Compliance & Sacred Calendar',
      subtitle: 'Verify your itinerary against the 24-hour Nyepi islandwide lockdown, temple dress codes, and foreign tourist levy.',
      inputSection: 'TRAVEL ITINERARY',
      inputLabel: 'Travel Itinerary & Planned Activities',
      placeholder: 'Enter your destinations, temple visits, scooter rentals, or arrival dates...',
      startDate: 'Arrival Date',
      endDate: 'Departure Date',
      travelerType: 'Traveler Category',
      typeInt: 'International Traveler / Foreigner (Love Bali Rp150,000 Levy Applies)',
      typeDom: 'Domestic Traveler / Indonesian Citizen (Levy Exempt)',
      submitBtn: 'Generate Compliance Dossier',
      loadingBtn: 'Checking Legal Corpus...',
      privacyNote: 'Reservation data (emails, passport numbers, booking codes) are automatically masked before analysis.',
      downloadIcs: 'Download Calendar (.ICS)',
      loveBaliLink: 'Official Love Bali Portal (Rp150k) ↗',
      priorityCalendar: 'PRIORITY 01 // CALENDAR ADVISORY',
      priorityLegal: '02 // STATUTORY PROVISIONS',
      articlesLabel: 'ARTICLES',
      copySummary: 'Copy Summary',
      copied: 'Copied',
      abstainTitle: 'No Specific Statutory Conflict Detected',
      abstainDesc: 'Calendar checks were evaluated. Nyepi restrictions or cultural ceremonies, if applicable, are shown above. No statutory citations were forced.',
      presets: [
        {
          label: '01 // Nyepi (18-21 Mar)',
          text: 'Trip to Ubud and Seminyak from 18 to 21 March 2026. Plan to rent motorbike to watch Ogoh-ogoh parade on the road and visit Tanah Lot during Nyepi.'
        },
        {
          label: '02 // Sacred Temple Grounds',
          text: 'Arriving in Denpasar on 10 April. Plan to visit Besakih Temple and Tirta Empul using rental scooter, entering inner sanctum (Utamaning Mandala) in casual resort wear.'
        },
        {
          label: '03 // Motorbike Rental & Remote',
          text: 'Staying 1 month in Canggu while working remotely. Planning to rent a 150cc scooter from local villa without an International Driving Permit and ride up to Mount Batur.'
        }
      ]
    },
    context: {
      badge: '02 // PUBLIC CONTEXT VERIFIER',
      title: 'Viral Incident Context Note & Statutory Grounds',
      subtitle: 'Verify viral posts and tourism controversy claims in Bali with official statutory provisions and objective facts.',
      claimNarrative: 'CLAIM NARRATIVE',
      dualGuard: 'Dual-Layer Guard',
      inputLabel: 'Social Media Caption / Incident Claim',
      placeholder: 'Paste viral post caption, community report, or rule violation claim here...',
      submitBtn: 'Verify Legal Facts',
      loadingBtn: 'Matching Pramana Corpus...',
      protocolL1: 'Layer-1 (corpus): Excerpts are verified against Pramana local corpus, not re-verified real-time against JDIH.',
      protocolL2: 'Layer-2 Abstain: Claims outside statutory scope are rejected automatically without speculation.',
      readyBadge: '01 // NEUTRAL CONTEXT NOTE (READY TO PUBLISH)',
      copyBtn: 'Copy Note',
      copiedBtn: 'Copied',
      framingTitle: 'Sensational Framing Rhetoric Detected',
      citationsBadge: '02 // CORPUS CITATIONS',
      documentsLabel: 'DOCUMENTS',
      exactMatch: 'LAYER-1 EXACT MATCH (CORPUS)',
      abstainTitle: 'No Statutory Grounds Found in Pramana Corpus',
      abstainDesc: 'Synthesis deterministically aborted because no citations passed the corpus relevance threshold. This is not a ruling that the act is lawful.',
      presets: [
        {
          label: '01 // Sacred Temple Tree',
          text: 'Viral video: a foreign tourist climbs a sacred banyan tree inside a Tabanan temple without clothes and screams rudely at locals when warned.'
        },
        {
          label: '02 // Tourist Levy Rp150,000',
          text: 'A video circulates of a foreign visitor arguing at the airport refusing to pay the 150,000 tourist levy at the Love Bali counter, claiming unawareness of the regulation.'
        },
        {
          label: '03 // "Immune to Law" Claim',
          text: 'All foreigners in Bali are completely immune to the law and police do nothing! They should be immediately deported without exception!'
        },
        {
          label: '04 // Abstain Test',
          text: 'An orange cat fell asleep on top of the restaurant cashier desk and demanded fried tuna from the guests.'
        }
      ]
    },
    corpus: {
      badge: '04 // DOCUMENT REGISTRY',
      title: 'Bali Legal Corpus',
      subtitle: 'Browse statutory chunks from registered legal documents of JDIH BPK and Bali Provincial Government.',
      searchPlaceholder: 'Search articles, keywords...',
      loading: 'Loading legal corpus index...'
    }
  }
};
