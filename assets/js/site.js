let wizardData = { hizmet: "", startstop: "Belirtilmedi", amper: "Belirtilmedi", marka: "", konum: "" };

function scrollToWizard() { document.getElementById('akuSihirbazi').scrollIntoView({ behavior: 'smooth' }); }

function selectOption(key, value, currentStep) {
    wizardData[key] = value;
    const stepDiv = document.getElementById(`step${currentStep}`);
    const cards = stepDiv.querySelectorAll('.option-card');
    cards.forEach(card => { if(card.innerText.includes(value) || card.innerText === value) { card.classList.add('selected'); } else { card.classList.remove('selected'); } });

    if (currentStep === 1) {
        if (value.includes("Değişimi")) {
            document.getElementById('degisimSorulari').style.display = "block";
            document.getElementById('takviyeSorulari').style.display = "none";
        } else {
            document.getElementById('degisimSorulari').style.display = "none";
            document.getElementById('takviyeSorulari').style.display = "block";
            wizardData.startstop = "Takviye Hizmeti (Gerekmiyor)";
        }
        nextStep(2);
    } else if (currentStep === 2) {
        if (!wizardData.hizmet.includes("Değişimi") || (wizardData.startstop !== "Belirtilmedi" && wizardData.amper !== "Belirtilmedi")) { nextStep(3); }
    }
}

function nextStep(stepNumber) {
    document.querySelectorAll('.wizard-step').forEach(s => s.classList.remove('active'));
    document.getElementById(`step${stepNumber}`).classList.add('active');
    document.getElementById('wizardProgress').style.width = `${(stepNumber / 4) * 100}%`;
}

function prevStep(stepNumber) {
    document.querySelectorAll('.wizard-step').forEach(s => s.classList.remove('active'));
    document.getElementById(`step${stepNumber}`).classList.add('active');
    document.getElementById('wizardProgress').style.width = `${(stepNumber / 4) * 100}%`;
}

function processStep3() {
    wizardData.marka = document.getElementById('wizMarka').value || "Belirtilmedi";
    wizardData.konum = document.getElementById('wizKonum').value || "Belirtilmedi";
    if(!wizardData.hizmet.includes("Değişimi")) { wizardData.amper = wizardData.amper_takviye || "Belirtilmedi"; }

    document.getElementById('summaryBox').innerHTML = `
                🔄 <b>Hizmet:</b> ${wizardData.hizmet}<br>
                🚗 <b>Araç:</b> ${wizardData.marka}<br>
                ⚡ <b>Amper:</b> ${wizardData.amper}<br>
                ⚙️ <b>Start-Stop:</b> ${wizardData.startstop}<br>
                📍 <b>Konum:</b> ${wizardData.konum}
    `;

            // 💬 MADDE 2: WHATSAPP ŞABLONUNU HAZIR METİN HALİNE GETİRDİK
    const waMessage = `Merhaba Jet Akü Ustası, web sitenizdeki akü sihirbazından fiyat teklifi almak istiyorum:\n\n` +
`• Hizmet: ${wizardData.hizmet}\n` +
`• Araç Marka/Model: ${wizardData.marka}\n` +
`• Akü Amperi: ${wizardData.amper}\n` +
`• Start-Stop Durumu: ${wizardData.startstop}\n` +
`• Konumum: ${wizardData.konum}`;

document.getElementById('whatsappWizLink').href = `https://wa.me/905551663380?text=${encodeURIComponent(waMessage)}`;
nextStep(4);
}

const districts = [
    { name: "Ayvacık", region: "anadolu", seo: "ayvacik" }, { name: "Eceabat", region: "avrupa", seo:"eceabat" }, { name: "Bayramiç", region: "anadolu", seo:"bayramic" },
    { name: "Gelibolu", region: "avrupa", seo: "gelibolu" }, { name: "Biga", region: "anadolu", seo:"biga" }, { name: "Bozcaada", region: "anadolu", seo:"bozcaada" },
    { name: "Çan", region: "anadolu", seo:"can" }, { name: "Ezine", region: "anadolu", seo:"ezine" }, { name: "Gökçeada", region: "anadolu", seo:"gokceada" },
    { name: "Lapseki", region: "anadolu", seo:"lapseki" }, { name: "Yenice", region: "anadolu", seo:"yenice" },
    { name: "Kepez", region: "anadolu", seo: "kepez" }, { name: "Geyikli", region: "anadolu", seo: "geyikli" },
    { name: "Karabiga", region: "anadolu", seo: "karabiga" }, { name: "Çardak", region: "anadolu", seo: "cardak" },
    { name: "Umurbey", region: "anadolu", seo: "umurbey" },
    { name: "Küçükkuyu", region: "anadolu", seo: "kucukkuyu" }, { name: "Assos", region: "anadolu", seo: "assos" },
    { name: "Güzelyalı", region: "anadolu", seo: "guzelyali" }, { name: "Dardanos", region: "anadolu", seo: "dardanos" },
    { name: "Gümüşçay", region: "anadolu", seo: "gumuscay" }
];

function renderCards(data) {
    const grid = document.getElementById('districtGrid'); if(!grid) return; grid.innerHTML = "";
    data.forEach(item => {
        const badgeClass = item.region === 'avrupa' ? 'badge-avrupa' : 'badge-anadolu';
        const statusText = item.region === 'anadolu' ? 'AKTİF MOBİL EKİP' : 'TALEP ÜZERİNE SERVİS';
        const statusClass = item.region === 'anadolu' ? 'status-active' : 'status-request';
        grid.innerHTML += `<div class="district-card" onclick="goToLocation('${item.seo}', '${item.region}')"><div class="card-title">${item.name}</div><span class="card-badge ${badgeClass}">${item.region}</span><div class="card-status ${statusClass}">${statusText}</div></div>`;
    });
}

function toggleMenu() { document.getElementById('navMenu').classList.toggle('active'); }
function toggleSubMenu(id, e) { if (window.innerWidth <= 768) { if(e) e.stopPropagation(); document.getElementById(id).classList.toggle('mobile-open'); } }
function filterRegion(region, btn) { document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active')); btn.classList.add('active'); if(region === 'tum') { renderCards(districts); } else { renderCards(districts.filter(d => d.region === region)); } }
function searchDistricts() { renderCards(districts.filter(d => d.name.toLowerCase().includes(document.getElementById('liveSearch').value.toLowerCase()))); }
function goToLocation(name, reg) { window.location.href = `./${encodeURIComponent(name)}`; }
function goToBrand(brandName) {
    const markaInput = document.getElementById('wizMarka');
    if (markaInput) { markaInput.value = brandName + " "; }
    scrollToWizard();
}

window.onload = function() {
    renderCards(districts);
    const avrupaMenu = document.getElementById('avrupaSubDropdown'); const anadoluMenu = document.getElementById('anadoluSubDropdown');
    if(avrupaMenu && anadoluMenu) {
        districts.sort((a,b) => a.name.localeCompare(b.name, 'tr')).forEach(item => {
            const liHTML = `<li><a class="dropdown-link" onclick="goToLocation('${item.seo}', '${item.region}')">${item.name}</a></li>`;
            if(item.region === 'avrupa') { avrupaMenu.innerHTML += liHTML; } else { anadoluMenu.innerHTML += liHTML; }
        });
    }
};

// 🔍 Sayfa H1 başlığına göre dinamik usta mesajı oluşturan fonksiyon
function getDynamicMessage() {
    const h1 = document.querySelector('h1');
    const headingText = h1 ? h1.textContent.trim().replace(/\s+/g, ' ') : '';
    
    // Anasayfa veya boş durumlar için varsayılan mesaj
    if (!headingText || headingText.includes("Sıkça") || headingText.includes("İletişim") || headingText.includes("Hakkımızda")) {
        return "Merhaba Jet Akü Ustası, yolda kaldım. Yol yardım ve fiyat teklifi almak istiyorum.";
    }
    
    return `Merhaba Jet Akü Ustası, ${headingText} hizmetiniz için yazıyorum.`;
}

// 📍 GPS Konumunu WhatsApp Mesajına Ekleyen Uber-Tarzı Fonksiyon
function shareGPSLocation() {
    const baseMsg = getDynamicMessage();
    const defaultUrl = `https://wa.me/905551663380?text=${encodeURIComponent(baseMsg)}`;
    
    if (navigator.geolocation) {
        // Butonlardaki yazıyı yükleniyor durumuna getir
        const buttons = document.querySelectorAll('.sub-whatsapp-btn, .btn-whatsapp, .floating-whatsapp');
        const originalTexts = [];
        buttons.forEach((btn, index) => {
            originalTexts[index] = btn.innerHTML;
            if (!btn.classList.contains('floating-whatsapp')) {
                btn.innerHTML = "📍 Konumunuz Bulunuyor...";
            }
        });
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                const mapLink = `https://maps.google.com/?q=${lat},${lng}`;
                const gpsMessage = `${baseMsg} Canlı Harita Konumum: ${mapLink}`;
                const waUrl = `https://wa.me/905551663380?text=${encodeURIComponent(gpsMessage)}`;
                
                // Buton yazılarını sıfırla
                buttons.forEach((btn, index) => {
                    btn.innerHTML = originalTexts[index];
                });
                
                // WhatsApp'a yönlendir
                window.open(waUrl, '_blank');
            },
            function(error) {
                console.log("GPS hatası alındı, varsayılan WhatsApp yönlendirmesi yapılıyor:", error);
                buttons.forEach((btn, index) => {
                    btn.innerHTML = originalTexts[index];
                });
                window.open(defaultUrl, '_blank');
            },
            { enableHighAccuracy: true, timeout: 6000, maximumAge: 0 }
        );
    } else {
        window.open(defaultUrl, '_blank');
    }
}

// ⏱️ Saat bazlı Nöbetçi Ekip durum göstergesi güncelleme
function updateLiveStatusDot() {
    const statusTextEl = document.querySelector('.navbar-status span:last-child');
    if (!statusTextEl) return;
    
    const currentHour = new Date().getHours();
    
    // Gece Modu: 20:00 - 08:00
    if (currentHour >= 20 || currentHour < 8) {
        statusTextEl.textContent = "7/24 GECE NÖBETÇİ EKİPLER AKTİF";
        const dot = document.querySelector('.status-dot');
        if (dot) {
            dot.style.background = "#10b981";
            dot.style.boxShadow = "0 0 12px #10b981";
        }
    } else {
        statusTextEl.textContent = "7/24 GEZİCİ EKİPLER SAHADA";
    }
}

// Sayfa yüklendiğinde butonları dinle ve saat durumunu güncelle
document.addEventListener('DOMContentLoaded', () => {
    updateLiveStatusDot();
    injectThemeToggle();
    
    // Hızlı WhatsApp butonlarını bağla
    document.querySelectorAll('.sub-whatsapp-btn, .btn-whatsapp').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            shareGPSLocation();
        });
    });
    
    // Yüzen WhatsApp butonunu otomatik enjekte et
    if (!document.querySelector('.floating-whatsapp')) {
        const floatWA = document.createElement('a');
        floatWA.href = '#';
        floatWA.className = 'floating-whatsapp';
        floatWA.innerHTML = '💬';
        floatWA.title = '7/24 Acil WhatsApp Konum Gönder';
        floatWA.addEventListener('click', (e) => {
            e.preventDefault();
            shareGPSLocation();
        });
        document.body.appendChild(floatWA);
    }
    
    // Acil Arama Butonunu periyodik sars (Shake)
    setInterval(() => {
        const btn = document.querySelector('.emergency-pulse-btn');
        if (btn) {
            btn.classList.add('shake-active');
            setTimeout(() => {
                btn.classList.remove('shake-active');
            }, 700);
        }
    }, 7000);
});

// ♿ Erişilebilirlik - Yazı Boyutu Ayarlama
let textScale = 1.0;
function changeTextSize(action) {
    if (action === 'up') {
        if (textScale < 1.25) textScale += 0.05;
    } else if (action === 'down') {
        if (textScale > 0.90) textScale -= 0.05;
    }
    document.documentElement.style.fontSize = `${textScale * 100}%`;
}

// 📱 GPS Konum Destekli Acil SMS Gönderme
function sendSMSLocation() {
    const phone = "+905551663380";
    const baseMsg = getDynamicMessage();
    
    if (navigator.geolocation) {
        const btn = document.querySelector('.sub-sms-btn');
        const originalText = btn ? btn.innerHTML : "";
        if (btn) btn.innerHTML = "📍 Konum Aranıyor...";
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                const mapLink = `https://maps.google.com/?q=${lat},${lng}`;
                const msg = `${baseMsg} Konumum: ${mapLink}`;
                if (btn) btn.innerHTML = originalText;
                window.location.href = `sms:${phone}?body=${encodeURIComponent(msg)}`;
            },
            function(err) {
                console.log("SMS Geolocation failed, using default message");
                if (btn) btn.innerHTML = originalText;
                window.location.href = `sms:${phone}?body=${encodeURIComponent(baseMsg)}`;
            },
            { enableHighAccuracy: true, timeout: 5000 }
        );
    } else {
        window.location.href = `sms:${phone}?body=${encodeURIComponent(baseMsg)}`;
    }
}

// ☀️ / 🌙 Aydınlık & Karanlık Tema Değiştirici Fonksiyonlar
function toggleTheme() {
    const body = document.body;
    body.classList.toggle('light-theme');
    
    const themeBtn = document.querySelector('.theme-toggle-btn');
    const isLight = body.classList.contains('light-theme');
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
    
    if (themeBtn) {
        themeBtn.innerHTML = isLight ? '🌙' : '☀️';
        themeBtn.title = isLight ? 'Karanlık Temaya Geç' : 'Aydınlık Temaya Geç';
    }
}

function injectThemeToggle() {
    if (document.querySelector('.theme-toggle-btn')) return;
    
    const navbarStatus = document.querySelector('.navbar-status');
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'accessibility-btn theme-toggle-btn';
    
    // Mevcut tema durumunu kontrol et
    const isLight = document.body.classList.contains('light-theme');
    toggleBtn.innerHTML = isLight ? '🌙' : '☀️';
    toggleBtn.title = isLight ? 'Karanlık Temaya Geç' : 'Aydınlık Temaya Geç';
    
    toggleBtn.addEventListener('click', (e) => {
        e.preventDefault();
        toggleTheme();
    });
    
    if (navbarStatus) {
        navbarStatus.appendChild(toggleBtn);
    } else {
        const navbarBrand = document.querySelector('.navbar-brand');
        if (navbarBrand) {
            toggleBtn.style.marginLeft = '15px';
            navbarBrand.parentNode.insertBefore(toggleBtn, navbarBrand.nextSibling);
        }
    }
}

// Tema durumunu sayfa yüklenmeden önce anında uygula (Beyaz ekran parlamasını önlemek için)
(function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.documentElement.classList.add('light-theme'); // html'e de ekleyelim
        document.body.classList.add('light-theme');
    }
})();