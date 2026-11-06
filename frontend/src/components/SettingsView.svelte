<script>
  import { i18n, setLanguage, DICT } from '../lib/i18n.svelte.js';

  let t = $derived(DICT[i18n.lang].settings);

  function handleLanguageChange(lang) {
    setLanguage(lang);
  }

  function clearUserData() {
    if (typeof localStorage !== 'undefined') {
      if (confirm(i18n.lang === 'id' ? 'Hapus riwayat gerbang dan setel ulang preferensi?' : 'Clear gate history and reset preferences?')) {
        localStorage.clear();
        setLanguage('id');
        window.location.reload();
      }
    }
  }
</script>

<div class="w-full mx-auto" style="max-width: 1040px;">
  <!-- Header Bar -->
  <section class="px-5 sm:px-10 py-6 sm:py-8 border-b" style="border-color: #cdc9be; background-color: #f3f1eb;">
    <div class="space-y-1">
      <span
        class="font-mono text-[10px] font-bold px-2 py-0.5 tracking-wider uppercase inline-block"
        style="background-color: #0c249c; color: #ffffff; border: 1px solid #0a0a0a;"
      >
        {t.badge}
      </span>
      <h1 class="text-2xl sm:text-3xl font-bold tracking-tight" style="color: #0a0a0a;">
        {t.title}
      </h1>
      <p class="text-xs sm:text-[13px] leading-relaxed max-w-2xl" style="color: #5c5952;">
        {t.subtitle}
      </p>
    </div>
  </section>

  <section class="px-5 sm:px-10 py-6 sm:py-8 space-y-6">
    <!-- CARD 1: Bahasa Tampilan -->
    <div class="brutal-card p-5 sm:p-6 space-y-4" style="background-color: #ffffff;">
      <div class="border-b pb-2.5" style="border-color: #cdc9be;">
        <h2 class="font-mono text-[11px] font-bold uppercase tracking-wider text-[#0c249c]">
          {t.langCardTitle}
        </h2>
        <p class="text-[11px] text-[#5c5952] mt-0.5">{t.langCardSubtitle}</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
        <button
          type="button"
          onclick={() => handleLanguageChange('id')}
          class="brutal-press w-full p-3.5 text-left border cursor-pointer flex items-center justify-between transition-all"
          style={i18n.lang === 'id'
            ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
            : 'background-color: #f3f1eb; color: #0a0a0a; border: 1.5px solid #cdc9be;'}
        >
          <div class="space-y-0.5">
            <span class="font-bold text-xs block"><span class="font-mono text-[10px] font-bold px-1.5 py-0.5 bg-[#0c249c] text-white mr-1">ID</span> {t.idLabel}</span>
            <span class="text-[11px] opacity-80 block">{t.idDesc}</span>
          </div>
          {#if i18n.lang === 'id'}
            <span class="font-mono text-sm font-bold">✓</span>
          {/if}
        </button>

        <button
          type="button"
          onclick={() => handleLanguageChange('en')}
          class="brutal-press w-full p-3.5 text-left border cursor-pointer flex items-center justify-between transition-all"
          style={i18n.lang === 'en'
            ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
            : 'background-color: #f3f1eb; color: #0a0a0a; border: 1.5px solid #cdc9be;'}
        >
          <div class="space-y-0.5">
            <span class="font-bold text-xs block"><span class="font-mono text-[10px] font-bold px-1.5 py-0.5 bg-[#0c249c] text-white mr-1">EN</span> {t.enLabel}</span>
            <span class="text-[11px] opacity-80 block">{t.enDesc}</span>
          </div>
          {#if i18n.lang === 'en'}
            <span class="font-mono text-sm font-bold">✓</span>
          {/if}
        </button>
      </div>
    </div>

    <!-- CARD 2: Storage & Privacy -->
    <div class="brutal-card p-5 sm:p-6 space-y-3" style="background-color: #f3f1eb;">
      <div class="flex flex-wrap items-center justify-between gap-2 border-b pb-2.5" style="border-color: #cdc9be;">
        <div>
          <h2 class="font-mono text-[11px] font-bold uppercase tracking-wider text-[#0a0a0a]">
            {t.storageCardTitle}
          </h2>
          <p class="text-[11px] text-[#5c5952]">{t.storageCardSubtitle}</p>
        </div>
        <button
          type="button"
          onclick={clearUserData}
          class="font-mono text-[11px] font-bold px-3 py-1.5 border border-[#c92a2a] text-[#c92a2a] bg-[#ffffff] hover:bg-[#fff0f0] cursor-pointer"
        >
          {t.clearDataBtn}
        </button>
      </div>
      <p class="text-[11px] text-[#5c5952] leading-relaxed">
        {t.storageDesc}
      </p>
    </div>
  </section>
</div>
