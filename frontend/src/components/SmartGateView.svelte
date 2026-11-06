<script>
    import { fetchZones, fetchTotem, requestTotemBrief } from '../lib/api.svelte.js';
  import { i18n } from '../lib/i18n.svelte.js';
  import EpistemicBadge from './EpistemicBadge.svelte';
  import QrCode from './QrCode.svelte';
  import GateScannerModal from './GateScannerModal.svelte';

  let { zoneId = null, navigate = (path) => {}, onOpenDoc = () => {} } = $props();

  let showScanner = $state(false);

  const UI_TEXT = {
    id: {
      badge: '03 // Phygital Smart Gate',
      title: 'Gerbang Pintar',
      titleAccent: 'Pramana',
      subtitle:
        'Kartu kepatuhan lokasi untuk wisatawan. Pilih gerbang, baca panduan, lalu periksa teks pasal aslinya.',
      loading: 'Memuat kartu gerbang...',
      loadError: 'Gagal memuat kartu gerbang. Pastikan backend berjalan.',
      retry: 'Coba Lagi',
      allGates: 'Semua Gerbang',
      openGate: 'Buka Gerbang',
      tapNote:
        'Halaman ini adalah tujuan URL NFC/QR. Tap tag NTAG213 atau scan QR akan membuka alamat yang sama; tidak memakai Web NFC.',
      zoneCount: 'gerbang',
      activeChunks: 'chunk aktif',
      historicalChunks: 'rujukan historis',
      version: 'Versi aturan',
      aiBrief: 'Panduan Singkat',
      aiBadge: 'AI',
      templateBadge: 'TEMPLATE',
      briefLoading: 'Menyusun panduan singkat...',
      briefError:
        'Ringkasan AI tidak tersedia. Kartu deterministik dan sitasi tetap dapat digunakan.',
      aiNote:
        'Ringkasan AI tidak diverifikasi Layer-1. Sitasi di bawah adalah teks korpus terverifikasi.',
      templateNote:
        'Template deterministik dipakai karena AI tidak tersedia atau output AI ditolak guard sitasi.',
      checks: 'Panduan Utama',
      legalBasis: 'Dasar Hukum Resmi',
      historicalTitle: 'Rujukan Historis',
      historicalNote:
        'Rujukan ini sudah disempurnakan dan tidak boleh diperlakukan sebagai aturan aktif. Ditampilkan untuk transparansi.',
      openSource: 'Buka teks korpus',
      localAck: 'Konfirmasi Lokal',
      ackButton: 'Tandai Sudah Dibaca (tersimpan di perangkat ini saja)',
      ackDone: 'Sudah ditandai di perangkat ini.',
      ackClear: 'Hapus Tanda',
      ackNote:
        'Disimpan hanya di localStorage perangkat ini. Bukan bukti hukum, bukan check-in server, dan tidak dikirim ke mana pun.',
      share: 'Bagikan Gerbang',
      copyLink: 'Salin Link',
      copied: 'Link disalin.',
      copyError: 'Gagal menyalin link.',
      metadata: 'Metadata Gerbang',
      rulesVersion: 'Versi aturan',
      lastVerified: 'Diverifikasi',
      citations: 'Sitasi aktif',
      historical: 'Rujukan historis',
      categoryEntry: 'Pintu Masuk',
      categoryTemple: 'Kawasan Suci',
      categoryPublic: 'Ruang Publik',
      scope: 'Catatan Cakupan',
      back: 'Kembali ke daftar gerbang'
    },
    en: {
      badge: '03 // Phygital Smart Gate',
      title: 'Smart Gate',
      titleAccent: 'Pramana',
      subtitle:
        'Location-specific compliance cards for travellers. Choose a gate, read the guidance, then inspect the original legal text.',
      loading: 'Loading gate card...',
      loadError: 'Failed to load the gate card. Make sure the backend is running.',
      retry: 'Try Again',
      allGates: 'All Gates',
      openGate: 'Open Gate',
      tapNote:
        'This page is the destination of the NFC/QR URL. Tapping an NTAG213 tag or scanning the QR opens the same address; it does not use Web NFC.',
      zoneCount: 'gates',
      activeChunks: 'active chunks',
      historicalChunks: 'historical references',
      version: 'Rules version',
      aiBrief: 'Short Guidance',
      aiBadge: 'AI',
      templateBadge: 'TEMPLATE',
      briefLoading: 'Generating short guidance...',
      briefError:
        'AI summary is unavailable. The deterministic card and citations remain usable.',
      aiNote:
        'The AI summary is not Layer-1 verified. The citations below are verified corpus text.',
      templateNote:
        'A deterministic template is used because AI is unavailable or the AI output was rejected by the citation guard.',
      checks: 'Key Guidance',
      legalBasis: 'Official Legal Basis',
      historicalTitle: 'Historical References',
      historicalNote:
        'These references have been superseded and must not be treated as current rules. They are shown for transparency.',
      openSource: 'Open corpus text',
      localAck: 'Local Acknowledgement',
      ackButton: 'Mark as Read (stored on this device only)',
      ackDone: 'Marked on this device.',
      ackClear: 'Clear Mark',
      ackNote:
        'Stored only in this device\'s localStorage. It is not legal proof, not a server check-in, and is not sent anywhere.',
      share: 'Share Gate',
      copyLink: 'Copy Link',
      copied: 'Link copied.',
      copyError: 'Could not copy the link.',
      metadata: 'Gate Metadata',
      rulesVersion: 'Rules version',
      lastVerified: 'Verified',
      citations: 'Active citations',
      historical: 'Historical references',
      categoryEntry: 'Entry Point',
      categoryTemple: 'Sacred Area',
      categoryPublic: 'Public Space',
      scope: 'Scope Note',
      back: 'Back to gate list'
    }
  };

  const CATEGORY_LABELS = {
    entry_point: { id: 'Pintu Masuk', en: 'Entry Point' },
    temple: { id: 'Kawasan Suci', en: 'Sacred Area' },
    public_area: { id: 'Ruang Publik', en: 'Public Space' }
  };

  let lang = $derived(i18n.lang);
  let zones = $state([]);
  let card = $state(null);
  let loading = $state(true);
  let errorMsg = $state('');
  let brief = $state(null);
  let briefLoading = $state(false);
  let briefError = $state('');  let acknowledged = $state(false);
  let copyStatus = $state('');
  let publicBaseUrl = $state('');
  let requestSeq = 0;
  let briefSeq = 0;

  let t = $derived(UI_TEXT[lang]);

  function categoryLabel(category) {
    return CATEGORY_LABELS[category]?.[lang] || category;
  }

  function statusStyle(citation) {
    if (citation.status === 'Disempurnakan') {
      return 'background-color: #fff3cd; color: #8a3b00; border: 1px solid #8a3b00;';
    }
    if (citation.text_status === 'verbatim') {
      return 'background-color: #e7f0ff; color: #0c249c; border: 1px solid #0c249c;';
    }
    return 'background-color: #ece9e2; color: #5c5952; border: 1px solid #8c877c;';
  }

  function statusLabel(citation) {
    if (citation.status === 'Disempurnakan') return lang === 'en' ? 'HISTORICAL' : 'HISTORIS';
    if (lang === 'en') {
      if (citation.translation_status === 'human-reviewed') return 'HUMAN-REVIEWED (EN)';
      if (citation.translation_status === 'ai-assisted') return 'AI-ASSISTED (EN)';
      if (citation.text_status === 'verbatim') return 'VERBATIM (ID)';
      return 'NON-VERBATIM';
    }
    if (citation.text_status === 'verbatim') return 'VERBATIM';
    return (citation.text_status || 'TEKS').toUpperCase();
  }

  function excerpt(text, length = 220) {
    const value = (text || '').trim();
    return value.length > length ? `${value.slice(0, length)}...` : value;
  }

  function shareBase() {
    if (publicBaseUrl) return publicBaseUrl.replace(/\/$/, '');
    if (typeof window === 'undefined') return '';
    return window.location.origin;
  }

  function shareUrl(id) {
    const base = shareBase();
    return base ? `${base}/totem/${id}` : `/totem/${id}`;
  }

  function isLocalShareUrl() {
    const base = shareBase().toLowerCase();
    return (
      base.includes('://localhost') ||
      base.includes('://127.0.0.1') ||
      base.includes('://[::1]')
    );
  }

  function ackStorageKey(zone) {
    return `pramana.totem.${zone.id}.${zone.rules_version}`;
  }

  function updateAcknowledged() {
    if (!card || typeof localStorage === 'undefined') {
      acknowledged = false;
      return;
    }
    try {
      acknowledged = Boolean(localStorage.getItem(ackStorageKey(card.zone)));
    } catch (error) {
      console.error(error);
      acknowledged = false;
    }
  }

  function acknowledge() {
    if (!card || typeof localStorage === 'undefined') return;
    try {
      localStorage.setItem(ackStorageKey(card.zone), new Date().toISOString());
      acknowledged = true;
    } catch (error) {
      console.error(error);
    }
  }

  function clearAcknowledged() {
    if (!card || typeof localStorage === 'undefined') return;
    try {
      localStorage.removeItem(ackStorageKey(card.zone));
      acknowledged = false;
    } catch (error) {
      console.error(error);
    }
  }

  async function copyShareLink(id) {
    const url = shareUrl(id);
    try {
      await navigator.clipboard.writeText(url);
      copyStatus = t.copied;
    } catch (error) {
      console.error(error);
      copyStatus = t.copyError;
    }
  }

  async function loadZoneList() {
    const seq = ++requestSeq;
    loading = true;
    errorMsg = '';
    try {
      const data = await fetchZones();
      if (seq !== requestSeq) return;
      zones = data.zones || [];
      publicBaseUrl = data.public_base_url || publicBaseUrl;
    } catch (error) {
      if (seq !== requestSeq) return;
      console.error(error);
      errorMsg = t.loadError;
    } finally {
      if (seq === requestSeq) loading = false;
    }
  }

  async function loadCard() {
    if (!zoneId) return;
    const seq = ++requestSeq;
    briefSeq += 1;
    loading = true;
    errorMsg = '';
    card = null;
    brief = null;
    briefError = '';    copyStatus = '';
    try {
      const data = await fetchTotem(zoneId, lang);
      if (seq !== requestSeq) return;
      card = data;
      publicBaseUrl = data.public_base_url || publicBaseUrl;
      updateAcknowledged();
      loadBrief();
    } catch (error) {
      if (seq !== requestSeq) return;
      console.error(error);
      errorMsg = error.message || t.loadError;
    } finally {
      if (seq === requestSeq) loading = false;
    }
  }

  async function loadBrief() {
    if (!zoneId || !card) return;
    const seq = ++briefSeq;
    briefLoading = true;
    briefError = '';
    try {
      const data = await requestTotemBrief(zoneId, lang);
      if (seq !== briefSeq) return;
      brief = data;
    } catch (error) {
      if (seq !== briefSeq) return;
      console.error(error);
      briefError = t.briefError;
    } finally {
      if (seq === briefSeq) briefLoading = false;
    }
  }

  function openZone(id) {
    navigate(`/totem/${id}`);
  }

  $effect(() => {
    const _lang = i18n.lang;
    const _zone = zoneId;
    if (_zone) {
      loadCard();
    } else {
      loadZoneList();
    }
  });
</script>

<div
  class="mx-auto"
  style="max-width: 1360px; width: 100%; border-left: 1px solid #cdc9be; border-right: 1px solid #cdc9be; background-color: #e6e4de; color: #0a0a0a;"
>
  <section
    class="px-5 sm:px-10 py-6 sm:py-8"
    style="border-bottom: 1px solid #cdc9be; background-color: #e6e4de;"
  >
    <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-5">
      <div>
        <div
          class="inline-flex items-center text-xs font-medium mb-3"
          style="background-color: #0c249c; color: #ffffff; padding: 2px; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
        >
          <span
            style="background-color: #dfd6c3; color: #0a0a0a;"
            class="px-2 py-0.5 font-mono text-[10px] font-bold"
          >
            03
          </span>
          <span class="px-3 py-0.5 text-[11px] font-semibold">{t.badge}</span>
        </div>

        <h1 class="opero-h1 text-[30px] sm:text-[42px]">
          {t.title} <span class="opero-serif">{t.titleAccent}</span>
        </h1>
        <p class="mt-3 max-w-3xl text-xs sm:text-sm leading-relaxed" style="color: #3a3935;">
          {t.subtitle}
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onclick={() => showScanner = true}
          style="background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
          class="brutal-press px-3 py-1.5 font-mono text-[11px] font-bold cursor-pointer inline-flex items-center gap-1.5"
        >
          <span>{lang === 'id' ? 'Pindai QR / Tap NFC' : 'Scan QR / Tap NFC'}</span>
        </button>
        {#if zoneId}
          <button
            type="button"
            onclick={() => navigate('/totem')}
            style="background-color: #dfd6c3; color: #0a0a0a; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
            class="brutal-press px-3 py-1.5 font-mono text-[11px] font-bold cursor-pointer"
          >
            ← {t.allGates}
          </button>
        {/if}
      </div>
    </div>
  </section>

  <section class="px-5 sm:px-10 py-6 sm:py-8">
    {#if loading}
      <div class="p-12 text-center font-mono text-xs" style="color: #5c5952;">
        {t.loading}
      </div>
    {:else if errorMsg}
      <div class="brutal-card p-6 space-y-3" style="background-color: #ffffff; border-color: #c92a2a;">
        <p class="text-sm font-medium" style="color: #c92a2a;">{errorMsg}</p>
        <button
          type="button"
          onclick={zoneId ? loadCard : loadZoneList}
          style="background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
          class="brutal-press px-3 py-1.5 font-mono text-[11px] font-semibold cursor-pointer"
        >
          {t.retry}
        </button>
      </div>
    {:else if zoneId && card}
      <div class="space-y-5">
        <div
          class="brutal-card p-5 sm:p-6 space-y-3"
          style="background-color: #dfd6c3;"
        >
          <div class="flex flex-wrap items-center justify-between gap-2">
            <span
              class="font-mono text-[10px] font-bold px-2 py-0.5"
              style="background-color: #0c249c; color: #ffffff; border: 1px solid #0a0a0a;"
            >
              {categoryLabel(card.zone.category)}
            </span>
            <span class="font-mono text-[10px]" style="color: #5c5952;">
              {t.version}: {card.zone.rules_version} · {t.lastVerified} {card.zone.last_verified_date}
            </span>
          </div>
          <h2 class="text-2xl sm:text-3xl font-medium leading-tight" style="color: #0a0a0a;">
            {card.zone.name}
          </h2>
          <p class="text-xs sm:text-sm leading-relaxed" style="color: #3a3935;">
            {card.zone.location_note}
          </p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div class="lg:col-span-7 space-y-5">
            <div class="brutal-card p-5 sm:p-6 space-y-3" style="background-color: #ffffff;">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <span class="font-mono text-[10px] uppercase font-bold" style="color: #0c249c;">
                  {t.aiBrief}
                </span>
                <span
                  class="font-mono text-[10px] font-bold px-2 py-0.5"
                  style={brief?.ai_synthesis_status === 'llm'
                    ? 'background-color: #0c249c; color: #ffffff; border: 1px solid #0a0a0a;'
                    : brief?.ai_synthesis_status === 'unavailable'
                      ? 'background-color: #fff3cd; color: #8a3b00; border: 1px solid #8a3b00;'
                      : brief?.ai_synthesis_status === 'abstain'
                        ? 'background-color: #8a3b00; color: #ffffff; border: 1px solid #0a0a0a;'
                        : 'background-color: #f3f1eb; color: #5c5952; border: 1px solid #8c877c;'}
                >
                  {brief?.ai_synthesis_status === 'llm'
                    ? t.aiBadge
                    : brief?.ai_synthesis_status === 'unavailable'
                      ? 'AI OFF'
                      : brief?.ai_synthesis_status === 'abstain'
                        ? 'ABSTAIN'
                        : t.templateBadge}
                </span>
              </div>

              {#if brief}
                <EpistemicBadge result={brief} />
              {/if}

              {#if briefLoading}
                <p class="text-sm leading-relaxed animate-pulse" style="color: #5c5952;" aria-live="polite">
                  {t.briefLoading}
                </p>
              {:else if brief}
                <p class="text-sm sm:text-[15px] leading-relaxed" style="color: #0a0a0a;" aria-live="polite">
                  {brief.brief}
                </p>
                <p class="font-mono text-[10px] leading-snug" style="color: #8a3b00;">
                  {#if brief.ai_synthesis_status === 'llm'}
                    {t.aiNote}
                  {:else if brief.ai_synthesis_status === 'unavailable'}
                    {lang === 'id'
                      ? 'AI tidak tersedia; checklist dan sitasi terverifikasi tetap dapat digunakan.'
                      : 'AI is unavailable; the verified checklist and citations remain usable.'}
                  {:else if brief.ai_synthesis_status === 'abstain'}
                    {lang === 'id'
                      ? 'AI memilih abstain karena permintaan tidak dapat dijawab aman dari bukti korpus.'
                      : 'AI abstained because the request cannot be safely answered from the corpus evidence.'}
                  {:else}
                    {t.templateNote}
                  {/if}
                </p>
                {#if brief.claims?.length}
                  <p class="font-mono text-[10px]" style="color: #0c249c;">
                    {brief.claims.length} {lang === 'id' ? 'klaim terverifikasi' : 'verified claims'}
                  </p>
                {/if}
              {:else if briefError}
                <p class="text-xs leading-relaxed" style="color: #8a3b00;" aria-live="polite">
                  {briefError}
                </p>
              {/if}
            </div>

            <div class="brutal-card p-5 sm:p-6 space-y-4" style="background-color: #f3f1eb;">
              <div class="flex items-center justify-between border-b pb-2.5" style="border-color: #cdc9be;">
                <span class="font-mono text-[10px] uppercase font-bold" style="color: #0c249c;">
                  {t.checks}
                </span>
                <span class="font-mono text-[10px]" style="color: #5c5952;">
                  {card.zone.practical_checks.length} item
                </span>
              </div>
              <ol class="space-y-3">
                {#each card.zone.practical_checks as check, index}
                  <li class="flex items-start gap-3">
                    <span
                      class="w-6 h-6 shrink-0 flex items-center justify-center font-mono text-[11px] font-bold"
                      style="background-color: #0c249c; color: #ffffff; border: 1px solid #0a0a0a;"
                    >
                      {index + 1}
                    </span>
                    <span class="text-xs sm:text-[13px] leading-relaxed" style="color: #0a0a0a;">
                      {check}
                    </span>
                  </li>
                {/each}
              </ol>
            </div>

            <div
              class="p-4 text-[11px] leading-snug"
              style="background-color: #fff3cd; border: 1px solid #8a3b00; color: #5c2d00;"
            >
              <strong>{t.scope}:</strong> {card.zone.scope_note}
            </div>

            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <h2 class="font-mono text-[11px] uppercase font-bold" style="color: #0c249c;">
                  {t.legalBasis}
                </h2>
                <span class="font-mono text-[10px]" style="color: #5c5952;">
                  {card.citations.length} sitasi
                </span>
              </div>

              {#each card.citations as citation}
                <button
                  type="button"
                  onclick={() => onOpenDoc(citation)}
                  class="brutal-press w-full text-left p-4 space-y-2 cursor-pointer"
                  style="background-color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
                >
                  <div class="flex flex-wrap items-center justify-between gap-2">
                    <span class="font-mono text-[10px] font-bold" style="color: #5c5952;">
                      {citation.pasal}
                    </span>
                    <span
                      class="font-mono text-[10px] font-bold px-2 py-0.5"
                      style={statusStyle(citation)}
                    >
                      {statusLabel(citation)}
                    </span>
                  </div>
                  <h3 class="text-xs sm:text-[13px] font-semibold leading-snug" style="color: #0a0a0a;">
                    {lang === 'en' ? (citation.display_title || citation.title_en || citation.official_doc_title) : citation.official_doc_title}
                  </h3>
                  <p class="text-[11px] leading-relaxed" style="color: #3a3935;">
                    {excerpt(lang === 'en' ? (citation.display_text || citation.text_en || citation.quoted_text) : citation.quoted_text)}
                  </p>
                  <span class="font-mono text-[10px] font-bold" style="color: #0c249c;">
                    {t.openSource} ↗
                  </span>
                </button>
              {/each}
            </div>

            {#if card.historical_citations.length}
              <div
                class="p-4 sm:p-5 space-y-3"
                style="background-color: #fff3cd; border: 1.5px solid #8a3b00;"
              >
                <div class="flex flex-wrap items-center justify-between gap-2">
                  <h2 class="font-mono text-[11px] uppercase font-bold" style="color: #8a3b00;">
                    {t.historicalTitle}
                  </h2>
                  <span class="font-mono text-[10px]" style="color: #8a3b00;">
                    {card.historical_citations.length}
                  </span>
                </div>
                <p class="text-[11px] leading-snug" style="color: #5c2d00;">
                  {t.historicalNote}
                </p>
                {#each card.historical_citations as citation}
                  <button
                    type="button"
                    onclick={() => onOpenDoc(citation)}
                    class="brutal-press w-full text-left p-3 space-y-1 cursor-pointer"
                    style="background-color: #ffffff; border: 1px solid #8a3b00;"
                  >
                    <div class="flex flex-wrap items-center justify-between gap-2">
                      <span class="font-mono text-[10px] font-bold" style="color: #8a3b00;">
                        {citation.pasal}
                      </span>
                      <span
                        class="font-mono text-[10px] font-bold px-2 py-0.5"
                        style={statusStyle(citation)}
                      >
                        {statusLabel(citation)}
                      </span>
                    </div>
                    <h3 class="text-xs font-semibold leading-snug" style="color: #0a0a0a;">
                      {lang === 'en' ? (citation.display_title || citation.title_en || citation.official_doc_title) : citation.official_doc_title}
                    </h3>
                    <p class="font-mono text-[10px]" style="color: #8a3b00;">
                      {lang === 'en' ? (citation.display_status_note || citation.status_note_en || citation.superseded_by || citation.status) : (citation.superseded_by || citation.status)}
                    </p>
                  </button>
                {/each}
              </div>
            {/if}
          </div>

          <div class="lg:col-span-5 space-y-5">
            <div class="brutal-card p-5 space-y-3" style="background-color: #ffffff;">
              <div class="flex items-center justify-between">
                <span class="font-mono text-[10px] uppercase font-bold" style="color: #0c249c;">
                  {t.share}
                </span>
                <span class="font-mono text-[10px]" style="color: #5c5952;">NFC / QR</span>
              </div>
              <div class="flex justify-center">
                <QrCode value={shareUrl(card.zone.id)} size={190} alt={`QR ${card.zone.name}`} />
              </div>
              <p class="font-mono text-[10px] break-all leading-snug" style="color: #5c5952;">
                {shareUrl(card.zone.id)}
              </p>
              {#if isLocalShareUrl()}
                <p class="text-[11px] leading-snug p-2" style="background-color: #fff3cd; border: 1px solid #8a3b00; color: #5c2d00;">
                  {lang === 'id'
                    ? 'QR ini mengarah ke alamat lokal (localhost). Jika dipindai dari HP, halaman tidak akan terbuka. Set PRAMANA_PUBLIC_URL ke alamat publik/LAN frontend, misalnya http://192.168.1.10:5173, lalu muat ulang.'
                    : 'This QR points to a local address (localhost). Scanning it from a phone will not open the page. Set PRAMANA_PUBLIC_URL to the public/LAN frontend address, for example http://192.168.1.10:5173, then reload.'}
                </p>
              {/if}
              <button
                type="button"
                onclick={() => copyShareLink(card.zone.id)}
                class="brutal-press w-full px-3 py-2 font-mono text-[11px] font-bold cursor-pointer"
                style="background-color: #dfd6c3; color: #0a0a0a; border: 1.5px solid #0a0a0a;"
              >
                {t.copyLink}
              </button>
              {#if copyStatus}
                <p class="font-mono text-[10px]" style="color: #0c249c;">{copyStatus}</p>
              {/if}
            </div>

            <div class="brutal-card p-5 space-y-3" style="background-color: #ffffff;">
              <span class="font-mono text-[10px] uppercase font-bold block" style="color: #0c249c;">
                {t.localAck}
              </span>
              {#if acknowledged}
                <p class="text-xs font-semibold" style="color: #2b7a3d;">✓ {t.ackDone}</p>
                <button
                  type="button"
                  onclick={clearAcknowledged}
                  class="brutal-press w-full px-3 py-2 font-mono text-[10px] font-bold cursor-pointer"
                  style="background-color: #ffffff; color: #8a3b00; border: 1px solid #8a3b00;"
                >
                  {t.ackClear}
                </button>
              {:else}
                <button
                  type="button"
                  onclick={acknowledge}
                  class="brutal-press w-full px-3 py-2.5 font-mono text-[11px] font-bold cursor-pointer"
                  style="background-color: #dfd6c3; color: #0a0a0a; border: 1.5px solid #0a0a0a;"
                >
                  {t.ackButton}
                </button>
              {/if}
              <p class="text-[10px] leading-snug" style="color: #5c5952;">{t.ackNote}</p>
            </div>

            <div class="brutal-card p-5 space-y-2" style="background-color: #f3f1eb;">
              <span class="font-mono text-[10px] uppercase font-bold block" style="color: #0c249c;">
                {t.metadata}
              </span>
              <div class="font-mono text-[10px] space-y-1" style="color: #3a3935;">
                <p>{t.rulesVersion}: {card.zone.rules_version}</p>
                <p>{t.lastVerified}: {card.zone.last_verified_date}</p>
                <p>{t.citations}: {card.citations.length}</p>
                <p>{t.historical}: {card.historical_citations.length}</p>
                <p>AI claims: {brief?.claims?.length || 0}</p>
                <p>AI status: {brief?.ai_synthesis_status || '-'}</p>
                <p>ID: {card.zone.id}</p>
              </div>
            </div>

            <div
              class="p-4 text-[10px] leading-relaxed"
              style="background-color: #ffffff; border: 1px solid #cdc9be; color: #5c5952;"
            >
              {card.disclaimer}
            </div>
          </div>
        </div>
      </div>
    {:else}
      <div class="space-y-5">
        <div
          class="p-4 sm:p-5 flex flex-wrap items-center justify-between gap-4"
          style="background-color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
        >
          <div class="space-y-1 max-w-xl">
            <span class="font-mono text-[10px] font-bold uppercase tracking-wider" style="color: #0c249c;">
              INTEGRASI FISIK LAPANGAN (NFC &amp; QR)
            </span>
            <p class="text-xs leading-relaxed text-[#0a0a0a]">
              <strong>{t.tapNote}</strong>
            </p>
          </div>
          <button
            type="button"
            onclick={() => { showScanner = true; }}
            class="brutal-press px-4 py-2.5 font-mono text-xs font-bold cursor-pointer inline-flex items-center gap-2"
            style="background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
          >
            <span>{lang === 'id' ? 'Buka Kamera / Simulasi Tap NFC' : 'Open Camera / Tap NFC Sim'}</span>
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          {#each zones as zone}
            <div class="brutal-card p-5 space-y-4" style="background-color: #f3f1eb;">
              <div class="flex items-center justify-between gap-2">
                <span
                  class="font-mono text-[10px] font-bold px-2 py-0.5"
                  style="background-color: #0c249c; color: #ffffff; border: 1px solid #0a0a0a;"
                >
                  {categoryLabel(zone.category)}
                </span>
                <span class="font-mono text-[10px]" style="color: #5c5952;">
                  {zone.rules_version}
                </span>
              </div>

              <h2 class="text-xl font-medium leading-tight" style="color: #0a0a0a;">
                {zone.name[lang]}
              </h2>
              <p class="text-xs leading-relaxed" style="color: #3a3935;">
                {zone.location_note[lang]}
              </p>

              <div class="flex items-center gap-4">
                <QrCode value={shareUrl(zone.id)} size={150} alt={`QR ${zone.name.en}`} />
                <div class="font-mono text-[10px] space-y-1" style="color: #5c5952;">
                  <p>{zone.regulation_ids.length} {t.activeChunks}</p>
                  {#if zone.historical_regulation_ids.length}
                    <p>{zone.historical_regulation_ids.length} {t.historicalChunks}</p>
                  {/if}
                  <p>{t.version}: {zone.rules_version}</p>
                </div>
              </div>

              <button
                type="button"
                onclick={() => openZone(zone.id)}
                class="brutal-press w-full px-4 py-2.5 font-mono text-[11px] font-bold cursor-pointer"
                style="background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
              >
                {t.openGate} →
              </button>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </section>

  <GateScannerModal
    isOpen={showScanner}
    onClose={() => { showScanner = false; }}
    onScan={(scannedZoneId) => {
      showScanner = false;
      openZone(scannedZoneId);
    }}
  />
</div>
