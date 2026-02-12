
// Global variable to store current businesses data for quick access
let currentBusinesses = [];

async function loadLicenses() {
    const tbody = document.getElementById('licensesTableBody');
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:20px; color:#666;">Yükleniyor...</td></tr>';

    try {
        const res = await fetch('/api/businesses');
        const data = await res.json();
        currentBusinesses = data; // Store for modal usage

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:20px; color:#666;">Kayıtlı lisans bulunamadı.</td></tr>';
            return;
        }

        tbody.innerHTML = data.map(b => `
            <tr onclick="openBusinessDetails(${b.id})" style="border-bottom:1px solid #222; font-family:'Courier New'; color:#aaa; cursor:pointer;" onmouseover="this.style.background='#111'" onmouseout="this.style.background='transparent'">
                <td style="padding:10px;">#${b.id}</td>
                <td style="padding:10px; color:#fff;">
                    ${b.name}<br>
                    <span style="font-size:10px; color:#666;">${b.product_type}</span>
                </td>
                <td style="padding:10px; color:#00f2ff; font-weight:bold;">${b.license_key}</td>
                <td style="padding:10px;">
                    <span class="tag ${b.status === 'active' ? 'success' : 'warning'}">${b.status}</span>
                    ${b.is_online ? '<span style="color:#0f0; font-size:10px; margin-left:5px;">● ONLINE</span>' : ''}
                </td>
                <td style="padding:10px; font-weight:bold; color:#10b981;">₺${(b.license_price || 0).toLocaleString('tr-TR')}</td>
                <td style="padding:10px;">
                    <button onclick="event.stopPropagation(); deleteLicense(${b.id})" style="background:none; border:none; color:#ef4444; cursor:pointer; font-size:14px;" title="Sil">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        // Update Total Revenue
        const totalRev = data.reduce((acc, curr) => acc + (curr.license_price || 0), 0);
        const revEl = document.getElementById('dash-total-revenue');
        if (revEl) revEl.innerText = `₺${totalRev.toLocaleString('tr-TR')}`;


    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px; color:red;">Hata: ${e}</td></tr>`;
    }
}

async function deleteLicense(id) {
    if (!confirm(`ID #${id} numaralı işletmeyi silmek istediğinize emin misiniz? Bu işlem geri alınamaz.`)) return;

    try {
        const res = await fetch(`/api/license/${id}`, { method: 'DELETE' });
        const data = await res.json();

        if (data.success) {
            // alert("İşletme silindi."); // Alert yerine toast daha şık olur ama şimdilik yeterli
            loadLicenses(); // Refresh table
        } else {
            alert("Silme başarısız: " + data.error);
        }
    } catch (e) {
        alert("Hata oluştu: " + e);
    }
}

async function deleteAllLicenses() {
    // Show confirmation dialog
    const result = await Swal.fire({
        title: 'TÜM AĞ SIFIRLANSIN MI?',
        text: "Bu işlem geri alınamaz! Tüm işletmeler ve kayıtlar silinecektir.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'EVET, SIFIRLA',
        cancelButtonText: 'İPTAL',
        background: '#020617',
        color: '#fff'
    });

    if (result.isConfirmed) {
        try {
            // Call API
            const response = await fetch('/api/license/delete-all', { method: 'POST' });

            if (response.ok) {
                await Swal.fire({
                    title: 'TEMİZLENDİ!',
                    text: 'Ağ verileri başarıyla sıfırlandı.',
                    icon: 'success',
                    background: '#020617',
                    color: '#fff',
                    timer: 1500,
                    showConfirmButton: false
                });
                // Reload page to reflect changes
                window.location.reload();
            } else {
                throw new Error('Sunucu hatası');
            }
        } catch (error) {
            Swal.fire({
                title: 'HATA!',
                text: 'Silme işlemi başarısız oldu: ' + error.message,
                icon: 'error',
                background: '#020617',
                color: '#fff'
            });
        }
    }
}
function openBusinessDetails(id) {
    const business = currentBusinesses.find(b => b.id === id);
    if (!business) return;

    document.getElementById('cardName').innerText = business.name;
    document.getElementById('cardLicense').innerText = business.license_key;
    document.getElementById('cardStatus').innerHTML = `
        <span class="${business.status === 'active' ? 'text-success' : 'text-warning'}">${business.status.toUpperCase()}</span>
        ${business.is_online ? '<span style="color:#0f0; margin-left:10px;">● ÇEVRİMİÇİ</span>' : '<span style="color:#666; margin-left:10px;">○ ÇEVRİMDIŞI</span>'}
    `;
    document.getElementById('cardLastSeen').innerText = business.last_seen ? new Date(business.last_seen).toLocaleString() : 'Yok';

    // Parse System Info
    let sysInfoHtml = '';
    try {
        const info = JSON.parse(business.system_info || '{}');
        if (Object.keys(info).length > 0) {
            sysInfoHtml += `<table style="width:100%; color:#aaa; font-size:12px;">`;
            for (const [key, value] of Object.entries(info)) {
                sysInfoHtml += `<tr><td style="width:100px; color:#666;">${key.toUpperCase()}:</td><td>${value}</td></tr>`;
            }
            sysInfoHtml += `</table>`;
        } else {
            sysInfoHtml = '<span style="color:#444;">Henüz veri alınmadı. (Program çalışınca otomatik gelecek)</span>';
        }
    } catch (e) {
        sysInfoHtml = '<span style="color:red;">Veri formatı hatalı.</span>';
    }

    document.getElementById('cardSystemInfo').innerHTML = sysInfoHtml;
    document.getElementById('businessDetailsModal').style.display = 'flex';
}

// Modal Close Logic
document.getElementById('closeBusinessModal').onclick = function () {
    document.getElementById('businessDetailsModal').style.display = 'none';
}

async function deleteAllLicenses() {
    if (!confirm("DİKKAT! Tüm lisans anahtarları ve işletme kayıtları silinecek. Müşterileriniz erişimi kaybedebilir. Emin misiniz?")) return;

    try {
        const res = await fetch('/api/license/delete-all', { method: 'POST' });

        // Yanıt başarılı değilse (örn: 4xx, 5xx)
        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            const errorMsg = errData.detail || errData.error || res.statusText || "Bilinmeyen sunucu hatası";
            alert("Sunucu Hatası: " + errorMsg);
            console.error("Delete failed:", res.status, res.statusText, errData);
            return;
        }

        const data = await res.json();

        if (data.success) {
            alert("Tüm lisanslar başarıyla silindi ve temizlendi.");
            loadLicenses();
            // İstatistikleri varsa güncelle (hata vermemesi için kontrol)
            if (typeof loadSystemStats === 'function') {
                loadSystemStats();
            }
        } else {
            // Backend'den {success: false, error: "..."} döndüyse
            alert("İşlem Başarısız: " + (data.error || "Bilinmeyen hata"));
            console.error("Backend error:", data);
        }
    } catch (e) {
        alert("Bağlantı veya Ağ Hatası: " + e);
        console.error("Network error:", e);
    }
}
