"use strict";
// Kanal Stüdyosu arayüzü. Durum /api/durum'dan okunur; ekran yalnızca durum değiştiğinde yeniden çizilir.

const $ = (s, k = document) => k.querySelector(s);
const kacir = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

let D = null;
let imza = "";

async function api(yol, govde) {
  const r = await fetch(yol, {
    method: govde === undefined ? "GET" : "POST",
    headers: { "X-App-Token": window.TOKEN, "Content-Type": "application/json" },
    body: govde === undefined ? undefined : JSON.stringify(govde),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.hata || "İşlem yapılamadı");
  return j;
}

function bildir(m) {
  const b = $("#bildirim");
  b.textContent = m; b.hidden = false;
  clearTimeout(bildir.t); bildir.t = setTimeout(() => (b.hidden = true), 5000);
}

async function yap(fn) {
  try { await fn(); await yenile(true); } catch (e) { bildir(e.message); }
}

async function kopyala(metin) {
  try { await navigator.clipboard.writeText(metin); bildir("Kopyalandı."); }
  catch { const t = document.createElement("textarea"); t.value = metin; document.body.appendChild(t); t.select(); document.execCommand("copy"); t.remove(); bildir("Kopyalandı."); }
}

// --- değer yolları (ör. "uzunluk.hedef_kelime.0") ---------------------------

function al(o, yol) { return yol.split(".").reduce((x, p) => (x == null ? undefined : x[p]), o); }
function koy(o, yol, v) {
  const p = yol.split(".");
  let x = o;
  p.slice(0, -1).forEach((k, i) => { if (x[k] == null) x[k] = /^\d+$/.test(p[i + 1]) ? [] : {}; x = x[k]; });
  x[p[p.length - 1]] = v;
}
const kopya = (o) => JSON.parse(JSON.stringify(o));

function kisaltmaOner(ad) {
  const tr = { ç: "c", ğ: "g", ı: "i", İ: "i", ö: "o", ş: "s", ü: "u", â: "a", î: "i", û: "u" };
  return ad.toLowerCase().replace(/[çğıİöşüâîû]/g, (c) => tr[c] || c).normalize("NFD").replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 31);
}

// --- kanal formu (sihirbaz ve ayarlar aynı alanları kullanır) ----------------

const IS_ADLARI = { hazir: "Hazır metin", konu: "1 Konu", arastirma: "2 Araştırma", senaryo: "3 Senaryo (TR)", ceviri: "4 Hedef dil", sahne: "5 Sahne paketi", paketleme: "6 Paketleme", bolumler: "6 Bölümler", defter: "Defter yenileme", uyum: "Sahne–görsel uyumu", rapor: "Rapor özeti", odak: "Odak noktası" };

function bolumler() {
  const diller = Object.entries(D.diller);
  return [
    { baslik: "1 · Kimlik", alanlar: [
      { yol: "ad", etiket: "Kanal adı", tur: "metin", ornek: "ör. Bilim Kahvesi" },
      { yol: "kisaltma", etiket: "Kısaltma (klasör adı)", tur: "metin", yalnizEkle: true, aciklama: "Kanallar/ altındaki klasörün adı. Küçük harf, rakam ve tire. Sonradan değişmez." },
      { yol: "kod_oneki", etiket: "Video kodu öneki", tur: "metin", ornek: "ör. BK", aciklama: "Videolar ÖNEK-01, ÖNEK-02… diye adlanır. İlk video üretildikten sonra değişmez." },
      { yol: "kod_hane", etiket: "Numara hanesi", tur: "secim", secenekler: [[2, "2 (01, 02…)"], [3, "3 (001, 002…)"]], gelismis: true },
    ] },
    { baslik: "2 · Dil ve uzunluk", alanlar: [
      { yol: "dil.hedef", etiket: "Videonun dili (hedef dil)", tur: "secim", secenekler: diller, aciklama: "Konu, araştırma ve senaryo Türkçe yazılır; senaryo bu dilde yeniden yazılır, bu dilde seslendirilir. Türkçe seçilirse 4. aşama atlanır." },
      { yol: "uzunluk.hedef_dk", etiket: "Hedef süre (dk)", tur: "sayi" },
      { tur: "kelime_bilgi" },
      { yol: "uzunluk.kelime_otomatik", etiket: "Kelime sayısını uygulama hesaplasın (önerilir)", tur: "onay", gelismis: true, aciklama: "Süre × dilin konuşma hızı; her videodan sonra gerçek ses süresiyle düzelir. Kapatırsan aşağıdaki sayılar kullanılır." },
      { cift: [{ yol: "uzunluk.calisma_kelime.0", etiket: "Türkçe senaryo · en az kelime", tur: "sayi" }, { yol: "uzunluk.calisma_kelime.1", etiket: "en çok kelime", tur: "sayi" }], gelismis: true, elleKelime: true },
      { cift: [{ yol: "uzunluk.hedef_kelime.0", etiket: "Hedef dil senaryo · en az kelime", tur: "sayi" }, { yol: "uzunluk.hedef_kelime.1", etiket: "en çok kelime", tur: "sayi" }], gelismis: true, elleKelime: true },
      { cift: [{ yol: "uzunluk.kart_karakter", etiket: "Konu kartı en fazla karakter", tur: "sayi" }, { yol: "uzunluk.hook_esigi", etiket: "Hook puanı eşiği (/10)", tur: "sayi" }], gelismis: true },
    ] },
    { baslik: "3 · Ses (ElevenLabs)", alanlar: [
      { cift: [{ yol: "ses.voice_id", etiket: "Ses kimliği (voice_id)", tur: "metin" }, { yol: "ses.voice_name", etiket: "Ses adı", tur: "metin" }], aciklama: "ElevenLabs'te sesin sayfasındaki kimlik. Üretim başlamadan önce gerekli." },
      { cift: [{ yol: "ses.model_id", etiket: "Model", tur: "metin" }, { yol: "ses.language_code", etiket: "Dil kodu", tur: "metin" }], gelismis: true },
      { cift: [{ yol: "ses.stability", etiket: "Stability (0–1)", tur: "sayi" }, { yol: "ses.similarity_boost", etiket: "Similarity (0–1)", tur: "sayi" }], gelismis: true },
      { cift: [{ yol: "ses.style", etiket: "Style (0–1)", tur: "sayi" }, { yol: "ses.speed", etiket: "Speed (0,7–1,2)", tur: "sayi" }], gelismis: true },
      { cift: [{ yol: "ses.output_format", etiket: "Çıkış biçimi", tur: "metin" }, { yol: "ses.use_speaker_boost", etiket: "Speaker boost", tur: "onay" }], gelismis: true },
    ] },
    { baslik: "4 · Görsel", alanlar: [
      { yol: "gorsel.karakter", etiket: "Flow karakter etiketi", tur: "metin", ornek: "ör. @Mira (yoksa boş)", aciklama: "Karakterli sahnelerin promptu bununla başlar." },
      { yol: "gorsel.kurallar", etiket: "Kanalın görsel kuralları", tur: "uzun", aciklama: "Son kontroldeki sahne–görsel uyum denetimine verilir (ör. 'çocuk figürü yok; yetişkinler arkadan')." },
      { yol: "gorsel.ifade_notu", etiket: "Karakterin yüz ifadesi notu (isteğe bağlı)", tur: "uzun", aciklama: "Sahne paketi aşamasına eklenir." },
      { yol: "gorsel.yasakli", etiket: "Flow yasaklı kelimeler", tur: "liste", aciklama: "Virgülle ayır. Görsel promptlarında geçerse kod kontrolü hata verir." },
      { yol: "gorsel.oran", etiket: "Görsel oranı", tur: "secim", secenekler: [["16:9", "16:9 yatay"], ["9:16", "9:16 dikey"]] },
      { yol: "gorsel.izinli_olumsuz", etiket: "İzinli olumsuzlamalar ('no …')", tur: "liste", gelismis: true },
      { yol: "gorsel.flow_model", etiket: "Flow modeli", tur: "metin", gelismis: true },
    ] },
    { baslik: "5 · Etiketler", alanlar: [
      { yol: "etiketler.senaryo.karakter", etiket: "Karakter sahnesi etiketi", tur: "metin", aciklama: "Senaryoda karakterli paragrafların başına köşeli parantezle yazılır, ör. [MIRA]." },
      { cift: [{ yol: "etiketler.senaryo.metafor", etiket: "Metafor sahnesi etiketi", tur: "metin" }, { yol: "etiketler.senaryo.sema", etiket: "Şema sahnesi etiketi", tur: "metin" }], gelismis: true },
      { yol: "etiketler.senaryo.ilk30", etiket: "İlk 30 sn etiketi", tur: "metin", gelismis: true },
      { yol: "etiketler.ses", etiket: "İzinli ses tag'leri (ElevenLabs)", tur: "liste", gelismis: true },
      { cift: [{ yol: "etiketler.ses_sinir", etiket: "Tag sınırları", tur: "sinir", aciklama: "ör. whispers:2" }, { yol: "etiketler.tag_orani", etiket: "Tag'li paragraf oranı üst sınırı (%)", tur: "sayi" }], gelismis: true },
      { yol: "hassas_kelimeler", etiket: "Hassas kelimeler (başlık, açıklama, ilk 30 sn)", tur: "liste", aciklama: "Hedef dilde, virgülle. Kelime kökü yazılabilir (ör. depress, trauma)." },
    ] },
    { baslik: "6 · Montaj", alanlar: [
      { yol: "montaj.muzik", etiket: "Arka plan müziği", tur: "onay", aciklama: "Müzik dosyaları kanal klasöründe Varliklar/Muzik'e konur; klasör boşsa video müziksiz olur." },
      { yol: "montaj.muzik_lufs", etiket: "Müzik seviyesi (LUFS)", tur: "sayi", gelismis: true },
      { yol: "montaj.son_ekran_sn", etiket: "Son ekran süresi (sn)", tur: "sayi" },
      { yol: "montaj.maskot.dosyalar", etiket: "Maskot dosyaları (Varliklar/Maskot içindeki adlar)", tur: "liste", aciklama: "Maskot yoksa boş bırak." },
      { yol: "montaj.maskot.sira", etiket: "Maskot sırası", tur: "liste", aciklama: "ör. M1, M2, M1, M2 (1. dosya = M1)." },
      { yol: "montaj.altyazi.yazi_tipi", etiket: "Altyazı yazı tipi", tur: "metin" },
      { cift: [{ yol: "montaj.altyazi.yazi", etiket: "Altyazı yazı rengi", tur: "renk" }, { yol: "montaj.altyazi.kutu", etiket: "Altyazı kutu rengi", tur: "renk" }] },
      { cift: [{ yol: "montaj.altyazi.boyut", etiket: "Altyazı boyutu", tur: "sayi" }, { yol: "montaj.altyazi.kutu_opaklik", etiket: "Kutu opaklığı (0–1)", tur: "sayi" }], gelismis: true },
      { yol: "imza", etiket: "Kapanış imzası (isteğe bağlı)", tur: "metin", ornek: "ör. …e insieme, ti ritroverai.", aciklama: "Her videonun sonunda değişmeden tekrar eden tek satır. Açılış–Kapanış Defteri'nde 'tek sabit satır' olarak geçer." },
      { yol: "kalip_sayaclari", etiket: "Kalıp sayaçları (isteğe bağlı)", tur: "kalip", aciklama: "Açılış–Kapanış Defteri'nde sayılan tekrar kalıpları. Her satıra bir tane: ad: desen (ör. soru_acilis: ^Hai mai). Desen düzenli ifadedir.", gelismis: true },
    ] },
    { baslik: "7 · Onaylar", alanlar: [
      { aciklama: "İşaretli aşamalarda üretim durur ve onayını bekler; işaretsiz aşama kod kontrolleri temizse beklemeden geçer, sorun varsa yine durur. ONAY 1 (konu) ve ONAY 3 (Türkçe senaryo) her zaman istenir. Sahne paketi onaysızdır. Bunlar varsayılandır; her üretimin başında o üretim için değiştirilebilir." },
      ...[["arastirma", "ONAY 2 · Araştırma"], ["ceviri", "ONAY 4 · Hedef dil"], ["paketleme", "ONAY 5 · Paketleme"]]
        .map(([k, e]) => ({ yol: "onaylar." + k, etiket: e, tur: "onay" })),
    ] },
    { baslik: "8 · Modeller ve bütçe", alanlar: [
      { tur: "isler", gelismis: true },
      { yol: "butce.video_usd", etiket: "Video başına bütçe ($)", tur: "sayi" },
    ] },
  ];
}

// Kelime aralığı: süre × konuşma hızı (kanallar.kelime_araligi ile aynı hesap; burada yalnız göstermek için).
function kelimeAraligi(k, dil) {
  const olc = (((k.uzunluk || {}).hiz_olcum || {})[dil] || []).map((x) => x && x.hiz).filter(Number.isFinite).sort((a, b) => a - b);
  const n = olc.length;
  const ort = n ? (n % 2 ? olc[(n - 1) / 2] : (olc[n / 2 - 1] + olc[n / 2]) / 2) : (D.konusma_hizi[dil] || 150);
  const sp = Number((k.ses || {}).speed), hiz = ort * (sp >= 0.5 && sp <= 2 ? sp : 1);
  const orta = hiz * Number(k.uzunluk.hedef_dk), onluk = (x) => Math.floor(x / 10 + 0.5) * 10;
  return { aralik: [onluk(orta * (1 - D.kelime_payi)), onluk(orta * (1 + D.kelime_payi))], hiz: Math.round(hiz), olcum: n };
}

function kelimeBilgi(k) {
  const u = k.uzunluk || {}, hedef = (k.dil || {}).hedef || "tr", dilAdi = D.diller[hedef] || hedef;
  if (!u.kelime_otomatik) return `Elle ayarlı: Türkçe senaryo ${(u.calisma_kelime || []).join("–")} kelime` + (hedef === "tr" ? "" : ` · ${dilAdi} ${(u.hedef_kelime || []).join("–")} kelime`) + ". İstersen Gelişmiş'ten otomatik hesaba geçebilirsin.";
  const dk = Number(u.hedef_dk);
  if (!(dk >= 1 && dk <= 60)) return "Süreyi yazınca uygulama hesaplar.";
  const tr = kelimeAraligi(k, "tr"), hd = kelimeAraligi(k, hedef);
  const kaynak = (x) => x.olcum ? `${x.olcum} videonun gerçek ses süresinden` : "dilin ortalama hızından";
  return `Uygulama hesaplar: Türkçe senaryo ~${tr.aralik.join("–")} kelime (dakikada ~${tr.hiz}, ${kaynak(tr)})` +
    (hedef === "tr" ? "" : ` · ${dilAdi} senaryo ~${hd.aralik.join("–")} kelime (dakikada ~${hd.hiz}, ${kaynak(hd)})`) +
    ". Her videodan sonra gerçek ses süresiyle düzelir.";
}

function alanYollari(a) { return a.cift ? a.cift.map((x) => x.yol) : [a.yol]; }

function alanBul(yol) {
  for (const b of bolumler()) for (const a of b.alanlar) {
    if (a.yol === yol) return { ...a, gelismis: false };
    for (const x of a.cift || []) if (x.yol === yol) return { ...x };
  }
  return null;
}

// Bir bölümün alanları: gelişmiş olanlar katlanmış "Gelişmiş" kutusunda (DOM'da kalır, formOku okur).
function bolumHtml(b, k, mod, haric = new Set()) {
  const alanlar = b.alanlar.map((a) => (a.cift ? { ...a, cift: a.cift.filter((x) => !haric.has(x.yol)) } : a))
    .filter((a) => (a.cift ? a.cift.length : !(a.yol && haric.has(a.yol)) && !(a.tur === "kelime_bilgi" && haric.has("kelime_bilgi"))));
  const normal = alanlar.filter((a) => !a.gelismis), ileri = alanlar.filter((a) => a.gelismis);
  return normal.map((a) => alanHtml(a, k, mod)).join("") +
    (ileri.length ? `<details class="gelismis"><summary>Gelişmiş</summary>${ileri.map((a) => alanHtml(a, k, mod)).join("")}</details>` : "");
}

function alanHtml(a, k, mod) {
  if (a.tur === "kelime_bilgi") return `<div class="alan"><label>Kelime sayısı</label><p class="kucuk" id="kelime-bilgi">${kacir(kelimeBilgi(k))}</p></div>`;
  if (a.cift) return `<div class="alan-cift${a.elleKelime ? " elle-kelime" : ""}" ${a.elleKelime && (k.uzunluk || {}).kelime_otomatik ? "hidden" : ""}>${a.cift.map((x) => alanHtml(x, k, mod)).join("")}</div>${a.aciklama ? `<p class="alan-aciklama">${kacir(a.aciklama)}</p>` : ""}`;
  if (a.tur === "isler") return islerHtml(k);
  if (!a.yol) return `<p class="alan-aciklama">${kacir(a.aciklama)}</p>`;
  if (a.yalnizEkle && mod !== "ekle") return `<label>${kacir(a.etiket)}</label><p><b>${kacir(al(k, a.yol))}</b></p>`;
  const v = al(k, a.yol);
  const id = `a-${a.yol.replace(/\./g, "-")}`;
  let girdi;
  if (a.tur === "secim") girdi = `<select id="${id}" data-yol="${a.yol}" data-tur="secim">${a.secenekler.map(([d, e]) => `<option value="${kacir(d)}" ${String(d) === String(v) ? "selected" : ""}>${kacir(e)}</option>`).join("")}</select>`;
  else if (a.tur === "onay") girdi = `<input type="checkbox" id="${id}" data-yol="${a.yol}" data-tur="onay" ${v ? "checked" : ""}>`;
  else if (a.tur === "uzun") girdi = `<textarea id="${id}" data-yol="${a.yol}" data-tur="metin">${kacir(v)}</textarea>`;
  else if (a.tur === "liste") girdi = `<textarea id="${id}" data-yol="${a.yol}" data-tur="liste" style="min-height:60px">${kacir((v || []).join(", "))}</textarea>`;
  else if (a.tur === "kalip") girdi = `<textarea id="${id}" data-yol="${a.yol}" data-tur="kalip" style="min-height:70px" placeholder="ad: desen">${kacir(Object.entries(v || {}).map(([x, y]) => `${x}: ${y}`).join("\n"))}</textarea>`;
  else if (a.tur === "sinir") girdi = `<input type="text" id="${id}" data-yol="${a.yol}" data-tur="sinir" value="${kacir(Object.entries(v || {}).map(([x, y]) => `${x}:${y}`).join(", "))}">`;
  else if (a.tur === "renk") girdi = `<div class="satir"><input type="color" id="${id}" data-yol="${a.yol}" data-tur="metin" value="${kacir(v)}"><span class="kucuk soluk">${kacir(v)}</span></div>`;
  else girdi = `<input type="${a.tur === "sayi" ? "number" : "text"}" step="any" id="${id}" data-yol="${a.yol}" data-tur="${a.tur}" value="${kacir(v ?? "")}" placeholder="${kacir(a.ornek || "")}">`;
  const neden = F && F.eksikNeden && F.eksikNeden[a.yol];
  return `<div class="alan${neden ? " eksik-alan" : ""}">` + (neden ? `<p class="alan-aciklama hata-yazi">Dosyada: ${kacir(neden)}</p>` : "") + (a.tur === "onay"
    ? `<label class="satir" style="font-weight:500">${girdi} ${kacir(a.etiket)}</label>${a.aciklama ? `<p class="alan-aciklama">${kacir(a.aciklama)}</p>` : ""}`
    : `<label for="${id}">${kacir(a.etiket)}</label>${girdi}${a.aciklama ? `<p class="alan-aciklama">${kacir(a.aciklama)}</p>` : ""}`) + `</div>`;
}

function islerHtml(k) {
  const modeller = Object.entries(D.ayarlar.modeller).filter(([m]) => ["claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-4-5"].includes(m));
  const satirlar = Object.entries(k.isler).filter(([i]) => !i.endsWith("_yedek")).map(([i, v]) => `<tr><td>${kacir(IS_ADLARI[i] || i)}</td>
    <td><select data-yol="isler.${i}.model" data-tur="secim">${modeller.map(([m, ad]) => `<option value="${m}" ${m === v.model ? "selected" : ""}>${kacir(ad)}</option>`).join("")}</select></td>
    <td><select data-yol="isler.${i}.efor" data-tur="secim"><option value="medium" ${v.efor !== "low" && v.efor !== "high" ? "selected" : ""}>Medium</option><option value="low" ${v.efor === "low" ? "selected" : ""}>Low</option><option value="high" ${v.efor === "high" ? "selected" : ""}>High</option></select></td></tr>`).join("");
  return `<div class="tablo-kap"><table><thead><tr><th>İş</th><th>Model</th><th>Efor</th></tr></thead><tbody>${satirlar}</tbody></table></div>
    <p class="alan-aciklama">Haiku'da efor ayarı kullanılmaz. Model değiştirmek maliyeti etkiler.</p>`;
}

function formOku(kapsayici, k) {
  kapsayici.querySelectorAll("[data-yol]").forEach((el) => {
    const t = el.dataset.tur, yol = el.dataset.yol;
    let v;
    if (t === "onay") v = el.checked;
    else if (t === "sayi") v = el.value === "" ? null : Number(String(el.value).replace(",", "."));
    else if (t === "liste") v = el.value.split(/[,\n]/).map((x) => x.trim()).filter(Boolean);
    else if (t === "sinir") v = Object.fromEntries(el.value.split(",").map((x) => x.split(":").map((y) => y.trim())).filter((x) => x[0]).map(([a, b]) => [a, Number(b)]));
    else if (t === "kalip") v = Object.fromEntries(el.value.split("\n").map((x) => x.trim()).filter((x) => x.includes(":")).map((x) => { const i = x.indexOf(":"); return [x.slice(0, i).trim(), x.slice(i + 1).trim()]; }).filter(([a, b]) => a && b));
    else if (t === "secim" && yol === "kod_hane") v = Number(el.value);
    else v = el.value.trim();
    koy(k, yol, v);
  });
  for (const v of Object.values(k.isler || {})) if (v.model === "claude-haiku-4-5") v.efor = null;
  return k;
}

// Sihirbaz durumu
let F = null;  // {mod: "ekle"|"ayarlar", adim, kanal, kaynak, klasor, hatalar, uyarilar}

function kanalEkleAc() {
  const k = kopya(D.kanal_varsayilan);
  F = { mod: "ekle", yol: "secim", adim: 0, kanal: k, kaynak: "sablon", klasor: "", hatalar: [], uyarilar: [] };
  kanalFormuCiz(); $("#kanal-pencere").showModal();
}

// Dosyayla ekleme: ekranda gösterilen, uygulamada seçilen alanlar (gerisi "diğer ayarlar"da).
const DOSYA_SECILEN = ["ad", "dil.hedef", "uzunluk.hedef_dk", "kisaltma", "kod_oneki", "ses.voice_id", "ses.voice_name", "montaj.muzik", "montaj.maskot.dosyalar",
  "montaj.maskot.sira", "onaylar.arastirma", "onaylar.ceviri", "onaylar.paketleme"];

function dosyaEkranlari() {
  const notlar = (F.hatalar.length ? `<ul class="notlar hata">${F.hatalar.map((x) => `<li>${kacir(x)}</li>`).join("")}</ul>` : "") +
    (F.uyarilar.length ? `<ul class="notlar uyari">${F.uyarilar.map((x) => `<li>${kacir(x)}</li>`).join("")}</ul>` : "");
  if (F.yol === "secim") return `<h2 style="margin-top:0">Kanal ekle</h2>
    <div class="secim-kartlari">
      <button type="button" class="secim-karti" data-eylem="kf-yol" data-secim="dosya"><b>Dosyayla ekle <span class="oneri">önerilen</span></b>
        <span class="soluk kucuk">Şablonu bir yapay zekaya (Claude, ChatGPT…) doldurt, buraya yapıştır. Kanal bilgileri ve anayasa birlikte gelir; eksik kalanları uygulama gösterir.</span></button>
      <button type="button" class="secim-karti" data-eylem="kf-yol" data-secim="elle"><b>Elle doldur</b>
        <span class="soluk kucuk">Adım adım form. Anayasayı sonra Kanal dosyaları › 01_Anayasa.md'den doldurursun.</span></button>
    </div>
    <div class="satir" style="margin-top:18px;justify-content:flex-start"><button class="dugme" data-eylem="kf-kapat">Vazgeç</button></div>`;
  if (!F.okundu) return `<h2 style="margin-top:0">Kanal ekle · dosyayla</h2>
    <ol class="kucuk" style="padding-left:20px">
      <li><b>Şablonu kopyala</b> (aynı şablon kurulum klasöründe <code>Yeni_Kanal_Sablonu.md</code> olarak da duruyor).</li>
      <li>Bir yapay zekaya yapıştır, altına kanalını birkaç cümleyle anlat: konusu, kimin için, hangi dilde, kaç dakika, anlatıcı ve görsel tarz.</li>
      <li>Doldurduğu metni aşağıya yapıştır ya da dosyayı seç.</li></ol>
    <div class="satir"><button type="button" class="dugme" data-eylem="kf-sablon-kopyala">Şablonu kopyala</button>
      <label class="dugme">Dosya seç<input type="file" id="kf-dosya" accept=".md,.txt,text/plain,text/markdown" hidden></label></div>
    <textarea id="kf-metin" class="dosya-duzenle" style="min-height:260px" placeholder="Doldurulmuş kanal dosyasını buraya yapıştır">${kacir(F.metin || "")}</textarea>
    ${notlar}
    <div class="satir" style="margin-top:14px;justify-content:space-between"><button class="dugme" data-eylem="kf-yol" data-secim="secim">Geri</button>
      <button class="dugme ana-dugme" data-eylem="kf-dosya-oku">Oku ve devam et</button></div>`;
  const k = F.kanal, b = bolumler();
  const eksikYollar = F.eksik.map((e) => e.yol);
  const gosterilen = new Set([...eksikYollar, ...DOSYA_SECILEN, "kelime_bilgi"]);
  const alan = (yol) => { const a = alanBul(yol); return a ? alanHtml(a, k, "ekle") : ""; };
  const anayasa = F.anayasa ? (F.doldur ? `var, ${F.doldur} yer doldurulmamış (sonra tamamlanabilir)` : "var, tam") : "yok (genel şablondan başlar)";
  return `<h2 style="margin-top:0">Kanal ekle · dosyayla</h2>
    <p class="kucuk">Dosyadan <b>${F.okunan}</b> bilgi okundu · Anayasa: <b>${kacir(anayasa)}</b></p>
    ${F.eksik.length ? `<h3 class="bolum-baslik">Eksik ya da hatalı (${F.eksik.length})</h3>` + eksikYollar.map(alan).join("") : ""}
    <h3 class="bolum-baslik">Kanal</h3>
    ${["ad", "dil.hedef", "uzunluk.hedef_dk"].filter((y) => !eksikYollar.includes(y)).map(alan).join("")}
    <div class="alan"><label>Kelime sayısı</label><p class="kucuk" id="kelime-bilgi">${kacir(kelimeBilgi(k))}</p></div>
    ${["kisaltma", "kod_oneki"].filter((y) => !eksikYollar.includes(y)).map(alan).join("")}
    <h3 class="bolum-baslik">Uygulamada seçilenler</h3>
    <div class="alan-cift">${alan("ses.voice_id")}${alan("ses.voice_name")}</div>
    <p class="alan-aciklama">ElevenLabs'te sesin sayfasındaki kimlik. Şimdi boş bırakabilirsin; üretim başlamadan önce gerekli.</p>
    ${["montaj.muzik", "montaj.maskot.dosyalar", "montaj.maskot.sira"].map(alan).join("")}
    <p class="alan-aciklama" style="margin-top:10px">Onay: işaretli aşamalarda üretim durup onayını bekler (ONAY 1 ve 3 her zaman istenir).</p>
    ${["onaylar.arastirma", "onaylar.ceviri", "onaylar.paketleme"].map(alan).join("")}
    <details class="gelismis"><summary>Dosyadan gelen diğer ayarlar ve gelişmiş ayarlar</summary>
      ${b.map((x) => { const h = bolumHtml(x, k, "ekle", gosterilen); return h ? `<h4 class="bolum-baslik">${kacir(x.baslik)}</h4>${h}` : ""; }).join("")}
    </details>
    ${notlar}
    <div class="satir" style="margin-top:18px;justify-content:space-between">
      <button class="dugme" data-eylem="kf-dosya-geri">Geri</button>
      <button class="dugme ana-dugme" data-eylem="kf-kaydet">Kanalı oluştur</button></div>`;
}

async function kfDosyaOku() {
  F.metin = $("#kf-metin").value;
  try {
    const j = await api("/api/kanal/dosya-oku", { metin: F.metin });
    Object.assign(F, { okundu: true, kanal: j.kanal, anayasa: j.anayasa, eksik: j.eksik, okunan: j.okunan, doldur: j.doldur,
      hatalar: j.hatalar, uyarilar: j.uyarilar, okunanDil: j.kanal.dil.hedef,
      eksikNeden: Object.fromEntries(j.eksik.map((e) => [e.yol, e.neden])) });
  } catch (e) { F.hatalar = [e.message]; F.uyarilar = []; }
  kanalFormuCiz();
}

function kanalAyarAc() {
  F = { mod: "ayarlar", adim: 0, kanal: kopya(D.kanal.ayar), hatalar: [], uyarilar: [] };
  kanalFormuCiz(); $("#kanal-pencere").showModal();
}

function kanalFormuCiz() {
  const b = bolumler();
  const k = F.kanal;
  let govde, alt;
  const notlar = (F.hatalar.length ? `<ul class="notlar hata">${F.hatalar.map((x) => `<li>${kacir(x)}</li>`).join("")}</ul>` : "") +
    (F.uyarilar.length ? `<ul class="notlar uyari">${F.uyarilar.map((x) => `<li>${kacir(x)}</li>`).join("")}</ul>` : "");
  if (F.mod === "ekle" && F.yol !== "elle") {
    $("#kanal-formu").innerHTML = dosyaEkranlari();
    return;
  }
  if (F.mod === "ekle") {
    const toplam = b.length + 1;
    const cubuk = `<div class="adim-cubugu">${[...b.map((x) => x.baslik), "9 · Beceriler ve dosyalar"].map((x, i) => `<span class="${i === F.adim ? "simdi" : i < F.adim ? "gecti" : ""}">${kacir(x)}</span>`).join("")}</div>`;
    if (F.adim < b.length) govde = `<h3 class="bolum-baslik">${kacir(b[F.adim].baslik)}</h3>` + bolumHtml(b[F.adim], k, "ekle");
    else govde = `<h3 class="bolum-baslik">9 · Beceriler ve proje dosyaları</h3>
      <p class="soluk kucuk">Kanalın 6 aşama becerisi ve 4 proje dosyası (Yönetici, Anayasa, Defter, Aktif video) kanal klasörüne konur. Sonra "Kanal dosyaları"ndan düzenleyebilirsin.</p>
      <label class="satir" style="font-weight:500"><input type="radio" name="kaynak" value="sablon" ${F.kaynak === "sablon" ? "checked" : ""}> Genel şablondan başla <span class="soluk kucuk">(doldurulacak yerler ⟦DOLDUR⟧ ile işaretli)</span></label>
      <label class="satir" style="font-weight:500"><input type="radio" name="kaynak" value="klasor" ${F.kaynak === "klasor" ? "checked" : ""}> Bir klasörden içe aktar <span class="soluk kucuk">(kaynak klasör değiştirilmez, kopyalanır)</span></label>
      <input type="text" id="ice-klasor" placeholder="ör. ~/Desktop/BaskaKanal" value="${kacir(F.klasor)}" ${F.kaynak === "klasor" ? "" : "disabled"}>
      <p class="alan-aciklama">İçe aktarmada SKILL.md dosyaları adlarına göre (konu, arastirma, senaryo, ceviri/italyanca, sahne, paketleme), proje dosyaları 00_/01_/02_/03_ ile başlayan adlarına göre, Muzik ve Maskot klasörlerindeki medya da kopyalanır. Bulunamayanlar şablondan gelir.</p>`;
    alt = `<div class="satir" style="margin-top:18px;justify-content:space-between">
      <button class="dugme" data-eylem="kf-kapat">Vazgeç</button>
      <div class="satir">${F.adim > 0 ? `<button class="dugme" data-eylem="kf-geri">Geri</button>` : `<button class="dugme" data-eylem="kf-yol" data-secim="secim">Geri</button>`}
      ${F.adim < toplam - 1 ? `<button class="dugme ana-dugme" data-eylem="kf-ileri">İleri</button>` : `<button class="dugme ana-dugme" data-eylem="kf-kaydet">Kanalı oluştur</button>`}</div></div>`;
    govde = `<h2 style="margin-top:0">Kanal ekle</h2>${cubuk}${govde}`;
  } else {
    govde = `<h2 style="margin-top:0">Kanal ayarları · ${kacir(k.ad)}</h2>` + b.map((x) => `<h3 class="bolum-baslik">${kacir(x.baslik)}</h3>` + bolumHtml(x, k, "ayarlar")).join("");
    alt = `<div class="satir" style="margin-top:18px;justify-content:flex-end;position:sticky;bottom:-22px;background:var(--kart);padding:10px 0">
      <button class="dugme" data-eylem="kf-kapat">Vazgeç</button><button class="dugme ana-dugme" data-eylem="kf-kaydet">Kaydet</button></div>`;
  }
  $("#kanal-formu").innerHTML = govde + notlar + alt;
}

function formuAl() {
  formOku($("#kanal-formu"), F.kanal);
  if (F.kanal.kod_oneki) F.kanal.kod_oneki = F.kanal.kod_oneki.toUpperCase();
  if (F.kanal.kisaltma) F.kanal.kisaltma = F.kanal.kisaltma.toLowerCase();
  const r = document.querySelector("input[name=kaynak]:checked");
  if (r) F.kaynak = r.value;
  if ($("#ice-klasor")) F.klasor = $("#ice-klasor").value.trim();
}

async function kfIleri(yon) {
  if (F.mesgul) return;  // art arda tıklama adım atlatmasın
  F.mesgul = true;
  try { await kfAdim(yon); } finally { if (F) F.mesgul = false; }
}

async function kfAdim(yon) {
  formuAl();
  if (F.adim === 0 && F.mod === "ekle" && !F.kanal.kisaltma && F.kanal.ad) F.kanal.kisaltma = kisaltmaOner(F.kanal.ad);
  if (F.adim === 1 && F.mod === "ekle" && F.kanal.ses.language_code === D.kanal_varsayilan.ses.language_code) F.kanal.ses.language_code = F.kanal.dil.hedef;
  const j = await api("/api/kanal/dogrula", { kanal: F.kanal }).catch((e) => ({ hatalar: [e.message], uyarilar: [] }));
  // Yalnız bu adıma kadar olan alanlarla ilgili hataları göstermek zor; ileri giderken hata olsa da geçilir, sonda hepsi denetlenir.
  F.hatalar = yon > 0 && F.adim === 0 ? j.hatalar.filter((x) => /Kanal adı|Kısaltma|öneki|kısaltması/.test(x)) : [];
  F.uyarilar = [];
  if (!F.hatalar.length) F.adim = Math.max(0, F.adim + yon);
  kanalFormuCiz();
}

async function kfKaydet() {
  formuAl();
  try {
    if (F.mod === "ekle") {
      if (F.yol === "dosya" && F.kanal.ses.language_code === F.okunanDil) F.kanal.ses.language_code = F.kanal.dil.hedef;
      const j = await api("/api/kanal/ekle", { kanal: F.kanal, kaynak: F.yol === "dosya" ? "sablon" : F.kaynak, klasor: F.klasor,
        anayasa: F.yol === "dosya" ? F.anayasa : "" });
      $("#kanal-pencere").close();
      const aktarilan = j.ice_aktarma.filter((x) => !x.startsWith("Anayasa:")).length;
      bildir(`Kanal oluşturuldu: ${F.kanal.ad}` + (F.yol === "dosya" && F.anayasa ? " · anayasa dosyadan alındı" : "") + (aktarilan ? ` · ${aktarilan} dosya içe aktarıldı` : ""));
      await api("/api/kanal/sec", { kisaltma: j.kisaltma });
    } else {
      const j = await api("/api/kanal/guncelle", { kisaltma: D.aktif, kanal: F.kanal });
      $("#kanal-pencere").close();
      bildir("Kanal ayarları kaydedildi." + (j.uyarilar.length ? " " + j.uyarilar.join(" ") : ""));
    }
    F = null; await yenile(true);
  } catch (e) {
    F.hatalar = e.message.split("; "); kanalFormuCiz();
  }
}

// --- kanal dosyaları --------------------------------------------------------

async function dosyaAc(ad) {
  const j = await api(`/api/kanal/dosya?kanal=${encodeURIComponent(D.aktif)}&ad=${encodeURIComponent(ad)}`);
  $("#dosya-icerik").innerHTML = `<div class="satir" style="justify-content:space-between"><h2 style="margin:0">${kacir(ad)}</h2>
      <div class="satir"><button class="dugme ince" data-eylem="dosya-kopyala">Kopyala</button></div></div>
    <p class="soluk kucuk">⟦DOLDUR: …⟧ ile işaretli yerleri kanalına göre yaz ve işareti sil. Kaydedince önceki hâl kanal klasöründeki .yedek'e konur.</p>
    <textarea id="dosya-metin" class="dosya-duzenle" data-ad="${kacir(ad)}">${kacir(j.icerik)}</textarea>
    <div class="satir" style="margin-top:12px;justify-content:flex-end">
      <button class="dugme" data-eylem="dosya-kapat">Vazgeç</button><button class="dugme ana-dugme" data-eylem="dosya-kaydet">Kaydet</button></div>`;
  $("#dosya-pencere").showModal();
}

// --- kanal silme -------------------------------------------------------------

async function silAc() {
  const k = D.kanal.ayar;
  const j = await api(`/api/kanal/silinecekler?kanal=${encodeURIComponent(D.aktif)}`);
  $("#sil-icerik").innerHTML = `<h2 style="margin-top:0">Kanalı sil · ${kacir(k.ad)}</h2>
    <div class="tehlike-kutu"><p>Şunlar <b>Çöp Kutusu'na</b> taşınır (Çöp boşaltılana kadar geri alınabilir):</p>
      <ul class="notlar"><li>Kanal klasörü ve içindeki her şey: <code>${kacir(j.klasor)}</code> (videolar, arşiv, beceriler, müzik, maskot)</li>
      ${j.taslaklar.map((t) => `<li>Kanal Stüdyosu'nun bu kanal için oluşturduğu CapCut taslağı: <b>${kacir(t)}</b></li>`).join("")}</ul>
      <p class="kucuk soluk">Kanal Stüdyosu dışında oluşmuş CapCut taslaklarına dokunulmaz.${j.dokunulmayan.length ? " Dokunulmayan: " + kacir(j.dokunulmayan.join("; ")) : ""}</p></div>
    <label for="sil-ad">Onaylamak için kanal adını yaz: <b>${kacir(k.ad)}</b></label>
    <input type="text" id="sil-ad" autocomplete="off">
    <div class="satir" style="margin-top:14px;justify-content:flex-end">
      <button class="dugme" data-eylem="sil-kapat">Vazgeç</button><button class="dugme tehlike" data-eylem="sil-onayla">Kanalı sil</button></div>`;
  $("#sil-pencere").showModal();
}

// --- genel ayarlar --------------------------------------------------------

function anahtarAlani(tur, baslik, ornek) {
  const var_ = D.anahtarlar && D.anahtarlar[tur];
  return `<label>${baslik} ${var_ ? '<span class="soluk kucuk">· kayıtlı</span>' : '<span class="kucuk" style="color:var(--hata)">· kayıtlı değil</span>'}</label>
    <div class="satir"><input type="password" id="anahtar-${tur}" autocomplete="off" placeholder="${var_ ? "Kayıtlı (değiştirmek için yenisini yaz)" : ornek}" style="flex:1 1 220px">
      <button type="button" class="dugme" data-eylem="anahtar-test" data-tur="${tur}">Bağlantıyı test et</button>
      <button type="button" class="dugme" data-eylem="anahtar-kaydet" data-tur="${tur}">Kaydet</button>
      ${var_ ? `<button type="button" class="dugme tehlike" data-eylem="anahtar-sil" data-tur="${tur}">Sil</button>` : ""}</div>
    <p class="kucuk" id="anahtar-sonuc-${tur}" aria-live="polite"></p>`;
}

function ayarFormu() {
  const a = D.ayarlar;
  return `<h2 style="margin-top:0">Ayarlar <span class="soluk kucuk">(bütün kanallar için)</span></h2>
    <label>Yazım servisi</label>
    <select id="saglayici"><option value="claude_code" ${a.saglayici !== "openrouter" ? "selected" : ""}>Claude Code (abonelik)</option>
      <option value="openrouter" ${a.saglayici === "openrouter" ? "selected" : ""}>OpenRouter üzerinden Claude</option></select>
    <p class="soluk kucuk"><b>Claude Code:</b> bütün yazım işleri bu bilgisayardaki Claude Code ile, Pro/Max aboneliğinden yapılır; anahtar gerekmez. Claude Code kurulu ve PowerShell'de <code>claude</code> → /login ile aboneliğinle giriş yapılmış olmalı. Kullanım sınırı dolarsa adım durur, sınır açılınca Tekrar dene. <b>OpenRouter:</b> ücret OpenRouter kredisinden düşer, bütçe sınırları geçerlidir. Görseller (Flow) iki durumda da bugünkü gibi Claude uygulamasındaki beceriyle yapılır.</p>
    <div class="satir"><button type="button" class="dugme" data-eylem="anahtar-test" data-tur="claude_code">Claude Code'u kontrol et</button></div>
    <p class="kucuk" id="anahtar-sonuc-claude_code" aria-live="polite"></p>
    ${anahtarAlani("openrouter", "OpenRouter API anahtarı (yalnız OpenRouter seçiliyse)", "sk-or-…")}
    ${anahtarAlani("ai84", "AI84 API anahtarı (seslendirme)", "AI84 anahtarı")}
    <p class="soluk kucuk">Anahtarlar Windows Kimlik Bilgisi Yöneticisi'nde saklanır, dosyaya yazılmaz.</p>
    <label>Aylık bütçe ($, bütün kanallar · yalnız OpenRouter)</label><input type="number" min="1" step="1" id="aylik" value="${a.butce.aylik_usd}">
    <label>CapCut taslak klasörü</label><input type="text" id="yol-capcut" value="${kacir(a.yollar.capcut_taslak)}">
    <label>Önbellek süresi (yalnız OpenRouter)</label><select id="onbellek"><option value="5m" ${a.onbellek_suresi === "5m" ? "selected" : ""}>5 dakika</option><option value="1h" ${a.onbellek_suresi === "1h" ? "selected" : ""}>1 saat</option></select>
    <p class="soluk kucuk">Kurulum klasörü: ${kacir(D.kurulum)}</p>
    <div class="satir" style="margin-top:16px;justify-content:flex-end">
      <button type="button" class="dugme" data-eylem="ayar-kapat">Vazgeç</button>
      <button type="button" class="dugme ana-dugme" data-eylem="ayar-kaydet">Kaydet</button></div>`;
}

// --- üretim ekranı (ilk sürümdeki ekranın kanala bağlı hâli) --------

const para = (x) => (Number(x) || 0).toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " $";
let secilenDosya = {};     // aşama → seçili dosya sekmesi
let gorulenAsama = null;   // tamamlanmış bir aşamaya bakılıyorsa
const taslak = {};         // yazılan notlar (yeniden çizimde korunur)
let duzenlenen = null;     // elle düzenlenen dosya: {kimlik, ad}
const ASAMALAR = () => (D.kanal ? D.kanal.asamalar : []);

const DURUM_ADI = { bekliyor: "Bekliyor", calisiyor: "Çalışıyor", kontrol: "Kontrol ediliyor", onay_bekliyor: "Onay bekliyor", tamam: "Tamam", hata: "Durdu", butce_sorusu: "Bütçe sorusu", bekleme: "Bekliyor" };
const BAKIYE_UYARI_USD = 2;  // bir yazım aşaması bundan pahalı olabilir: yarıda kalmadan kredi yükle

function bakiyeCiz() {
  const b = D.bakiye || {}, parca = [];
  let az = false;
  if (b.saglayici === "openrouter") {
    const v = b.openrouter;
    az = typeof v === "number" && v < BAKIYE_UYARI_USD;
    parca.push(`<span${az ? ' class="az-deger"' : ""}>OpenRouter <b>${typeof v === "number" ? para(v) : "—"}</b></span>`);
  }
  if (b.ai84 !== null && b.ai84 !== undefined) parca.push(`AI84 <b>${Number(b.ai84).toLocaleString("tr-TR")}</b> kredi`);
  else if (b.zaman) parca.push("AI84 <b>—</b>");
  const el = $("#bakiye");
  el.hidden = !parca.length && !b.suruyor;
  el.innerHTML = b.suruyor && !parca.length ? "Bakiye okunuyor…" : "Kalan: " + parca.join(" · ");
  el.classList.toggle("az", az);
  el.title = (az ? "OpenRouter bakiyesi az: yazım aşaması yarıda kalabilir, kredi yükle. " : "") +
    "Kalan bakiye" + (b.zaman ? " · " + new Date(b.zaman * 1000).toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" }) : "") + " · tıkla: yenile";
}

function maliyetCiz() {
  bakiyeCiz();
  const m = D.maliyet;
  if (m && D.ayarlar.saglayici !== "openrouter") {
    $("#maliyet").innerHTML = "Yazım: <b>Claude Code aboneliği</b>" + (D.uretim && m.abonelik_tahmini_usd ? ` · API karşılığı ~${para(m.abonelik_tahmini_usd)}` : "");
    $("#maliyet").title = "Ücret abonelikten; API karşılığı yalnız bilgi içindir.";
    return;
  }
  $("#maliyet").innerHTML = m ? (D.uretim ? `Bu video <b>${para(m.video_usd)}</b> / ${para(m.video_sinir)} · ` : "") +
    `Bu ay <b>${para(m.ay_usd)}</b> / ${para(m.ay_sinir)}` : "";
}

function adimCubugu(d) {
  const ogeler = ASAMALAR().map((a) => {
    const s = d.asamalar[a.kimlik]?.durum || "bekliyor";
    if (s === "atlandi") return `<span class="adim atlandi" title="Hazır metinle başlandığı için atlandı">${kacir(a.ad)} · atlandı</span>`;
    const sinif = d.adim === a.kimlik ? "simdi" : s === "tamam" ? "tamam" : "";
    const gor = s === "tamam" && a.yazi ? `data-eylem="gor" data-kimlik="${a.kimlik}"` : "";
    return `<span class="adim ${sinif}" ${gor}>${kacir(a.ad)}${s === "tamam" ? " ✓" : ""}</span>`;
  }).join("");
  return `<div class="adimlar">${ogeler}</div>`;
}

function dosyaSekmeleri(a, kimlik, duzenlenebilir = false) {
  const ciktilar = ASAMALAR().find((x) => x.kimlik === kimlik).ciktilar;
  const secili = secilenDosya[kimlik] || ciktilar[0];
  const sekmeler = `<div class="sekmeler">${ciktilar.map((ad) => `<span class="sekme ${ad === secili ? "secili" : ""}" data-eylem="sekme" data-kimlik="${kimlik}" data-ad="${kacir(ad)}">${kacir(ad.replace(D.uretim.kod + "_", ""))}${a.elle_yedek?.[ad] ? " ✎" : ""}</span>`).join("")}</div>`;
  if (!duzenlenebilir) return sekmeler + `<pre class="dosya" id="uretim-dosya" data-ad="${kacir(secili)}">Yükleniyor…</pre>`;
  const geri = a.elle_yedek?.[secili] ? `<button class="dugme ince" data-eylem="elle-geri" data-kimlik="${kimlik}" data-ad="${kacir(secili)}">Modelin yazdığı hâle dön</button>` : "";
  if (duzenlenen && duzenlenen.kimlik === kimlik && duzenlenen.ad === secili) {
    const anahtar = `elle_${kimlik}_${secili}`;
    return sekmeler + `<textarea class="dosya duzenle" id="uretim-duzenle" data-taslak="${kacir(anahtar)}" data-ad="${kacir(secili)}" spellcheck="false">${kacir(taslak[anahtar] ?? "Yükleniyor…")}</textarea>
      <div class="satir" style="margin-top:8px"><button class="dugme ana-dugme" data-eylem="elle-kaydet" data-kimlik="${kimlik}" data-ad="${kacir(secili)}">Kaydet ve kontrol et</button>
      <button class="dugme" data-eylem="elle-vazgec">Vazgeç</button>${geri}</div>
      <p class="soluk kucuk">Kaydet ücretsizdir: model çağrılmaz, yalnız kod kontrolleri yeniden çalışır. Paragraflar arasındaki boş satırları koru; sahneler onlardan oluşur. Modelin yazdığı hâl yedeklenir.</p>`;
  }
  return sekmeler + `<pre class="dosya" id="uretim-dosya" data-ad="${kacir(secili)}">Yükleniyor…</pre>
    <div class="satir" style="margin-top:8px"><button class="dugme" data-eylem="elle-ac" data-kimlik="${kimlik}" data-ad="${kacir(secili)}">Metni burada düzenle</button>${geri}</div>`;
}

function kontrolNotlari(k) {
  if (!k) return "";
  return `${k.bilgiler?.length ? `<div class="etiketler">${k.bilgiler.map((b) => `<span class="etiket">${kacir(b)}</span>`).join("")}</div>` : ""}
    ${k.hatalar?.length ? `<h3>Otomatik düzeltmeyle çözülemeyenler</h3><ul class="notlar hata">${k.hatalar.map((h) => `<li>${kacir(h)}</li>`).join("")}</ul>` : ""}
    ${k.uyarilar?.length ? `<h3>Dikkat</h3><ul class="notlar uyari">${k.uyarilar.map((h) => `<li>${kacir(h)}</li>`).join("")}</ul>` : ""}`;
}

function calisiyorPaneli(baslik, s, u, yazi) {
  const ek = s.oto_tur ? ` · otomatik düzeltme ${s.oto_tur}` : s.kullanici_tur ? " · düzeltmen işleniyor" : "";
  const ilerleme = yazi ? (u.ilerleme ? u.ilerleme.toLocaleString("tr-TR") + " karakter" : "Başlıyor") : (u.ilerleme_metni || "Başlıyor…");
  return `<section class="kart"><h2>${baslik}</h2><div class="yukleniyor"><div class="donen"></div>
    <div><b>${s.durum === "kontrol" ? "Kontrol ediliyor…" : yazi ? "Yazılıyor…" : "Çalışıyor…"}</b>${kacir(ek)}<br>
    <span class="soluk kucuk" id="ilerleme" data-yazi="${yazi ? 1 : 0}">${kacir(ilerleme)}</span></div></div>
    <p class="soluk kucuk">Bu adım ${yazi ? "birkaç dakika" : "uzun (ses ve video için 15–20 dk)"} sürebilir. Uygulamayı kapatırsan kaldığı yerden devam eder.</p>
    <button class="dugme tehlike" data-eylem="durdur">Durdur</button>
    <span class="soluk kucuk">${yazi ? "Yazım hemen kesilir; o ana kadarki kısmın ücreti gider, Tekrar dene ile adım baştan yazılır."
      : "Güvenli durdurma: ses/video o anki sahne, montaj o anki işlem bitince durur. Tekrar dene kaldığı yerden sürer."}</span></section>`;
}

function flowPaneli(u, s) {
  const f = u.flow || {};
  if (s.sorun) {
    return `<section class="kart"><h2>Görseller (Flow) · ajan bir sorun bildirdi</h2>
      <pre class="ozet">${kacir(s.sorun)}</pre>
      <p>Prompt değişmesi gerekiyorsa Aşama 5'e düzeltme gönder; uygulama promptu kendisi değiştirmez. Değişen sahneler için Flow isteği yeniden hazırlanır.</p>
      <textarea data-taslak="flow_duz" placeholder="Örn. 0034 politikaya takıldı: mutfakta yalnız fincan ve pencere olsun.">${kacir(taslak.flow_duz || "")}</textarea>
      <div class="satir" style="margin-top:10px"><button class="dugme ana-dugme" data-eylem="flow-a5">Aşama 5'e düzeltme gönder</button>
      <button class="dugme" data-eylem="flow-sorun-devam">Sorun çözüldü, beklemeye devam</button></div></section>`;
  }
  return `<section class="kart"><h2>Görseller (Flow)</h2>
    ${s.uyari ? `<p class="notlar uyari">${kacir(s.uyari)}</p>` : ""}
    ${s.eksik?.length ? `<p><b>Eksik/hatalı sahneler:</b> ${s.eksik.map((n) => "sahne" + String(n).padStart(4, "0")).join(", ")}</p>` : ""}
    ${s.boyut?.length ? `<ul class="notlar uyari">${s.boyut.map((x) => `<li>${kacir(x)}</li>`).join("")}</ul>` : ""}
    <ol>
      <li>Claude masaüstü uygulamasında <b>yeni bir sohbet</b> aç (Sonnet). <b>kanal-studyosu-flow</b> becerisi yüklü olmalı.</li>
      <li>Şunu yapıştır: <div class="satir" style="margin:6px 0"><code class="ozet" style="flex:1 1 300px;margin:0">${kacir(s.komut || "")}</code>
        <button class="dugme ince" data-eylem="kopyala" data-metin="${kacir(s.komut || "")}">Kopyala</button></div></li>
      <li>Ajan görselleri <b>flow_cikti</b> klasörüne koyup <code>BITTI.json</code> yazınca uygulama kendiliğinden kontrol eder ve devam eder (ses, video, CapCut taslağı ve rapor dahil).</li>
    </ol>
    <div class="yukleniyor"><div class="donen"></div><span>Bekleniyor · klasörde <b>${f.gorsel || 0}</b> görsel${f.zip ? `, ${f.zip} zip` : ""}</span></div>
    <p class="soluk kucuk">İstek klasörü: ${kacir(s.klasor || "")}<br>Görseller buraya: ${kacir(s.cikti || "")}</p>
    <div class="satir" style="margin-top:10px"><button class="dugme" data-eylem="flow-kontrol">Görselleri şimdi kontrol et</button>
      <button class="dugme" data-eylem="partiler">Yarı elle yol (partileri göster)</button></div>
    <div id="partiler"></div>
    <p class="soluk kucuk">Hatırlatma: Flow'un kullanım şartlarını sen izliyorsun. Hesap uyarısı gelirse yarı elle yola dön: partileri kopyala, Flow'a yapıştır, indirilen zip'i yukarıdaki klasöre bırak, sonra "Görselleri şimdi kontrol et".</p></section>`;
}

function bittiPaneli(u, d) {
  const r = d.sonuclar || {};
  const adaylar = d.silme_adaylari || [];
  const kok = D.kanal.klasor + "/";
  return `<section class="kart"><h2>Her şey bitti 🎬</h2>
    <div class="ozet">${kacir(r.rapor_ozet || "")}</div>
    <ul>
      <li><b>CapCut'ta açılacak taslak:</b> ${kacir(u.kod)} (listede yoksa CapCut'ı kapatıp aç)</li>
      <li><b>Süre / sahne:</b> ${kacir(r.sure || "?")} / ${kacir(r.sahne || "?")}</li>
      <li><b>Müzik:</b> ${kacir(r.muzik || "-")}${D.kanal.ayar.montaj.muzik ? ` <button class="dugme mini" data-eylem="muzik-yenile" title="Yeni rastgele parçalarla müziği yeniden yapar; eski hâli arşive kopyalanır">Müziği yeniden yap</button>` : ""}</li>
      <li><b>Kanal Defteri:</b> ${kacir(r.defter || "-")}</li>
      <li><b>Maliyet:</b> ${para(D.maliyet.video_usd)}</li>
    </ul>
    <p><b>Senin işin:</b> CapCut'ta kontrol, rötuş ve dışa aktarma; kapak görsellerini Flow'da üretmek.</p>
    <button class="dugme" data-eylem="rapor">Raporun tamamını göster</button><pre class="dosya" id="rapor" hidden></pre>
    ${adaylar.length ? `<h3>Silme adayları (${adaylar.length})</h3><ul class="notlar">${adaylar.map((x) => `<li>${kacir(x.startsWith(kok) ? x.slice(kok.length) : x)}</li>`).join("")}</ul>
      <p class="soluk kucuk">Uygulama hiçbir şey silmez. "Taşı" dersen kanal klasöründe Silinecekler/${kacir(u.kod)}/ içine taşınır, sen silersin. Cevap vermezsen üretimi kapatırken taşınır.</p>
      <div class="satir"><button class="dugme" data-eylem="silme" data-tasi="1">Silinecekler'e taşı</button><button class="dugme" data-eylem="silme" data-tasi="0">Kalsın</button></div>` :
      d.silme_karari ? `<p class="soluk">Silme adayları: ${kacir(d.silme_karari)}.</p>` : ""}
    <div class="satir" style="margin-top:16px"><button class="dugme ana-dugme" data-eylem="uretim-kapat">Üretimi kapat, ana ekrana dön</button></div></section>`;
}

function uretimEkrani() {
  const u = D.uretim, d = u.durum;
  const kimlik = gorulenAsama || d.adim;
  const tanim = ASAMALAR().find((a) => a.kimlik === kimlik);
  let govde = "";
  if (!tanim) {
    govde = bittiPaneli(u, d);
  } else {
    const s = d.asamalar[kimlik];
    const baslik = kacir(tanim.ad);
    if (gorulenAsama) {
      govde = `<section class="kart"><div class="satir" style="justify-content:space-between"><h2>${baslik} (onaylandı)</h2>
        <button class="dugme ince" data-eylem="geri">Güncel adıma dön</button></div>
        ${s.onay_notu ? `<p><b>Onay notun:</b> ${kacir(s.onay_notu)}</p>` : ""}${dosyaSekmeleri(s, kimlik)}</section>`;
    } else if (s.durum === "calisiyor" || s.durum === "kontrol" || (u.calisiyor && s.durum !== "onay_bekliyor")) {
      govde = calisiyorPaneli(baslik, s, u, tanim.yazi);
    } else if (kimlik === "FLOW" && s.durum === "bekleme") {
      govde = flowPaneli(u, s);
    } else if (s.durum === "bekleme") {
      govde = `<section class="kart"><h2>${baslik}</h2><p>${kacir(s.uyari || "Devam için seni bekliyor.")}</p>
        <button class="dugme ana-dugme" data-eylem="devam">Devam</button></section>`;
    } else if (s.durum === "onay_bekliyor" && !tanim.yazi) {
      govde = `<section class="kart"><h2>${baslik} · kontrol notları</h2>
        <p>${kimlik === "STUDIO" ? "Ses kenarı kontrolü aşağıdaki sahnelerin sonunda kesik buldu. Bu sahnelerin sonunu dinle; sorun değilse <b>Yine de devam et</b>." : "Senkron kontrolü aşağıdaki notları verdi. Notları CapCut'ta düzelttiysen <b>Tekrar kontrol et</b>; sorun değilse <b>Yine de devam et</b>."}</p>
        ${kontrolNotlari(s.kontrol)}<h3>Kontrol çıktısı</h3><pre class="ozet">${kacir(s.ozet || "")}</pre>
        <div class="satir"><button class="dugme ana-dugme" data-eylem="onay" data-kimlik="${kimlik}">Yine de devam et</button>
        <button class="dugme" data-eylem="devam">Tekrar kontrol et</button></div></section>`;
    } else if (s.durum === "onay_bekliyor") {
      const temiz = !(s.kontrol?.hatalar?.length);
      const onayAdi = tanim.onay ? `ONAY ${tanim.onay}` : "Kontrol";
      govde = `<section class="kart"><h2>${baslik} · ${onayAdi}</h2>
        <p class="soluk">${temiz ? "Kod kontrollerinden geçti." : "Kod kontrolü sorun buldu; aşağıda listelendi."}
        ${s.model ? ` · ${kacir(D.ayarlar.modeller[s.model] || s.model)}` : ""}${s.usd ? ` · ${para(s.usd)}` : ""}</p>
        ${s.yedek_model_notu ? `<p class="notlar uyari">${kacir(s.yedek_model_notu)}</p>` : ""}
        ${kontrolNotlari(s.kontrol)}
        ${s.degisiklikler?.length && s.kullanici_tur ? `<h3>Son düzeltmede değişenler</h3><ul class="notlar">${s.degisiklikler.slice(-30).map((x) => `<li>${kacir(x)}</li>`).join("")}</ul>` : ""}
        ${s.acik_noktalar ? `<h3>Açık noktalar</h3><p class="acik-noktalar ${/^yok\.?$/i.test(s.acik_noktalar.trim()) ? "soluk" : "notlar uyari"}">${kacir(s.acik_noktalar)}</p>` : ""}
        <h3>Özet</h3><div class="ozet">${kacir(s.ozet || "")}</div>
        ${dosyaSekmeleri(s, kimlik, true)}
        <div class="onay-alani">
          <div class="kutu"><h3>${tanim.onay ? "Onayla" : "Devam et"}</h3>
            <textarea data-taslak="onay_${kimlik}" placeholder="İsteğe bağlı not (sonraki aşamaya iletilir)">${kacir(taslak["onay_" + kimlik] || "")}</textarea>
            <button class="dugme ana-dugme" style="margin-top:10px" data-eylem="onay" data-kimlik="${kimlik}">${tanim.onay ? `ONAY ${tanim.onay} ver` : "Yine de devam et"}</button></div>
          <div class="kutu"><h3>Düzeltme iste</h3>
            <textarea data-taslak="duz_${kimlik}" placeholder="Ne değişsin? Örn. ¶12 daha kısa olsun; başlıkta şu kelime geçmesin.">${kacir(taslak["duz_" + kimlik] || "")}</textarea>
            <button class="dugme" style="margin-top:10px" data-eylem="duzeltme" data-kimlik="${kimlik}">Düzeltme gönder</button></div>
        </div></section>`;
    } else if (s.durum === "butce_sorusu") {
      govde = `<section class="kart"><h2>${baslik} · bütçe</h2><p>${kacir(s.hata)}</p>
        <div class="satir"><button class="dugme ana-dugme" data-eylem="tekrar" data-butce="1">Bu adım için devam et</button>
        <button class="dugme" data-eylem="kanal-ayar">Video bütçesini değiştir (Kanal ayarları)</button></div></section>`;
    } else if (s.durum === "hata") {
      govde = `<section class="kart"><h2>${baslik} · durdu</h2><p>${kacir(s.hata)}</p>
        ${s.hata_ayrinti ? `<details class="hata-ayrinti"><summary>Ayrıntı (betiğin çıktısı)</summary><pre class="ozet">${kacir(s.hata_ayrinti)}</pre></details>` : ""}
        <div class="satir"><button class="dugme ana-dugme" data-eylem="tekrar">Tekrar dene</button>
        <button class="dugme" data-eylem="hata-kopyala" data-kimlik="${kimlik}">Hatayı kopyala</button></div></section>`;
    } else {
      govde = `<section class="kart"><h2>${baslik}</h2><p class="soluk">${DURUM_ADI[s.durum] || ""}</p>
        <button class="dugme ana-dugme" data-eylem="tekrar">Başlat</button></section>`;
    }
  }
  const iptalEdilebilir = d.adim !== "BITTI" && !d.defter_tamam;
  return `<div class="satir" style="justify-content:space-between;margin-bottom:14px"><h1 style="margin:0;font-size:24px">${kacir(u.kod)} <span class="soluk kucuk" style="font-weight:400">· ${kacir(D.kanal.ayar.ad)}</span></h1>
    ${iptalEdilebilir ? `<button class="dugme ince tehlike" data-eylem="iptal">Üretimi iptal et</button>` : ""}</div>${adimCubugu(d)}${govde}`;
}

// Metin kutularına (dosya, özet, rapor, betik çıktısı) Kopyala ve Büyüt düğmeleri.
function metinKutulari() {
  document.querySelectorAll("#ana pre.dosya, #ana pre.ozet, #ana div.ozet").forEach((el) => {
    if (el.parentElement.classList.contains("kutu-kap")) return;
    const kap = document.createElement("div");
    kap.className = "kutu-kap";
    el.replaceWith(kap);
    kap.innerHTML = `<div class="kutu-arac"><button class="dugme mini" data-eylem="kutu-kopyala">Kopyala</button><button class="dugme mini" data-eylem="kutu-buyut">Büyüt</button></div>`;
    kap.appendChild(el);
  });
}

async function uretimDosyasiYukle() {
  const t = $("#uretim-duzenle");
  if (t && taslak[t.dataset.taslak] === undefined) {
    try { const ic = (await api("/api/dosya?ad=" + encodeURIComponent(t.dataset.ad))).icerik; taslak[t.dataset.taslak] = ic; t.value = ic; }
    catch (e) { t.value = e.message; }
  }
  const p = $("#uretim-dosya");
  if (!p) return;
  try { p.textContent = (await api("/api/dosya?ad=" + encodeURIComponent(p.dataset.ad))).icerik; }
  catch (e) { p.textContent = e.message; }
}

async function partilerGoster() {
  const k = $("#partiler");
  if (k.innerHTML) { k.innerHTML = ""; return; }
  const j = await api("/api/flow/istek").catch((e) => ({ hata: e.message }));
  if (!j.partiler) { k.innerHTML = `<p class="soluk">${kacir(j.hata || "İstek bulunamadı")}</p>`; return; }
  const ay = j.ayarlar || {};
  window.__partiler = { liste: j.partiler, oran: ay.oran || "16:9", model: ay.model || "Nano Banana 2" };
  k.innerHTML = `<h3>Yarı elle yol · ${j.partiler.length} parti</h3>
    <p class="soluk kucuk">Flow'da proje adı: <b>${kacir(j.proje_adi)}</b> · Ayarlar: ${kacir(window.__partiler.oran)}, x1, ${kacir(window.__partiler.model)}, "Hiçbir zaman". Her partiyi Flow'a yapıştır, bitmesini bekle, sonrakine geç.</p>` +
    j.partiler.map((p, i) => `<div class="kutu" style="margin:8px 0"><div class="satir" style="justify-content:space-between">
      <b>Parti ${i + 1} · ${kacir(p.sahneler[0])}–${kacir(p.sahneler[p.sahneler.length - 1])}</b>
      <button class="dugme ince" data-eylem="parti-kopyala" data-i="${i}">Kopyala</button></div></div>`).join("");
}

function partiKopyala(i) {
  const P = window.__partiler, p = P.liste[i];
  kopyala(`Sıradaki promptları sırayla üret (her biri ${P.oran}, x1, ${P.model}) ve üretilen görselleri sırayla ${p.sahneler.join(", ")} olarak adlandır. Hata olursa bir promptu en fazla 3 kez dene. Onay bekleme.\n\n` + p.promptlar.join("\n\n"));
}

// --- ana ekran ------------------------------------------------------------

function ustCiz() {
  const sec = $("#kanal-sec");
  const kilit = D.uretim ? ` disabled title="Üretim sürerken kanal değiştirilemez"` : ` title="Kanal seç"`;
  sec.innerHTML = D.kanallar.length ? `<select id="kanal-secici"${kilit}>${D.kanallar.map((k) => `<option value="${kacir(k.kisaltma)}" ${k.kisaltma === D.aktif ? "selected" : ""}>${kacir(k.ad)}${k.test ? " (test)" : ""}</option>`).join("")}</select>` : "";
}

function anaEkran() {
  const ok = D.onkontrol;
  const maddeler = ok ? ok.maddeler.map((x) => `<li><span class="isaret ${x.tamam ? "tamam" : x.zorunlu ? "yok" : "bilgi"}">${x.tamam ? "✓" : x.zorunlu ? "✗" : "!"}</span>
      <span><b>${kacir(x.ad)}</b> · <span class="soluk">${kacir(x.mesaj)}</span></span></li>`).join("") : "";
  const kontrol = `<section class="kart"><div class="satir" style="justify-content:space-between"><h2>Başlangıç kontrolü</h2>
      <button class="dugme ince" data-eylem="onkontrol" ${D.onkontrol_suruyor ? "disabled" : ""}>Yeniden kontrol et</button></div>
    ${D.onkontrol_suruyor && !ok ? `<div class="yukleniyor"><div class="donen"></div><span>Kontrol ediliyor…</span></div>` : `<ul class="kontrol-listesi">${maddeler}</ul>`}</section>`;
  if (!D.kanal) {
    return kontrol + `<section class="kart"><h2>Henüz kanal yok</h2>
      <p>Kanal Stüdyosu her kanalı kendi klasöründe, kendi ayarlarıyla çalıştırır. Başlamak için bir kanal ekle.</p>
      <button class="dugme ana-dugme" data-eylem="kanal-ekle">+ Kanal ekle</button>
      <p class="soluk kucuk" style="margin-top:12px">Kurulum klasörü: ${kacir(D.kurulum)}</p></section>`;
  }
  const k = D.kanal.ayar;
  const dil = D.diller[k.dil.hedef] || k.dil.hedef;
  const eksik = D.kanal.eksikler.length ? `<ul class="notlar">${D.kanal.eksikler.map((e) => `<li style="color:var(${e.zorunlu ? "--hata" : "--uyari"})">${kacir(e.mesaj)}</li>`).join("")}</ul>` : `<p style="color:var(--tamam)">✓ Kanal üretime hazır.</p>`;
  const dosyalar = D.kanal.dosyalar.map((d) => `<li data-eylem="dosya-ac" data-ad="${kacir(d.ad)}"><b>${kacir(d.ad.replace("Beceriler/", "Beceri · ").replace("/SKILL.md", ""))}</b>
      ${d.doldur ? `<span class="rozet uyari">${d.doldur} yer doldurulacak</span>` : `<span class="rozet tamam">hazır</span>`}</li>`).join("");
  return kontrol + `
  <section class="kart kanal-karti">
    <div class="satir" style="justify-content:space-between"><h2>${kacir(k.ad)}${k.test ? ' <span class="rozet">test kanalı</span>' : ""}</h2>
      <div class="satir"><button class="dugme ince" data-eylem="kanal-ayar">Kanal ayarları</button>
      <button class="dugme ince" data-eylem="klasor-ac">Klasörü aç</button>
      <button class="dugme ince tehlike" data-eylem="kanal-sil">Kanalı sil</button></div></div>
    <div class="bilgi">
      <span class="soluk">Video kodu</span><span>${kacir(k.kod_oneki)}-01, ${kacir(k.kod_oneki)}-02…</span>
      <span class="soluk">Dil akışı</span><span>Türkçe senaryo → ${kacir(dil)}${k.dil.hedef === "tr" ? " (4. aşama atlanır)" : ""} → ${kacir(dil)} seslendirme</span>
      <span class="soluk">Süre</span><span>~${kacir(k.uzunluk.hedef_dk)} dk · ${kacir(k.uzunluk.hedef_kelime.join("–"))} kelime</span>
      <span class="soluk">Ses</span><span>${kacir(k.ses.voice_name || k.ses.voice_id || "seçilmedi")} · ${kacir(k.ses.model_id)}</span>
      <span class="soluk">Karakter</span><span>${kacir(k.gorsel.karakter || "yok")}</span>
      <span class="soluk">Maskot / müzik</span><span>${k.montaj.maskot.dosyalar.length ? k.montaj.maskot.dosyalar.length + " maskot" : "maskot yok"} · müzik ${k.montaj.muzik ? "açık" : "kapalı"}</span>
      <span class="soluk">Klasör</span><span class="kucuk">${kacir(D.kanal.klasor)}</span>
    </div>
    <h3>Üretime hazırlık</h3>${eksik}
  </section>
  <section class="kart"><h2>Kanal dosyaları</h2>
    <p class="soluk kucuk">Becerileri ve proje dosyalarını burada düzenleyebilirsin. Sayısal sınırlar, etiketler ve ses gibi değerler Kanal ayarları'ndadır; uygulama onları her aşamada modele kendisi verir.</p>
    <ul class="dosya-listesi">${dosyalar}</ul></section>
  ${baslatKarti()}
  ${videolarKarti()}`;
}

// "Sıradaki üretim" kartı: konudan başla ya da hazır metinle başla; bu üretimde istenecek onaylar.
function baslatKarti() {
  const ok = D.onkontrol, hazir = ok && ok.hazir;
  const kanalHazir = !D.kanal.eksikler.some((e) => e.zorunlu);
  const sebep = !hazir ? "Başlangıç kontrolündeki eksikler tamamlanınca açılır." : !kanalHazir ? "Kanalın üretime hazırlığındaki eksikler tamamlanınca açılır." : !D.kanal.siradaki ? "Sıradaki kod bulunamadı." : "";
  const K_ = D.kanal, mod = taslak.mod === "hazir" ? "hazir" : "konu";
  const diller = Object.entries(K_.hazir_diller);
  const dil = taslak.hazir_dil && K_.hazir_diller[taslak.hazir_dil] ? taslak.hazir_dil : diller[diller.length - 1][0];
  const onaylar = K_.onay_secilebilir.map((o) => {
    const acik = taslak["uonay_" + o.kimlik] ?? K_.onaylar[o.kimlik];
    const atlanir = mod === "hazir" && (o.kimlik === "A2" || (o.kimlik === "A4" && dil !== "tr"));
    return `<label class="satir" style="margin:0;font-weight:500;${atlanir ? "opacity:.45" : ""}"><input type="checkbox" data-taslak="uonay_${o.kimlik}" ${acik ? "checked" : ""} ${atlanir ? "disabled" : ""}> ONAY ${o.onay} · ${kacir(o.ad.replace(/^\d · /, ""))}${atlanir ? " (bu yolda yok)" : ""}</label>`;
  }).join("");
  const atlanan = K_.ayar.dil.hedef === "tr" ? "2–3. aşamalar atlanır" : `Türkçe metinde 2–3. aşamalar, ${kacir(K_.dil_adi)} metinde 2–4. aşamalar atlanır`;
  const govde = mod === "konu" ? `
    <label for="konu-istegi">Konu isteğin (isteğe bağlı)</label>
    <input type="text" id="konu-istegi" data-taslak="konu_istegi" value="${kacir(taslak.konu_istegi || "")}" placeholder="Boş bırakırsan konuyu 1. aşama seçer">` : `
    <p class="soluk kucuk">Metnin hazırsa yapıştır. Tek bir yazım adımında konu kartı çıkarılır, Kanal Defteri'ne göre çakışma kontrol edilir, metin sahne paragraflarına bölünüp etiketlenir. <b>Metnin kelimelerine dokunulmaz</b>; uygulama bunu denetler. ${atlanan}.</p>
    <label>Metnin dili</label>
    <div class="satir">${diller.map(([k, ad]) => `<label class="satir" style="margin:0;font-weight:500"><input type="radio" name="hazir-dil" value="${k}" data-taslak="hazir_dil" ${k === dil ? "checked" : ""}> ${kacir(ad)}</label>`).join("")}</div>
    <label for="hazir-metin">Metin</label>
    <textarea id="hazir-metin" data-taslak="hazir_metin" style="min-height:220px" placeholder="Metni buraya yapıştır">${kacir(taslak.hazir_metin || "")}</textarea>`;
  return `<section class="kart">
    <h2>Sıradaki üretim: ${kacir(K_.siradaki || "—")}</h2>
    <div class="sekmeler"><span class="sekme ${mod === "konu" ? "secili" : ""}" data-eylem="baslat-mod" data-mod="konu">Konudan başla</span>
      <span class="sekme ${mod === "hazir" ? "secili" : ""}" data-eylem="baslat-mod" data-mod="hazir">Hazır metinle başla</span></div>
    ${govde}
    ${onaylar ? `<h3>Bu üretimde onay iste</h3><div class="satir" style="gap:16px;flex-wrap:wrap">${onaylar}</div>` : ""}
    <p class="soluk kucuk">Varsayılanlar Kanal ayarları › Onaylar'dan gelir. ONAY 1 ve ONAY 3 her zaman istenir (hazır metinde ilk onay ekranı). Onayı kapalı aşama, kod kontrolleri temizse beklemeden geçer; sorun varsa yine durur.</p>
    <div class="satir" style="margin-top:16px">
      <button class="dugme ana-dugme" data-eylem="baslat" ${sebep ? "disabled" : ""}>${mod === "hazir" ? "Hazır metinle başla" : "Üretime başla"}</button>
      ${sebep ? `<span class="soluk kucuk">${sebep}</span>` : ""}
    </div>
    <p class="soluk kucuk">Aşamalar: ${ASAMALAR().map((a) => kacir(a.ad)).join(" → ")}</p>
  </section>`;
}

function baslatGovdesi() {
  const K_ = D.kanal, mod = taslak.mod === "hazir" ? "hazir" : "konu";
  const onaylar = Object.fromEntries(K_.onay_secilebilir.map((o) => [o.kimlik, !!(taslak["uonay_" + o.kimlik] ?? K_.onaylar[o.kimlik])]));
  const diller = Object.keys(K_.hazir_diller);
  const dil = taslak.hazir_dil && K_.hazir_diller[taslak.hazir_dil] ? taslak.hazir_dil : diller[diller.length - 1];
  return mod === "hazir" ? { hazir: true, hazir_metin: taslak.hazir_metin || "", hazir_dil: dil, onaylar }
    : { konu_istegi: taslak.konu_istegi || "", onaylar };
}

function videolarKarti() {
  const satirlar = D.kanal.liste.map((v) => `<tr><td class="kod"><b>${kacir(v.kod)}</b></td><td>${kacir(v.baslik)}</td><td>${kacir(v.durum)}</td>
      <td>${kacir(v.sure)}${v.sahne ? " / " + v.sahne : ""}</td><td class="soluk kucuk">${v.salt_okunur ? "salt okunur" : v.rapor ? `<button class="dugme mini" data-eylem="liste-rapor" data-kod="${kacir(v.kod)}">Rapor</button>` : ""}</td></tr>`).join("");
  return `<section class="kart"><h2>Videolar</h2>
    <div class="tablo-kap"><table><thead><tr><th>Kod</th><th>Başlık</th><th>Durum</th><th>Süre / sahne</th><th></th></tr></thead>
    <tbody>${satirlar || `<tr><td colspan=5 class="soluk">Henüz video yok.</td></tr>`}</tbody></table></div>
  </section>`;
}


function ekranImzasi() {
  const u = D.uretim;
  return JSON.stringify([D.onkontrol, D.onkontrol_suruyor, D.kanallar, D.aktif, D.kanal, gorulenAsama, duzenlenen,
    u && [u.kod, u.durum.adim, u.durum.asamalar, u.calisiyor, u.flow, u.durum.silme_adaylari, u.durum.silme_karari]]);
}

async function yenile(zorla = false) {
  try { D = await api("/api/durum"); } catch (e) { $("#ana").innerHTML = `<p class="soluk">Uygulamaya ulaşılamıyor. Kapatılmış olabilir.</p>`; return; }
  maliyetCiz();
  const yeni = ekranImzasi();
  if (zorla || yeni !== imza) {
    imza = yeni; ustCiz();
    // Bir dialog içinde yazı yazılıyorsa ana ekran yine çizilir; dialoglar ayrı kaldığı için yazılanlar kaybolmaz.
    $("#ana").innerHTML = D.uretim && D.kanal ? uretimEkrani() : anaEkran();
    metinKutulari();
    uretimDosyasiYukle();
  } else if (D.uretim && $("#ilerleme")) {
    const el = $("#ilerleme");
    el.textContent = el.dataset.yazi === "1"
      ? (D.uretim.ilerleme ? D.uretim.ilerleme.toLocaleString("tr-TR") + " karakter" : "Başlıyor")
      : (D.uretim.ilerleme_metni || "Çalışıyor…");
  }
  if (!$("#kayit-paneli").hidden) kayitYukle();
}

// Kayıt paneli: kullanıcı yukarı kaydırdıysa ya da metin seçiyse yenileme onu aşağı atmaz.
let kayitSatirlari = [];
function kayitGorunen() {
  const yalnizHata = $("#kayit-hata")?.checked;
  const bloklar = [];
  for (const l of kayitSatirlari) { if (/^\d\d:\d\d:\d\d \[/.test(l) || !bloklar.length) bloklar.push(l); else bloklar[bloklar.length - 1] += "\n" + l; }
  return yalnizHata ? bloklar.filter((b) => /^\S+ \[(hata|uyari)\]/.test(b)) : bloklar;
}
async function kayitYukle(zorla = false) {
  const p = $("#kayit-icerik");
  const sel = window.getSelection();
  if (!zorla && sel && !sel.isCollapsed && p.contains(sel.anchorNode)) return;
  const altta = p.scrollHeight - p.scrollTop - p.clientHeight < 40;
  const j = await api("/api/kayit").catch(() => ({ satirlar: [] }));
  kayitSatirlari = j.satirlar.flatMap((x) => x.split("\n"));
  const yeni = kayitGorunen().join("\n");
  if (yeni !== p.textContent) {
    const ust = p.scrollTop;
    p.textContent = yeni;
    p.scrollTop = altta || zorla ? p.scrollHeight : ust;
  }
  $("#kayit-asagi").hidden = p.scrollHeight - p.scrollTop - p.clientHeight < 40;
}

// --- olaylar --------------------------------------------------------------

document.addEventListener("input", (e) => {
  const t = e.target;
  if (t.dataset.taslak) taslak[t.dataset.taslak] = t.type === "checkbox" ? t.checked : t.value;
  if (F && $("#kelime-bilgi") && ["uzunluk.hedef_dk", "dil.hedef", "ses.speed", "uzunluk.kelime_otomatik"].includes(t.dataset.yol)) {
    formOku($("#kanal-formu"), F.kanal); $("#kelime-bilgi").textContent = kelimeBilgi(F.kanal);
    if (t.dataset.yol === "uzunluk.kelime_otomatik") {
      document.querySelectorAll(".elle-kelime").forEach((x) => { x.hidden = t.checked; });
      const dk = Number(F.kanal.uzunluk.hedef_dk);
      if (!t.checked && dk >= 1 && dk <= 60) {  // elle ayara geçerken son hesaplanan değerlerden başla
        const tr = kelimeAraligi(F.kanal, "tr").aralik, hd = kelimeAraligi(F.kanal, F.kanal.dil.hedef).aralik;
        [["uzunluk.calisma_kelime.0", tr[0]], ["uzunluk.calisma_kelime.1", tr[1]], ["uzunluk.hedef_kelime.0", hd[0]], ["uzunluk.hedef_kelime.1", hd[1]]]
          .forEach(([y, v]) => { const el = document.querySelector(`[data-yol="${y}"]`); if (el) el.value = v; });
        formOku($("#kanal-formu"), F.kanal); $("#kelime-bilgi").textContent = kelimeBilgi(F.kanal);
      }
    }
  }
});

document.addEventListener("change", (e) => {
  if (e.target.id === "kayit-hata") kayitYukle(true);
  if (e.target.name === "hazir-dil") { imza = ""; yenile(true); }  // dil değişince atlanan onaylar güncellensin
  if (e.target.id === "kanal-secici") yap(() => api("/api/kanal/sec", { kisaltma: e.target.value }));
  if (e.target.name === "kaynak" && $("#ice-klasor")) $("#ice-klasor").disabled = e.target.value !== "klasor";
  if (e.target.type === "color") e.target.nextElementSibling.textContent = e.target.value;
  if (e.target.id === "kf-dosya" && e.target.files[0]) {
    const r = new FileReader();
    r.onload = () => { $("#kf-metin").value = r.result; };
    r.readAsText(e.target.files[0], "utf-8");
  }
});

document.addEventListener("click", (e) => {
  const el = e.target.closest("[data-eylem]");
  if (!el) return;
  const k = el.dataset.kimlik;
  const eylemler = {
    ...uretimEylemleri(el, k),
    onkontrol: () => yap(() => api("/api/onkontrol", {})),
    "kanal-ekle": () => kanalEkleAc(),
    "kanal-ayar": () => kanalAyarAc(),
    "kanal-sil": () => silAc().catch((x) => bildir(x.message)),
    "klasor-ac": () => api("/api/kanal/klasor-ac", { kisaltma: D.aktif }).catch((x) => bildir(x.message)),
    "kf-ileri": () => kfIleri(1),
    "kf-geri": () => kfIleri(-1),
    "kf-kaydet": () => kfKaydet(),
    "kf-kapat": () => { $("#kanal-pencere").close(); F = null; },
    "kf-yol": () => { if (F.yol === "dosya" && $("#kf-metin")) F.metin = $("#kf-metin").value; F.yol = el.dataset.secim; F.adim = 0; F.hatalar = []; F.uyarilar = []; kanalFormuCiz(); },
    "kf-sablon-kopyala": () => api("/api/kanal/sablon").then((j) => kopyala(j.metin)).catch((x) => bildir(x.message)),
    "kf-dosya-oku": () => kfDosyaOku(),
    "kf-dosya-geri": () => { formuAl(); F.okundu = false; F.hatalar = []; F.uyarilar = []; kanalFormuCiz(); },
    "dosya-ac": () => dosyaAc(el.dataset.ad).catch((x) => bildir(x.message)),
    "dosya-kopyala": () => kopyala($("#dosya-metin").value),
    "dosya-kapat": () => $("#dosya-pencere").close(),
    "dosya-kaydet": () => yap(async () => {
      await api("/api/kanal/dosya", { kanal: D.aktif, ad: $("#dosya-metin").dataset.ad, icerik: $("#dosya-metin").value });
      $("#dosya-pencere").close(); bildir("Dosya kaydedildi.");
    }),
    "sil-kapat": () => $("#sil-pencere").close(),
    "sil-onayla": () => yap(async () => {
      const ad = D.kanal.ayar.ad;
      const j = await api("/api/kanal/sil", { kisaltma: D.aktif, onay_adi: $("#sil-ad").value });
      $("#sil-pencere").close();
      bildir(`${ad} silindi: ${j.tasinan.length} öğe Çöp Kutusu'na taşındı.`);
    }),
    ayarlar: () => { $("#ayar-formu").innerHTML = ayarFormu(); $("#ayar-penceresi").showModal(); },
    "ayar-kapat": () => $("#ayar-penceresi").close(),
    "ayar-kaydet": () => yap(async () => {
      await api("/api/ayarlar", { butce: { aylik_usd: Number($("#aylik").value) }, yollar: { capcut_taslak: $("#yol-capcut").value.trim() },
        onbellek_suresi: $("#onbellek").value, saglayici: $("#saglayici").value });
      $("#ayar-penceresi").close(); bildir("Ayarlar kaydedildi.");
    }),
    "anahtar-kaydet": () => yap(async () => { const t = el.dataset.tur; await api("/api/anahtar", { tur: t, anahtar: $("#anahtar-" + t).value }); $("#ayar-penceresi").close(); bildir("Anahtar kaydedildi."); }),
    "anahtar-sil": () => yap(async () => { const t = el.dataset.tur; if (confirm("Anahtar silinsin mi?")) { await api("/api/anahtar", { tur: t, sil: true }); $("#ayar-penceresi").close(); } }),
    "anahtar-test": async () => {
      const t = el.dataset.tur, s = $("#anahtar-sonuc-" + t);
      s.textContent = "Deneniyor…"; el.disabled = true;
      try { const j = await api("/api/anahtar-test", { tur: t, anahtar: $("#anahtar-" + t)?.value || "" }); s.textContent = (j.tamam ? "✓ " : "✗ ") + j.mesaj; s.style.color = j.tamam ? "var(--tamam)" : "var(--hata)"; }
      catch (x) { s.textContent = "✗ " + x.message; s.style.color = "var(--hata)"; }
      finally { el.disabled = false; }
    },
    kayit: () => { const p = $("#kayit-paneli"); p.hidden = !p.hidden; if (!p.hidden) kayitYukle(true); },
    "kayit-kopyala": () => kopyala(kayitGorunen().join("\n")),
    "kayit-son-hata": () => { const h = kayitGorunen().filter((b) => /^\S+ \[hata\]/.test(b)).pop(); h ? kopyala(h) : bildir("Kayıtta hata yok."); },
    "kayit-dosya": () => api("/api/kayit/ac", {}).then(() => bildir("Tüm geçmiş Not Defteri'nde açıldı.")).catch((x) => bildir(x.message)),
    "kayit-buyut": () => { const p = $("#kayit-paneli"); p.classList.toggle("buyuk"); el.textContent = p.classList.contains("buyuk") ? "Küçült" : "Büyüt"; },
    "kayit-en-alt": () => { const p = $("#kayit-icerik"); p.scrollTop = p.scrollHeight; $("#kayit-asagi").hidden = true; },
    kapat: () => { if (confirm("Kanal Stüdyosu kapatılsın mı? Süren bir yazım varsa yarıda kalır; sonra kaldığı yerden devam edebilirsin.")) api("/api/kapat", {}).then(() => { document.body.innerHTML = "<p style='padding:30px'>Uygulama kapatıldı. Bu sekmeyi kapatabilirsin.</p>"; }); },
  };
  (eylemler[el.dataset.eylem] || (() => {}))();
});

function uretimEylemleri(el, k) {
  return {
    "baslat-mod": () => { taslak.mod = el.dataset.mod; imza = ""; yenile(true); },
    baslat: () => yap(async () => {
      const g = baslatGovdesi();
      if (g.hazir && !g.hazir_metin.trim()) throw new Error("Metni yapıştır.");
      await api("/api/uretim/baslat", g);
      bildir(g.hazir ? "Üretim başladı: hazır metin hazırlanıyor (konu kartı, sahne paragrafları, etiketler)." : "Üretim başladı: 1. aşama yazılıyor.");
      delete taslak.hazir_metin;
    }),
    onay: () => yap(async () => {
      if (duzenlenen && !confirm("Kaydedilmemiş bir düzenlemen var; onay kayıtlı hâli kullanır. Yine de onaylansın mı?")) return;
      duzenlenen = null;
      await api("/api/asama/onay", { kimlik: k, not: taslak["onay_" + k] || "" }); delete taslak["onay_" + k];
    }),
    duzeltme: () => yap(async () => {
      if (duzenlenen && !confirm("Kaydedilmemiş bir düzenlemen var; önce 'Kaydet ve kontrol et'e basmazsan model onu görmez. Yine de gönderilsin mi?")) return;
      duzenlenen = null; await api("/api/asama/duzeltme", { kimlik: k, not: taslak["duz_" + k] || "" }); delete taslak["duz_" + k];
    }),
    tekrar: () => yap(() => api("/api/asama/tekrar", { butce_onayli: el.dataset.butce === "1" })),
    devam: () => yap(() => api("/api/asama/devam", {})),
    "flow-kontrol": () => yap(() => api("/api/asama/flow-kontrol", {})),
    "flow-sorun-devam": () => yap(() => api("/api/asama/flow-sorun-devam", {})),
    "flow-a5": () => yap(async () => { await api("/api/asama/flow-a5-duzeltme", { not: taslak.flow_duz || "" }); delete taslak.flow_duz; }),
    partiler: () => partilerGoster(),
    "parti-kopyala": () => partiKopyala(Number(el.dataset.i)),
    kopyala: () => kopyala(el.dataset.metin),
    silme: () => yap(async () => { const j = await api("/api/asama/silme", { tasi: el.dataset.tasi === "1" }); bildir(j.tasinan.length ? `${j.tasinan.length} dosya Silinecekler'e taşındı.` : "Dosyalar yerinde kaldı."); }),
    "muzik-yenile": async () => {
      if (!confirm("Müzik yeni rastgele parçalarla yeniden yapılsın mı?\n\nCapCut kapalı olmalı. Taslaktaki müzik değişir; eski müzik dosyası ve taslak arşive kopyalanır, silinmez. 1–2 dakika sürebilir.")) return;
      el.disabled = true; el.textContent = "Yapılıyor…";
      try { const j = await api("/api/asama/muzik-yenile", {}); bildir("Müzik yenilendi. " + j.secilen); }
      catch (x) { bildir(x.message); }
      finally { imza = ""; yenile(true); }
    },
    "uretim-kapat": () => { if (confirm("Üretim kapatılsın mı? Dosyaların hepsi yerinde kalır.")) yap(async () => { await api("/api/asama/kapat", {}); gorulenAsama = null; secilenDosya = {}; }); },
    durdur: () => yap(async () => { await api("/api/asama/durdur", {}); bildir("Durduruluyor…"); }),
    iptal: () => {
      if (!confirm("Bu üretim iptal edilsin mi?\n\nHiçbir dosya silinmez: bu videonun klasörleri kanalın Arsiv klasörüne (…_iptal_tarih) taşınır, Aktif Video dosyası bu üretimden önceki hâline döner ve aynı kod bir sonraki üretimde yeniden kullanılır.\n\nÇalışan bir adım varsa önce Durdur'a bas.")) return;
      yap(async () => {
        const j = await api("/api/asama/iptal", {});
        let m = `İptal edildi. Dosyalar: ${j.klasor}.`;
        if (j.capcut_taslak) m += " CapCut taslağı yerinde bırakıldı.";
        bildir(m); gorulenAsama = null; secilenDosya = {};
      });
    },
    rapor: async () => { const r = $("#rapor"); r.hidden = !r.hidden; if (!r.hidden) r.textContent = (await api("/api/rapor").catch((x) => ({ icerik: x.message }))).icerik; },
    "kutu-kopyala": () => kopyala(el.closest(".kutu-kap").lastElementChild.innerText),
    "kutu-buyut": () => {
      const hedef = el.closest(".kutu-kap").lastElementChild;
      const bas = hedef.closest("section")?.querySelector("h2, h3");
      $("#buyuk-baslik").textContent = hedef.dataset.ad || (bas ? bas.textContent : "Metin");
      $("#buyuk-icerik").textContent = hedef.innerText;
      $("#buyuk-pencere").showModal();
    },
    "liste-rapor": async () => {
      const kod = el.dataset.kod;
      $("#buyuk-baslik").textContent = `${kod} · Üretim raporu`;
      $("#buyuk-icerik").textContent = "Yükleniyor…";
      $("#buyuk-pencere").showModal();
      $("#buyuk-icerik").textContent = (await api("/api/rapor?kod=" + encodeURIComponent(kod)).catch((x) => ({ icerik: x.message }))).icerik;
    },
    "buyuk-kopyala": () => kopyala($("#buyuk-icerik").textContent),
    "buyuk-kapat": () => $("#buyuk-pencere").close(),
    sekme: () => {
      if (duzenlenen && !confirm("Düzenlemen kaydedilmedi. Başka dosyaya geçilsin mi? (Yazdıkların bu pencerede saklı kalır.)")) return;
      duzenlenen = null; secilenDosya[k] = el.dataset.ad; imza = ""; yenile(true);
    },
    "elle-ac": () => { duzenlenen = { kimlik: k, ad: el.dataset.ad }; imza = ""; yenile(true); },
    "elle-vazgec": () => { if (duzenlenen) delete taslak[`elle_${duzenlenen.kimlik}_${duzenlenen.ad}`]; duzenlenen = null; imza = ""; yenile(true); },
    "elle-kaydet": () => yap(async () => {
      const anahtar = `elle_${k}_${el.dataset.ad}`;
      const j = await api("/api/asama/elle", { kimlik: k, ad: el.dataset.ad, icerik: $("#uretim-duzenle").value });
      delete taslak[anahtar]; duzenlenen = null;
      const h = j.kontrol?.hatalar?.length || 0, u = j.kontrol?.uyarilar?.length || 0;
      bildir(h ? `Kaydedildi. Kontrol ${h} sorun buldu; aşağıda listelendi.` : u ? `Kaydedildi. ${u} uyarı var.` : "Kaydedildi. Kontrollerden geçti.");
    }),
    "elle-geri": () => yap(async () => {
      if (!confirm("Bu dosya modelin yazdığı hâline dönsün mü? Elle yaptığın değişiklikler kaybolur.")) return;
      await api("/api/asama/elle-geri", { kimlik: k, ad: el.dataset.ad });
      delete taslak[`elle_${k}_${el.dataset.ad}`]; duzenlenen = null; bildir("Modelin yazdığı hâle dönüldü.");
    }),
    gor: () => { gorulenAsama = k; yenile(true); },
    geri: () => { gorulenAsama = null; yenile(true); },
    bakiye: () => api("/api/bakiye", {}).then(() => setTimeout(() => yenile(), 1500)),
    "hata-kopyala": () => kopyala(D.uretim?.durum?.asamalar?.[k]?.hata + "\n\n" + (D.uretim?.durum?.asamalar?.[k]?.hata_ayrinti || "")),
  };
}

function dongu() { yenile().finally(() => setTimeout(dongu, D && (D.uretim?.calisiyor || D.onkontrol_suruyor) ? 1500 : 4000)); }
dongu();
document.addEventListener("DOMContentLoaded", () => {
  const p = $("#kayit-icerik");
  if (p) p.addEventListener("scroll", () => { $("#kayit-asagi").hidden = p.scrollHeight - p.scrollTop - p.clientHeight < 40; });
});
