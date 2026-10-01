# -*- coding: utf-8 -*-
"""Konum (ilçe / köy / mahalle) sayfalarını, /hizmet-bolgeleri hub sayfasını
ve sitemap.xml'i tek kaynaktan üretir.

Kullanım (repo kökünden):  python _build/build_locations.py

Köy -> ilçe eşleşmeleri Türkçe Vikipedi'deki "<İlçe> belde ve köyleri"
şablonlarından doğrulanmıştır. İlçesi doğrulanamayan yerler için sayfada
ilçe bilgisi YAZILMAZ (yanlış bilgi vermemek için).
"""
import hashlib
import html
import json
import os
import re
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://akutakviyecisi.com"
PHONE_DISPLAY = "0555 166 33 80"
PHONE_TEL = "+905551663380"
WA = "905551663380"
TODAY = date.today().isoformat()

# ---------------------------------------------------------------------------
# İlçeler
# ---------------------------------------------------------------------------
# side: anadolu / avrupa / ada
DISTRICTS = {
    "merkez": {
        "name": "Çanakkale Merkez", "short": "Merkez", "side": "anadolu", "page": None,
        "paras": [
            "Çanakkale merkezde araçların büyük kısmı kısa mesafeli şehir içi yolculuk yapar. Kısa yolculuklarda alternatör aküyü tam dolduramaz; akü her marşta biraz daha boşalır ve özellikle kışın ilk soğuk sabahlarda araç çalışmaz hale gelir. Kepez, Güzelyalı ve Dardanos gibi sahil yerleşimlerinde ise kış boyunca kapalı kalan yazlık araçlarında akünün tamamen boşalması sık görülen bir durumdur.",
            "Şehir merkezindeki mahallelerden Kumkale, Tevfikiye (Troya) ve İntepe yönündeki köylere kadar tüm Merkez ilçesinde yerinde akü takviyesi ve akü değişimi yapıyoruz. Dar sokaklarda ya da kapalı otoparkta kalan araçlar için ekibimiz taşınabilir booster cihazıyla gelir; aracınızı çekmek ya da itmek gerekmez.",
        ],
    },
    "ayvacik": {
        "name": "Ayvacık", "short": "Ayvacık", "side": "anadolu", "page": "ayvacik",
        "paras": [
            "Ayvacık, Biga Yarımadası'nın güneybatısında, Kaz Dağları'nın eteğinden Edremit Körfezi kıyısına kadar uzanan geniş bir ilçedir. Çanakkale–İzmir karayolu (D550) ilçeden geçer; Küçükkuyu, Assos (Behramkale) ve Babakale gibi sahil yerleşimleri yazın çok kalabalıklaşır.",
            "Bu bölgede iki farklı akü sorunu öne çıkar: Kaz Dağları'na yakın yüksek köylerde kış soğuğu akünün marş gücünü (CCA) düşürür, sahildeki yazlık evlerde ise aylarca çalıştırılmayan araçların aküsü kendi kendine boşalır. Sezon açılışında yazlığa gelip aracı çalıştıramayanlar için yerinde takviye ve gerekirse yerinde akü değişimi yapıyoruz.",
        ],
    },
    "bayramic": {
        "name": "Bayramiç", "short": "Bayramiç", "side": "anadolu", "page": "bayramic",
        "paras": [
            "Bayramiç, Kaz Dağları'nın kuzey eteğinde, Karamenderes vadisinde yer alan bir iç bölge ilçesidir. Kışları kıyı ilçelerine göre belirgin şekilde soğuktur; sabah eksi derecelerde zayıf akülü araçlar marşa basmakta zorlanır.",
            "Tarım ve bahçe işlerinde kullanılan ticari araçlar, kamyonetler ve uzun süre bekleyen ikinci araçlar bölgede en sık akü sorunu yaşanan araçlardır. Bayramiç merkezde ve bağlı köylerde aracınızın yanına gelerek akü takviyesi yapıyor, akü ömrünü tamamladıysa uygun amper ve tipte yeni aküyü yerinde takıyoruz.",
        ],
    },
    "biga": {
        "name": "Biga", "short": "Biga", "side": "anadolu", "page": "biga",
        "paras": [
            "Biga, Çanakkale merkezine yaklaşık 90 km uzaklıkta, Marmara kıyısına uzanan ve ilin en kalabalık ilçelerinden biridir. Çanakkale–Bursa karayolu (D200) üzerinde olduğu için yoldan geçen araçların da sık yolda kaldığı bir güzergâhtır.",
            "Biga merkezi, Karabiga ve Gümüşçay gibi beldeler ile bağlı köylerde akü takviyesi ve yerinde akü değişimi yapıyoruz. Sanayi ve tarım bölgesinde çalışan ticari araçlar için yüksek amperli akü seçeneklerini de yanımızda getiriyoruz.",
        ],
    },
    "bozcaada": {
        "name": "Bozcaada", "short": "Bozcaada", "side": "ada", "page": "bozcaada",
        "paras": [
            "Bozcaada'ya araçla ulaşım, Ezine'deki Geyikli Yükyeri iskelesinden kalkan feribotla sağlanır. Adaya hizmet planlaması feribot saatlerine bağlı olduğundan aradığınızda size gerçekçi bir varış zamanı söyleriz.",
            "Adada yaz sezonunda çok sayıda araç kısa mesafelerde kullanılır, kışın ise uzun süre bekler. Bu iki durum da akünün yorulmasına neden olur. Sezon öncesinde akünüzü kontrol ettirmek ada içinde yolda kalma riskini ciddi şekilde azaltır.",
        ],
    },
    "can": {
        "name": "Çan", "short": "Çan", "side": "anadolu", "page": "can",
        "paras": [
            "Çan, ilin iç kesiminde yer alan, seramik sanayisi ve kömür madenciliğiyle bilinen bir ilçedir. Kışları soğuk ve nemli geçer; bu da özellikle 3 yaşını geçmiş akülerde sabah marş sorunlarını artırır.",
            "İş yerlerine erken saatte çıkan sürücüler ve vardiyalı çalışanlar için 7/24 arayabileceğiniz bir akü hattı sunuyoruz. Çan merkezde ve Terzialan gibi bağlı yerleşimlerde aracınızın yanına gelerek takviye veya değişim yapıyoruz.",
        ],
    },
    "eceabat": {
        "name": "Eceabat", "short": "Eceabat", "side": "avrupa", "page": "eceabat",
        "paras": [
            "Eceabat, Gelibolu Yarımadası üzerinde, Çanakkale–Eceabat feribot hattının Avrupa yakasındaki ayağıdır. Kilitbahir, Kabatepe ve yarımadadaki şehitlik alanları yıl boyunca çok sayıda ziyaretçi aracını ağırlar.",
            "Tarihi alanı gezerken farları ya da kontağı açık unutup aküsü biten ziyaretçiler, bölgede en sık karşılaştığımız durumlardan biridir. Avrupa yakasına ekibimiz talep üzerine yönlendirilir. Aradığınızda feribot ya da 1915 Çanakkale Köprüsü güzergâhına göre varış süresini net olarak bildiririz.",
        ],
    },
    "ezine": {
        "name": "Ezine", "short": "Ezine", "side": "anadolu", "page": "ezine",
        "paras": [
            "Ezine, Çanakkale–İzmir karayolu (D550) üzerinde yer alır. Geyikli ve Dalyan sahilleri ile Bozcaada feribotunun kalktığı Geyikli Yükyeri iskelesi bu ilçededir.",
            "Feribot kuyruğunda beklerken ya da sahildeki yazlıkta uzun süre bekleyen araçlarda akü boşalması sık yaşanır. Ezine merkez, Geyikli ve bağlı köylerde yerinde akü takviyesi ve akü değişimi yapıyoruz.",
        ],
    },
    "gelibolu": {
        "name": "Gelibolu", "short": "Gelibolu", "side": "avrupa", "page": "gelibolu",
        "paras": [
            "Gelibolu, yarımadanın kuzeyinde, Lapseki–Gelibolu feribot hattının Avrupa yakasındaki ayağıdır. 1915 Çanakkale Köprüsü'nün Avrupa yakası bağlantısı ve Bolayır, Evreşe yönündeki Keşan yolu da ilçe sınırlarındadır.",
            "Köprü ve otoyol bağlantıları nedeniyle uzun yoldan gelip burada yolda kalan araçlarla sık karşılaşıyoruz. Gelibolu merkezde ve bağlı köylerde ekibimiz talep üzerine yönlendirilir; aradığınızda varış süresini net olarak söyleriz.",
        ],
    },
    "gokceada": {
        "name": "Gökçeada", "short": "Gökçeada", "side": "ada", "page": "gokceada",
        "paras": [
            "Gökçeada, Türkiye'nin en büyük adasıdır ve araçla ulaşım Eceabat'taki Kabatepe iskelesinden kalkan feribotla sağlanır. Hizmet planlamasını feribot saatlerine göre yaptığımızdan aradığınızda size gerçekçi bir varış zamanı veririz.",
            "Ada yollarında yerleşimler arası mesafeler uzun, servis seçenekleri ise sınırlıdır. Bu yüzden adaya araçla geçmeden önce akünüzü test ettirmenizi öneririz. Akü yaşı 4 yılı geçmişse yolculuk öncesi değişim, adada yolda kalmaktan çok daha zahmetsizdir.",
        ],
    },
    "lapseki": {
        "name": "Lapseki", "short": "Lapseki", "side": "anadolu", "page": "lapseki",
        "paras": [
            "Lapseki, Çanakkale Boğazı'nın Anadolu yakasında, Lapseki–Gelibolu feribot hattının ve 1915 Çanakkale Köprüsü'nün Anadolu ayağının bulunduğu ilçedir. Çanakkale–Bursa karayolu (D200) da Lapseki'den geçer.",
            "Köprü ve feribot trafiği, Çardak ve Umurbey gibi yoğun yerleşimler nedeniyle Lapseki, yolda kalan araçlar için en sık çağrı aldığımız bölgelerden biridir. Lapseki merkezde ve bağlı köylerde yerinde akü takviyesi ve değişimi yapıyoruz.",
        ],
    },
    "yenice": {
        "name": "Yenice", "short": "Yenice", "side": "anadolu", "page": "yenice",
        "paras": [
            "Yenice, ilin en doğusunda, Balıkesir sınırına yakın, ormanlık ve dağlık bir ilçedir. Köyler arası mesafeler uzun ve kışlar soğuktur. Zayıf bir akü burada kolayca yolda bırakabilir.",
            "Orman ve tarım işlerinde kullanılan araçlar ile uzun süre çalıştırılmayan araçlar için yerinde akü takviyesi ve akü değişimi yapıyoruz. Uzak köylerde varış süresi mesafeye göre değişir; aradığınızda net süre bildiririz.",
        ],
    },
}
DISTRICT_ORDER = ["merkez", "ayvacik", "bayramic", "biga", "bozcaada", "can", "eceabat",
                  "ezine", "gelibolu", "gokceada", "lapseki", "yenice"]

# ---------------------------------------------------------------------------
# Yerler: slug -> (görünen ad, [ilçe anahtarları], tür)
# tür: mahalle (merkez mahallesi), yer (köy/belde), nokta (özel nokta), yol
# ---------------------------------------------------------------------------
P = {}
def add(districts, kind, items):
    for slug, name in items:
        P[slug] = {"name": name, "districts": districts, "kind": kind}

add(["merkez"], "mahalle", [
    ("barbaros", "Barbaros"), ("cevatpasa", "Cevatpaşa"), ("cumhuriyet", "Cumhuriyet"),
    ("fatih", "Fatih"), ("fevzipasa", "Fevzipaşa"), ("ismetpasa", "İsmetpaşa"),
    ("istiklal", "İstiklal"), ("kemalpasa", "Kemalpaşa"), ("namikkemal", "Namık Kemal")])
add(["merkez"], "yer", [
    ("kepez", "Kepez"), ("guzelyali", "Güzelyalı"), ("dardanos", "Dardanos"), ("intepe", "İntepe"),
    ("elmacik", "Elmacık"), ("erenkoy", "Erenköy"), ("halileli", "Halileli"), ("isiklar", "Işıklar"),
    ("kalabakli", "Kalabaklı"), ("karacaoren", "Karacaören"), ("kayadere", "Kayadere"),
    ("kemel", "Kemel"), ("kirazli", "Kirazlı"), ("kocalar", "Kocalar"), ("kumkale", "Kumkale"),
    ("musakoy", "Musaköy"), ("ozbek", "Özbek"), ("saricaeli", "Sarıcaeli"),
    ("tevfikiye", "Tevfikiye"), ("yapildak", "Yapıldak")])
add(["ayvacik"], "yer", [
    ("assos", "Assos"), ("ahmetce", "Ahmetçe"), ("babakale", "Babakale"),
    ("buyukhusun", "Büyükhusun"), ("kayalar", "Kayalar"), ("korubasi", "Korubaşı"),
    ("kosedere", "Kösedere"), ("kozlu", "Kozlu"), ("kucukkuyu", "Küçükkuyu"), ("kuruoba", "Kuruoba"),
    ("naldoken", "Naldöken"), ("sapanca", "Sapanca"), ("sazli", "Sazlı"), ("sogutlu", "Söğütlü"),
    ("tasagil", "Taşağıl"), ("tuzla", "Tuzla"), ("yesilyurt", "Yeşilyurt"), ("yukarikoy", "Yukarıköy")])
add(["bayramic"], "yer", [
    ("dagoba", "Dağoba"), ("muratlar", "Muratlar"), ("palamutoba", "Palamutoba")])
add(["biga"], "yer", [
    ("agakoy", "Ağaköy"), ("baliklicesme", "Balıklıçeşme"), ("danisment", "Danişment"),
    ("goktepe", "Göktepe"), ("gumuscay", "Gümüşçay"), ("karabiga", "Karabiga"), ("kemer", "Kemer"),
    ("kozcesme", "Kozçeşme"), ("sinekci", "Sinekçi"), ("yeniciftlik", "Yeniçiftlik"), ("yolindi", "Yolindi")])
add(["can"], "yer", [
    ("dereoba", "Dereoba"), ("etili", "Etili"), ("kocayayla", "Kocayayla"), ("terzialan", "Terzialan")])
add(["eceabat"], "yer", [
    ("alcitepe", "Alçıtepe"), ("behramli", "Behramlı"), ("buyukanafarta", "Büyükanafarta"),
    ("kabatepe", "Kabatepe"), ("kilitbahir", "Kilitbahir"), ("kucukanafarta", "Küçükanafarta"),
    ("seddulbahir", "Seddülbahir"), ("yalova", "Yalova Köyü")])
add(["ezine"], "yer", [
    ("camlica", "Çamlıca"), ("dalyan", "Dalyan"), ("geyikli", "Geyikli"), ("gokcebayir", "Gökçebayır"),
    ("kemalli", "Kemallı"), ("kizilkoy", "Kızılköy"), ("kiziltepe", "Kızıltepe"),
    ("mahmudiye", "Mahmudiye"), ("uvecik", "Üvecik"), ("yahyacavus", "Yahyaçavuş")])
add(["gelibolu"], "yer", [
    ("bayirkoy", "Bayırköy"), ("bolayir", "Bolayır"), ("bolayirgecidi", "Bolayır Geçidi"),
    ("evrese", "Evreşe"), ("guneyli", "Güneyli"), ("karainebeyli", "Karainebeyli"),
    ("kavakkoy", "Kavakköy"), ("kocacesme", "Kocaçeşme"), ("tayfur", "Tayfur"), ("yazicizade", "Yazıcızade")])
add(["lapseki"], "yer", [
    ("alpagut", "Alpagut"), ("cardak", "Çardak"), ("gureci", "Güreci"), ("sevketiye", "Şevketiye"),
    ("subasi", "Subaşı"), ("suluca", "Suluca"), ("umurbey", "Umurbey")])
add(["yenice"], "yer", [("hamdibey", "Hamdibey")])
# Aynı adı taşıyan, birden fazla ilçede bulunan yerleşimler
for slug, name, ds in [
    ("adatepe", "Adatepe", ["ayvacik", "lapseki"]), ("bademli", "Bademli", ["ayvacik", "gokceada"]),
    ("belen", "Belen", ["ezine", "merkez"]), ("camoba", "Çamoba", ["ezine", "yenice"]),
    ("hacikoy", "Hacıköy", ["bayramic", "biga"]), ("kalafat", "Kalafat", ["biga", "merkez"]),
    ("karakoy", "Karaköy", ["bayramic", "yenice"]), ("kulfal", "Kulfal", ["ayvacik", "can"]),
    ("mecidiye", "Mecidiye", ["ezine", "lapseki"]), ("ovacik", "Ovacık", ["biga", "merkez"]),
    ("pinarbasi", "Pınarbaşı", ["bayramic", "ezine"]), ("saraycik", "Saraycık", ["bayramic", "merkez"]),
    ("yenicekoy", "Yeniceköy", ["bayramic", "lapseki"])]:
    P[slug] = {"name": name, "districts": ds, "kind": "yer"}
P["koprugirisi"] = {"name": "1915 Köprü Girişi", "districts": ["lapseki", "gelibolu"], "kind": "nokta"}
P["bursaotoyolu"] = {"name": "Bursa Yolu", "districts": ["lapseki", "biga"], "kind": "yol",
                     "road": "Çanakkale–Bursa karayolu (D200)", "via": "Lapseki ve Biga"}
P["izmirotoyolu"] = {"name": "İzmir Yolu", "districts": ["ezine", "ayvacik"], "kind": "yol",
                     "road": "Çanakkale–İzmir karayolu (D550)", "via": "Ezine ve Ayvacık"}
# İlçesi doğrulanamayan yerler: sayfada ilçe bilgisi verilmez
for slug, name in [("babaoba", "Babaoba"), ("camikebir", "Camikebir"), ("cetmibasi", "Çetmibaşı"),
                   ("cinarlik", "Çınarlık"), ("daridere", "Darıdere"), ("derbent", "Derbent"),
                   ("duragan", "Durağan"), ("esentepe", "Esentepe"), ("gumuscu", "Gümüşcü"),
                   ("hamidiye", "Hamidiye"), ("kizilcik", "Kızılcık"), ("korubuku", "Korubükü"),
                   ("koseobasi", "Köseobası"), ("kumkoyu", "Kumköy"), ("sakarya", "Sakarya"),
                   ("saricay", "Sarıçay"), ("serceler", "Serceler"), ("sirintepe", "Şirintepe"),
                   ("tavsanli", "Tavşanlı")]:
    P[slug] = {"name": name, "districts": [], "kind": "yer"}

# Aynı yerin kopyası olan sayfalar -> ana sayfaya 301
MERGES = {
    "adatepekoyu": "adatepe", "evresebeldesi": "evrese", "gumuscaybeldesi": "gumuscay",
    "karabigabeldesi": "karabiga", "kavakkoybeldesi": "kavakkoy", "mahmudiyekoyu": "mahmudiye",
    "gurecci": "gureci", "geyiklisahil": "geyikli", "guzelyalisahil": "guzelyali",
    "guneylisahil": "guneyli", "dardanossahil": "dardanos",
}

# Sayfası olmayan (ilçe sayfası) ilçeler hariç ilçe sayfaları
for k, d in DISTRICTS.items():
    if d["page"]:
        P[d["page"]] = {"name": d["name"], "districts": [k], "kind": "ilce"}

GUIDES = [
    ("/aku-ariza-belirtileri", "Akü Arıza Belirtileri"),
    ("/aku-mu-alternator-mu-arizali", "Akü mü Alternatör mü Arızalı?"),
    ("/aku-takviyesi-nasil-yapilir", "Akü Takviyesi Nasıl Yapılır?"),
    ("/efb-agm-aku-farki", "EFB ve AGM Akü Farkı"),
    ("/start-stop-aku-nedir", "Start-Stop Akü Nedir?"),
    ("/kis-aylarinda-aku-bakimi", "Kış Aylarında Akü Bakımı"),
    ("/yazin-aku-bakimi", "Yazın Akü Bakımı"),
    ("/aku-omru-kac-yildir", "Akü Ömrü Kaç Yıldır?"),
    ("/aku-isigi-yaniyor-ne-demek", "Akü Işığı Yanıyor Ne Demek?"),
    ("/aku-fiyatlari", "Akü Fiyatları Nasıl Belirlenir?"),
]

# ---------------------------------------------------------------------------
# Türkçe yardımcılar
# ---------------------------------------------------------------------------
LOC_OVERRIDE = {"Yalova Köyü": "Yalova Köyü'nde", "1915 Köprü Girişi": "1915 Köprü girişinde",
                "Bolayır Geçidi": "Bolayır Geçidi'nde", "Çanakkale Merkez": "Çanakkale merkezde",
                "Bursa Yolu": "Bursa yolunda", "İzmir Yolu": "İzmir yolunda",
                "Namık Kemal": "Namık Kemal'de", "İstiklal": "İstiklal'de"}

def lower_tr(s):
    return s.replace("I", "ı").replace("İ", "i").lower()

def locative(name):
    """'Biga' -> "Biga'da", 'Kepez' -> "Kepez'de", 'Ezine' -> "Ezine'de"."""
    if name in LOC_OVERRIDE:
        return LOC_OVERRIDE[name]
    w = lower_tr(name.split()[-1])
    vowels = [c for c in w if c in "aeıioöuü"]
    back = vowels and vowels[-1] in "aıou"
    hard = w[-1] in "fstkçşhp"
    return f"{name}'{'t' if hard else 'd'}{'a' if back else 'e'}"

TR_ORDER = {c: i for i, c in enumerate("0123456789aâbcçdefgğhıiîjklmnoöprsştuüûvyz ")}
def tr_key(s):
    return [TR_ORDER.get(c, 99) for c in lower_tr(s)]

def h(s):
    return html.escape(s, quote=True)

def pick(slug, n, mod):
    return int(hashlib.md5(slug.encode()).hexdigest(), 16) // (n + 1) % mod

def district_names(ds):
    names = [DISTRICTS[d]["short"] if d != "merkez" else "Merkez" for d in ds]
    return " ve ".join(names)

def district_link(d):
    dd = DISTRICTS[d]
    href = f"/{dd['page']}" if dd["page"] else "/hizmet-bolgeleri#merkez"
    return f'<a href="{href}" class="text-warning">{h(dd["name"])}</a>'

# ---------------------------------------------------------------------------
# Ortak parçalar
# ---------------------------------------------------------------------------
def head(title, desc, url, image, jsonld, robots="index, follow"):
    blocks = "\n".join(
        f'    <script type="application/ld+json">\n{json.dumps(j, ensure_ascii=False, indent=2)}\n    </script>'
        for j in jsonld)
    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta name="google-adsense-account" content="ca-pub-8816248752189045">
    <!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-BVKB3TN7JE"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('consent', 'default', {{
    'ad_storage': 'denied',
    'ad_user_data': 'denied',
    'ad_personalization': 'denied',
    'analytics_storage': 'denied'
  }});
  gtag('js', new Date());

  gtag('config', 'G-BVKB3TN7JE');
</script>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8816248752189045" crossorigin="anonymous"></script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{h(title)}</title>
    <meta name="description" content="{h(desc)}">
    <meta name="robots" content="{robots}">
    <link rel="canonical" href="{url}">
    <meta property="og:locale" content="tr_TR">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Akü Takviyecisi">
    <meta property="og:title" content="{h(title)}">
    <meta property="og:description" content="{h(desc)}">
    <meta property="og:url" content="{url}">
    <meta property="og:image" content="{image}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{h(title)}">
    <meta name="twitter:description" content="{h(desc)}">
    <meta name="twitter:image" content="{image}">
    <link rel="shortcut icon" href="/assets/img/favicon.png" type="image/png">
    <link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
    <link rel="manifest" href="/manifest.json">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <link rel="stylesheet" href="/assets/css/style.css?v=8">
{blocks}
</head>
<body>

    <a href="#main-content" class="skip-link">İçeriğe geç</a>
"""

def nav():
    def item(slug, name):
        return f'                                    <li><a class="dropdown-item" href="/{slug}">{h(name)}</a></li>'
    avrupa = "\n".join(item(DISTRICTS[d]["page"], DISTRICTS[d]["name"]) for d in ["eceabat", "gelibolu"])
    anadolu = "\n".join(item(DISTRICTS[d]["page"], DISTRICTS[d]["name"])
                        for d in ["ayvacik", "bayramic", "biga", "bozcaada", "can", "ezine", "gokceada", "lapseki", "yenice"])
    merkez = "\n".join(item(s, P[s]["name"]) for s in ["fatih", "kepez", "barbaros", "cumhuriyet", "istiklal", "namikkemal"])
    return f"""
    <nav class="navbar navbar-expand-lg navbar-dark bg-black sticky-top border-bottom border-secondary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="/assets/img/logo.png?v=1" alt="Akü Takviyecisi" height="100">
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNavbar" aria-label="Menüyü aç">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="mainNavbar" style="background: #000;">
                <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
                    <li class="nav-item"><a class="nav-link" href="/">Ana Sayfa</a></li>
                    <li class="nav-item"><a class="nav-link" href="/hakkimizda">Hakkımızda</a></li>
                    <li class="nav-item"><a class="nav-link" href="/blog">Blog</a></li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">Bölgelerimiz</a>
                        <ul class="dropdown-menu dropdown-menu-dark">
                            <li><a class="dropdown-item" href="/hizmet-bolgeleri">Tüm Hizmet Bölgeleri</a></li>
                            <li class="dropdown-submenu">
                                <a class="dropdown-item dropdown-toggle" href="#">Avrupa Yakası</a>
                                <ul class="dropdown-menu dropdown-menu-dark">
{avrupa}
                                </ul>
                            </li>
                            <li class="dropdown-submenu">
                                <a class="dropdown-item dropdown-toggle" href="#">Anadolu Yakası</a>
                                <ul class="dropdown-menu dropdown-menu-dark">
{anadolu}
                                </ul>
                            </li>
                            <li class="dropdown-submenu">
                                <a class="dropdown-item dropdown-toggle" href="#">Çanakkale Merkez</a>
                                <ul class="dropdown-menu dropdown-menu-dark">
{merkez}
                                </ul>
                            </li>
                        </ul>
                    </li>
                    <li class="nav-item"><a class="nav-link" href="/sss">S.S.S</a></li>
                    <li class="nav-item"><a class="nav-link" href="/gizlilik-politikasi">Gizlilik</a></li>
                    <li class="nav-item"><a class="nav-link" href="/iletisim">İletişim</a></li>
                </ul>
            </div>
        </div>
    </nav>
"""

def foot(wa_text):
    from urllib.parse import quote_plus
    return f"""
    <footer style="background:#000; border-top:1px solid #333; padding:24px 16px; text-align:center;">
        <p style="color:#888; font-size:13px; margin:0;"><a href="/hizmet-bolgeleri" class="text-secondary">Hizmet Bölgeleri</a> · <a href="/blog" class="text-secondary">Blog</a> · <a href="/iletisim" class="text-secondary">İletişim</a></p>
        <p style="color:#888; font-size:13px; margin-top:8px; margin-bottom:0;">© 2026 Akü Takviyecisi — Çanakkale 7/24 Akü Servisi ve Yol Yardım</p>
    </footer>

    <div class="cta-container">
        <a href="tel:{PHONE_TEL}" class="cta-btn btn-call">📞 ACİL EKİP ÇAĞIR</a>
        <a href="https://wa.me/{WA}?text={quote_plus(wa_text)}" target="_blank" class="cta-btn btn-whatsapp" rel="noopener noreferrer">💬 WP KONUM GÖNDER</a>
    </div>

    <script src="/assets/js/site.js?v=6"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
    <script>
    document.querySelectorAll('.dropdown-submenu > a').forEach(function(element) {{
        element.addEventListener('click', function(e) {{
            if (window.innerWidth < 992) {{
                e.preventDefault();
                e.stopPropagation();
                var submenu = this.nextElementSibling;
                if (submenu) submenu.classList.toggle('show');
            }}
        }});
    }});
    </script>
</body>
</html>
"""

def breadcrumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u}
                                for i, (n, u) in enumerate(items)]}

def breadcrumb_html(items):
    lis = []
    for i, (n, u) in enumerate(items):
        if i == len(items) - 1:
            lis.append(f'<li class="breadcrumb-item text-secondary active" aria-current="page">{h(n)}</li>')
        else:
            lis.append(f'<li class="breadcrumb-item"><a href="{u}" class="text-warning text-decoration-none">{h(n)}</a></li>')
    return ('        <nav aria-label="breadcrumb" class="mb-4">\n'
            '            <ol class="breadcrumb" style="background:transparent; padding:0; margin:0;">\n'
            + "\n".join("                " + l for l in lis) + "\n            </ol>\n        </nav>")

def service_ld(name, url, desc, area):
    return {"@context": "https://schema.org", "@type": "Service",
            "serviceType": "Yerinde akü takviyesi ve akü değişimi",
            "name": f"{name} akü takviye ve akü değişimi", "url": url, "description": desc,
            "provider": {"@type": "AutoRepair", "@id": SITE + "/#business", "name": "Akü Takviyecisi",
                         "telephone": PHONE_TEL, "url": SITE + "/"},
            "areaServed": area}

CHECKLIST = """                <h2 class="h4 mt-4">Ararken Hangi Bilgileri Vermelisiniz?</h2>
                <p>Ekibin doğru ekipmanla ve en kısa sürede gelmesi için şu bilgiler işimizi çok kolaylaştırır:</p>
                <ul>
                    <li><strong>Konum:</strong> WhatsApp'tan canlı ya da sabit konum gönderin. Köy yollarında ve sahil yerleşimlerinde adres tarifinden çok daha hızlıdır.</li>
                    <li><strong>Araç bilgisi:</strong> Marka, model ve yıl. Değişim gerekirse doğru amperde aküyü yanımızda getiririz.</li>
                    <li><strong>Start-stop özelliği:</strong> Varsa araca EFB ya da AGM akü gerekir; normal akü takılmamalıdır.</li>
                    <li><strong>Belirti:</strong> Marşa basınca tık sesi mi geliyor, motor ağır mı dönüyor, yoksa gösterge hiç mi yanmıyor? Bu bilgi takviyenin yeterli olup olmayacağını önceden kestirmemizi sağlar.</li>
                </ul>
                <h2 class="h4 mt-4">Ekip Gelene Kadar</h2>
                <ul>
                    <li>Marşa art arda basmayın. Boşalmış aküyü daha da zorlar ve marş motorunu ısıtır.</li>
                    <li>Farları, klimayı ve radyoyu kapatın; varsa şarjdaki cihazları çıkarın.</li>
                    <li>Yol kenarındaysanız dörtlüleri yakın, reflektif yeleği giyin ve üçgen reflektörü koyun.</li>
                    <li>Akü kutusunda şişme, çatlak ya da asit kokusu varsa takviye denemeyin; bunu bize telefonda söyleyin.</li>
                </ul>"""

def services_block(name):
    return f"""                <h2 class="h4 mt-4">{h(name)} İçin Verdiğimiz Hizmetler</h2>
                <ul>
                    <li><strong>Yerinde akü takviyesi:</strong> Akü boşaldıysa profesyonel booster cihazıyla aracınızı bulunduğu yerde çalıştırırız. <a href="/yol-yardim" class="text-warning">Yol yardım hizmetimiz</a> hakkında detaylı bilgi alabilirsiniz.</li>
                    <li><strong>Yerinde akü değişimi:</strong> Akü ömrünü tamamladıysa aracınıza uygun amper ve tipte yeni aküyü, hafıza koruma cihazı bağlayarak yerinde takarız. <a href="/aku-degisimi" class="text-warning">Akü değişimi süreci</a> sayfasında adımları görebilirsiniz.</li>
                    <li><strong>Akü ve şarj testi:</strong> Sorunun aküde mi yoksa alternatörde mi olduğunu ölçerek belirleriz; gereksiz yere akü değiştirmeyiz.</li>
                    <li><strong>Start-stop araçlar:</strong> EFB ve AGM akü gerektiren araçlarda doğru akü tipini kullanırız.</li>
                    <li><strong>Eski akü:</strong> Değiştirdiğimiz eski aküyü geri dönüşüme gönderir, <a href="/aku-geri-donusum-hurda-deger" class="text-warning">hurda değerini</a> fiyattan düşeriz.</li>
                </ul>"""

def guides_block(slug):
    start = pick(slug, 3, len(GUIDES))
    chosen = [GUIDES[(start + i * 3) % len(GUIDES)] for i in range(4)]
    btns = "\n".join(f'                <a href="{u}" class="btn btn-outline-warning btn-sm">{h(t)}</a>' for u, t in chosen)
    return f"""        <div class="mt-4 p-4 bg-dark border border-secondary rounded">
            <h2 class="text-white h5 mb-3">Faydalı Rehberler</h2>
            <div class="d-flex flex-wrap gap-2">
{btns}
            </div>
        </div>"""

def members(d):
    return sorted([s for s, p in P.items() if d in p["districts"] and p["kind"] in ("yer", "mahalle", "nokta", "yol")],
                  key=lambda s: tr_key(P[s]["name"]))

def link_list(slugs):
    return ", ".join(f'<a href="/{s}" class="text-warning">{h(P[s]["name"])}</a>' for s in slugs)

# ---------------------------------------------------------------------------
# Sayfa üreticileri
# ---------------------------------------------------------------------------
def render_place(slug):
    p = P[slug]
    name, ds, kind = p["name"], p["districts"], p["kind"]
    url = f"{SITE}/{slug}"
    img_n = pick(slug, 1, 9) + 1
    image = f"{SITE}/uploads/aku/{img_n}.webp"

    if kind == "ilce":
        d = ds[0]
        dd = DISTRICTS[d]
        title = f"{name} Akücü | 7/24 Akü Takviye ve Akü Değişimi"
        desc = f"{locative(name)} 7/24 yerinde akü takviyesi ve akü değişimi. Mobil ekibimiz {name} merkez ve bağlı köylere gelir, aracınızı yerinde çalıştırır. Hemen arayın: {PHONE_DISPLAY}"
        h1 = f"{name} Akü Takviye ve Yerinde Akü Değişimi"
        crumbs = [("Ana Sayfa", "/"), ("Hizmet Bölgeleri", "/hizmet-bolgeleri"), (name, f"/{slug}")]
        intro = "\n".join(f'                <p>{h(t)}</p>' for t in dd["paras"])
        mem = [s for s in members(d) if s != slug]
        near = (f"""                <h2 class="h4 mt-4">{h(name)} İlçesinde Hizmet Verdiğimiz Yerler</h2>
                <p>{link_list(mem)}{' ve ilçeye bağlı diğer tüm köy ve mahalleler.' if mem else ''}</p>""" if mem else
                f"""                <h2 class="h4 mt-4">Hizmet Alanı</h2>
                <p>{h(locative(name))} adanın tamamında hizmet veriyoruz.</p>""")
        area = {"@type": "AdministrativeArea", "name": f"{name}, Çanakkale"}
    else:
        if kind == "yol":
            title = f"{name} Akü Takviye | {p['road'].split(' (')[0]} Yol Yardım"
            desc = f"{p['road']} üzerinde {p['via']} güzergâhında aküsü biten araçlara 7/24 yerinde akü takviyesi ve akü değişimi. Konum gönderin: {PHONE_DISPLAY}"
            h1 = f"{p['road']}: Akü Takviye ve Yol Yardım"
            intro = (f'                <p>{h(p["road"])}, {h(p["via"])} üzerinden geçen ve yoğun kullanılan bir güzergâhtır. Uzun yolda akü ya da şarj sistemi arızası nedeniyle yolda kalırsanız mobil ekibimiz bulunduğunuz noktaya gelir.</p>\n'
                     f'                <p>Karayolunda kilometre taşı, yakındaki bir benzinlik ya da tabela adı vermek yerine WhatsApp\'tan canlı konum göndermeniz en hızlı yöntemdir. Aracınızı güvenli şekilde emniyet şeridine alın ve araç dışında, bariyerin arkasında bekleyin.</p>')
        elif kind == "nokta":
            title = f"{name} Akücü | 7/24 Acil Akü Takviye"
            desc = f"1915 Çanakkale Köprüsü bağlantı yollarında aküsü biten araçlara 7/24 yerinde akü takviyesi ve değişimi. Lapseki ve Gelibolu yakasına mobil ekip: {PHONE_DISPLAY}"
            h1 = "1915 Çanakkale Köprüsü Girişi: Akü Takviye ve Yol Yardım"
            intro = ('                <p>1915 Çanakkale Köprüsü, Anadolu yakasında Lapseki\'yi Avrupa yakasında Gelibolu\'ya bağlar. Köprü ve otoyol bağlantı yollarında aküsü biten ya da şarj sistemi arızalanan araçlar için yerinde akü takviyesi ve değişimi yapıyoruz.</p>\n'
                     '                <p>Otoyolda yolda kaldıysanız aracı emniyet şeridine alın, dörtlüleri yakın ve bariyerin arkasında bekleyin. Ekibimize hangi yakada (Lapseki ya da Gelibolu tarafı) ve hangi yönde olduğunuzu bildirin. En hızlısı WhatsApp\'tan canlı konum göndermektir.</p>')
        else:
            title = f"{name} Akücü | 7/24 Acil Akü Takviye"
            if len(ds) == 1:
                dn = DISTRICTS[ds[0]]["name"]
                where = f"{name} ({dn})" if ds[0] != "merkez" else f"{name} (Çanakkale Merkez)"
                desc = f"{where} ve çevresinde 7/24 yerinde akü takviyesi ve akü değişimi. Mobil ekip adresinize gelir, aracınızı yerinde çalıştırır. Hemen arayın: {PHONE_DISPLAY}"
                rel = ("Çanakkale merkezdeki mahallelerden biridir" if kind == "mahalle"
                       else f"Çanakkale'nin {dn} ilçesine bağlı bir yerleşimdir" if ds[0] != "merkez"
                       else "Çanakkale Merkez ilçesine bağlı bir yerleşimdir")
                intro = f'                <p>{h(name)}, {h(rel)}. {h(name)} ve çevresinde aküsü biten ya da ömrünü tamamlayan araçlar için mobil ekibimiz adresinize gelir; akü takviyesini ya da akü değişimini yerinde yapar.</p>'
            elif len(ds) > 1:
                desc = f"{name} ({district_names(ds)}) ve çevresinde 7/24 yerinde akü takviyesi ve akü değişimi. Mobil ekip adresinize gelir. Hemen arayın: {PHONE_DISPLAY}"
                intro = (f'                <p>Çanakkale\'de {h(name)} adını taşıyan birden fazla yerleşim var: {h(district_names(ds))} ilçelerinde. İkisinde de yerinde akü takviyesi ve akü değişimi yapıyoruz.</p>\n'
                         f'                <p>Bizi ararken hangi {h(name)} olduğunu, yani bağlı olduğu ilçeyi belirtmeniz ya da WhatsApp\'tan konum göndermeniz ekibin doğru adrese yönlenmesini hızlandırır.</p>')
            else:
                desc = f"{name} ve çevresinde 7/24 yerinde akü takviyesi ve akü değişimi. Mobil ekip adresinize gelir, aracınızı yerinde çalıştırır. Hemen arayın: {PHONE_DISPLAY}"
                intro = f'                <p>{h(name)} ve çevresinde aküsü biten ya da ömrünü tamamlayan araçlar için mobil ekibimiz adresinize gelir; akü takviyesini ya da akü değişimini yerinde yapar. Bizi ararken bulunduğunuz yeri ve bağlı olduğu ilçeyi belirtmeniz ya da WhatsApp\'tan konum göndermeniz ekibin doğru adrese yönlenmesini hızlandırır.</p>'
            h1 = f"{name} Akü Takviye ve Yerinde Akü Değişimi"
        # Bağlı ilçenin bölgesel notu
        if ds and kind != "nokta":
            for d in ds[:1]:
                intro += f'\n                <p>{h(DISTRICTS[d]["paras"][0])}</p>'
        crumbs = [("Ana Sayfa", "/"), ("Hizmet Bölgeleri", "/hizmet-bolgeleri")]
        if len(ds) == 1:
            d = ds[0]
            crumbs.append((DISTRICTS[d]["name"], f"/{DISTRICTS[d]['page']}" if DISTRICTS[d]["page"] else "/hizmet-bolgeleri#merkez"))
        crumbs.append((name, f"/{slug}"))
        parts = []
        for d in ds:
            mem = [s for s in members(d) if s != slug]
            label = DISTRICTS[d]["name"]
            parts.append(f'                <p><strong>{h(label)}:</strong> {district_link(d)}'
                         + (f' · {link_list(mem)}' if mem else '') + '</p>')
        if not ds:
            parts.append('                <p>Çanakkale\'nin 12 ilçesinin tamamında hizmet veriyoruz. Bulunduğunuz ilçeyi <a href="/hizmet-bolgeleri" class="text-warning">hizmet bölgeleri</a> sayfasından seçebilirsiniz.</p>')
        near = '                <h2 class="h4 mt-4">Yakındaki Hizmet Noktalarımız</h2>\n' + "\n".join(parts)
        area = {"@type": "Place", "name": f"{name}, Çanakkale"}

    jsonld = [service_ld(name, url, desc, area), breadcrumb_ld(crumbs)]
    wa_text = f"Merhaba Akü Takviyecisi, {locative(name) if kind != 'yol' else name + ' üzerinde'} aracım için akü desteği istiyorum. Konumumu paylaşıyorum:"
    body = f"""{nav()}
    <div class="max-wrapper py-5" id="main-content">
{breadcrumb_html(crumbs)}

        <article class="bg-dark border border-secondary rounded p-4">
            <div class="text-warning fw-bold mb-2">7/24 Mobil Akü Servisi</div>
            <h1 class="text-white fw-bold mb-3">{h(h1)}</h1>
            <img src="/uploads/aku/{img_n}.webp" alt="{h(name)} yerinde akü takviye ve akü değişimi" class="img-fluid rounded mb-4" style="width:100%; max-height:340px; object-fit:cover;" loading="lazy">
            <div class="text-light">
{intro}

            <div class="p-3 rounded border border-warning my-4" style="background: rgba(245,158,11,0.08);">
                <p class="text-light mb-2"><strong>Aracınız çalışmıyor mu?</strong> {h(PHONE_DISPLAY)} numarasını arayın ya da WhatsApp'tan konum gönderin. Aradığınızda tahmini varış süresini ve fiyatı net olarak söyleriz.</p>
                <a href="tel:{PHONE_TEL}" class="btn btn-warning btn-sm me-2">📞 Hemen Ara</a>
                <a href="https://wa.me/{WA}" target="_blank" rel="noopener noreferrer" class="btn btn-success btn-sm">💬 WhatsApp</a>
            </div>

{services_block(name)}
{CHECKLIST}
{near}
            </div>
        </article>

{guides_block(slug)}
    </div>
"""
    return head(title, desc, url, image, jsonld) + body + foot(wa_text)


def render_hub():
    url = f"{SITE}/hizmet-bolgeleri"
    title = "Hizmet Bölgeleri | Çanakkale'nin 12 İlçesinde Akü Takviye"
    desc = "Akü Takviyecisi'nin hizmet verdiği tüm Çanakkale ilçeleri, köyleri ve mahalleleri. Merkez, Ayvacık, Bayramiç, Biga, Bozcaada, Çan, Eceabat, Ezine, Gelibolu, Gökçeada, Lapseki, Yenice."
    crumbs = [("Ana Sayfa", "/"), ("Hizmet Bölgeleri", "/hizmet-bolgeleri")]
    sections = []
    side_label = {"anadolu": "Anadolu yakası", "avrupa": "Avrupa yakası (Gelibolu Yarımadası)", "ada": "Ada ilçesi"}
    for d in DISTRICT_ORDER:
        dd = DISTRICTS[d]
        mem = [s for s in members(d)]
        title_link = (f'<a href="/{dd["page"]}" class="text-warning text-decoration-none">{h(dd["name"])}</a>'
                      if dd["page"] else h(dd["name"]))
        sections.append(f"""            <section id="{d}" class="mb-4">
                <h2 class="h4 text-white">{title_link} <small class="text-secondary fs-6">· {side_label[dd['side']]}</small></h2>
                <p class="text-secondary">{h(dd['paras'][0])}</p>
                {'<p>' + link_list(mem) + '</p>' if mem else ''}
            </section>""")
    others = sorted([s for s, p in P.items() if not p["districts"]], key=lambda s: tr_key(P[s]["name"]))
    sections.append(f"""            <section id="diger" class="mb-4">
                <h2 class="h4 text-white">Diğer Yerleşimler</h2>
                <p>{link_list(others)}</p>
            </section>""")
    jsonld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Hizmet Bölgeleri", "url": url,
               "description": desc}, breadcrumb_ld(crumbs)]
    body = f"""{nav()}
    <div class="max-wrapper py-5" id="main-content">
{breadcrumb_html(crumbs)}
        <article class="bg-dark border border-secondary rounded p-4 text-light">
            <h1 class="text-white fw-bold mb-3">Hizmet Bölgelerimiz</h1>
            <p class="fs-5 text-secondary">Çanakkale merkez ve 11 ilçede, bu ilçelere bağlı köy ve mahallelerde 7/24 yerinde akü takviyesi ve akü değişimi yapıyoruz. Anadolu yakasında gezici ekiplerimiz sahadadır. Avrupa yakasına (Gelibolu ve Eceabat) ve adalara (Bozcaada, Gökçeada) ekip talep üzerine yönlendirilir; aradığınızda varış süresini net olarak söyleriz.</p>
{chr(10).join(sections)}
        </article>
    </div>
"""
    return head(title, desc, url, f"{SITE}/assets/img/og-image.png", jsonld) + body + foot(
        "Merhaba Akü Takviyecisi, akü desteği istiyorum. Konumumu paylaşıyorum:")


def build_sitemap(location_slugs):
    old = {}
    sm = os.path.join(ROOT, "sitemap.xml")
    if os.path.exists(sm):
        for loc, lm in re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", open(sm, encoding="utf-8").read()):
            old[loc] = lm
    pages = []
    for f in sorted(os.listdir(ROOT)):
        if not f.endswith(".html") or f in ("404.html",):
            continue
        slug = f[:-5]
        if slug in MERGES:  # vercel.json ile 301 yönlendirilen kopya sayfalar
            continue
        loc = SITE + "/" if slug == "index" else f"{SITE}/{slug}"
        if slug in location_slugs or slug == "hizmet-bolgeleri":
            lastmod = TODAY
        else:
            lastmod = old.get(loc, TODAY)
        if slug == "index":
            pr, cf = "1.0", "daily"
        elif slug == "hizmet-bolgeleri" or (slug in P and P[slug]["kind"] == "ilce"):
            pr, cf = "0.8", "monthly"
        elif slug in P:
            pr, cf = "0.5", "monthly"
        elif slug == "blog":
            pr, cf = "0.7", "weekly"
        else:
            pr, cf = "0.6", "monthly"
        pages.append((0 if slug == "index" else 1, loc, lastmod, cf, pr))
    pages.sort(key=lambda x: (x[0], x[1]))
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for _, loc, lm, cf, pr in pages:
        out.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lm}</lastmod>\n    <changefreq>{cf}</changefreq>\n    <priority>{pr}</priority>\n  </url>")
    out.append("</urlset>\n")
    open(sm, "w", encoding="utf-8", newline="\n").write("\n".join(out))
    return len(pages)


def main():
    for slug in P:
        with open(os.path.join(ROOT, f"{slug}.html"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(render_place(slug))
    with open(os.path.join(ROOT, "hizmet-bolgeleri.html"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_hub())
    n = build_sitemap(set(P))
    print(f"{len(P)} konum sayfası + hub üretildi, {len(MERGES)} kopya sayfa sitemap dışı (301), sitemap: {n} URL")


if __name__ == "__main__":
    main()
