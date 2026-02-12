
// --- LEAD HUNTER MODULE ---
const LeadHunter = {
    data: [],
    currentFilter: 'all',

    init: function () {
        console.log("Lead Hunter Initialized.");
        this.refresh();
        setInterval(() => this.refresh(), 5000);
    },

    refresh: async function () {
        try {
            // API_BASE global config.js'den gelir
            const api = window.API_BASE || 'http://localhost:8001';

            const res = await fetch(`${api}/api/leads`);
            const json = await res.json();

            this.data = json.leads;
            this.updateStats(json.stats);
            this.render();
        } catch (e) {
            console.error("Lead fetch error:", e);
        }
    },

    triggerScan: async function () {
        Swal.fire({
            title: 'Derin Tarama Başlatılsın mı?',
            text: "AZI tüm sektörleri arka planda detaylıca tarayacak. Bu işlem interneti yoğun kullanabilir.",
            icon: 'info',
            showCancelButton: true,
            confirmButtonText: 'Evet, Başlat 🚀',
            cancelButtonText: 'İptal',
            background: '#0f172a', color: '#fff'
        }).then(async (result) => {
            if (result.isConfirmed) {
                const api = window.API_BASE || 'http://localhost:8001';
                await fetch(`${api}/api/leads/scan`, { method: 'POST' });
                Swal.fire({
                    title: 'Başlatıldı!',
                    text: 'Arkanıza yaslanın, av başladı.',
                    icon: 'success',
                    timer: 2000,
                    background: '#0f172a', color: '#fff'
                });
            }
        });
    },

    updateStats: function (stats) {
        document.getElementById('stat-total-leads').innerText = stats.total;
        document.getElementById('stat-new-leads').innerText = stats.new;
        document.getElementById('stat-contacted-leads').innerText = stats.contacted;
        document.getElementById('stat-replied-leads').innerText = stats.replied;

        // Onay bekleyen badge varsa güncelle (Henüz HTML'de olmayabilir)
    },

    filter: function (filterType) {
        this.currentFilter = filterType;
        document.querySelectorAll('[id^="filter-btn-"]').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`filter-btn-${filterType}`).classList.add('active');
        this.render();
    },

    setApproval: async function (leadId, approved) {
        try {
            const api = window.API_BASE || 'http://localhost:8001';
            const res = await fetch(`${api}/api/leads/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lead_id: leadId, approved: approved })
            });

            if (res.ok) {
                // Listeden anlık kaldır veya güncelle
                this.refresh();
                const msg = approved ? 'Onaylandı' : 'Reddedildi';
                Swal.fire({
                    toast: true, position: 'top-end', icon: approved ? 'success' : 'error',
                    title: `Müşteri ${msg}`, timer: 1500, background: '#0f172a', color: '#fff'
                });
            }
        } catch (e) {
            console.error(e);
        }
    },

    markAsReplied: async function (leadId) {
        // ... (Mevcut kod aynı kalabilir veya API_BASE güncellemesi ile burası da düzelir)
        // Kısaltma için burayı tekrar yazmıyorum, yukarıdaki setApproval mantığıyla aynı.
        const api = window.API_BASE || 'http://localhost:8001';
        await fetch(`${api}/api/leads/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lead_id: leadId, status: 'replied' })
        });
        this.refresh();
    },

    render: function () {
        const tbody = document.getElementById('leads-table-body');
        tbody.innerHTML = '';

        let filtered = this.data;

        // FİLTRELEME MANTIĞI
        if (this.currentFilter === 'pending') {
            // Sadece onaysızlar (is_approved == 0)
            filtered = this.data.filter(l => l.is_approved === 0);
        } else if (this.currentFilter === 'all') {
            // Hepsi (Reddedilenler hariç -1)
            filtered = this.data.filter(l => l.is_approved !== -1);
        } else {
            // Diğer durumlar (new, contacted, replied) VE Onaylanmışlar
            filtered = this.data.filter(l => l.status === this.currentFilter && l.is_approved === 1);
        }

        if (filtered.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-gray-500">Kayıt bulunamadı.</td></tr>';
            return;
        }

        filtered.forEach(lead => {
            let statusBadge = '';
            let rowClass = 'hover:bg-slate-800/50 transition';

            // Satır Rengi ve Badge
            if (lead.is_approved === 0) {
                statusBadge = '<span class="text-orange-400 font-bold border border-orange-500/30 px-2 rounded">ONAY BEKLİYOR</span>';
                rowClass += ' bg-orange-900/10';
            } else if (lead.status === 'new') {
                statusBadge = '<span class="text-blue-400 font-bold">YENİ</span>';
            } else if (lead.status === 'contacted') {
                statusBadge = '<span class="text-yellow-500">GÖNDERİLDİ</span>';
            } else if (lead.status === 'replied') {
                statusBadge = '<span class="text-green-400 font-bold animate-pulse">CEVAP GELDİ!</span>';
                rowClass += ' bg-green-900/10 border-l-2 border-green-500';
            }

            const lastContact = lead.last_contacted ? new Date(lead.last_contacted).toLocaleString('tr-TR') : '-';

            const tr = document.createElement('tr');
            tr.className = rowClass + ' border-b border-gray-800';

            // Aksiyon Butonları
            let actions = '';

            if (lead.is_approved === 0) {
                actions = `
                    <button class="cyber-btn sm success mr-2" onclick="LeadHunter.setApproval(${lead.id}, true)">
                        <i class="fa-solid fa-check"></i> ONAYLA
                    </button>
                    <button class="cyber-btn sm danger" onclick="LeadHunter.setApproval(${lead.id}, false)">
                        <i class="fa-solid fa-xmark"></i> REDDET
                    </button>
                `;
            } else {
                // Onaylanmışsa diğer işlemler
                if (lead.status !== 'replied') {
                    actions = `
                    <button class="text-green-400 hover:text-green-300 mr-2" onclick="LeadHunter.markAsReplied(${lead.id})" title="Cevap Geldi">
                        <i class="fa-solid fa-check-double"></i>
                    </button>
                    `;
                } else {
                    actions = '<i class="fa-solid fa-check text-green-500"></i>';
                }
            }

            tr.innerHTML = `
                <td class="p-3">${statusBadge}</td>
                <td class="p-3 text-white font-mono select-all">${lead.email}</td>
                <td class="p-3">
                    <div class="w-full bg-gray-800 rounded-full h-1.5 w-16" title="Skor: ${lead.trust_score}">
                        <div class="bg-blue-500 h-1.5 rounded-full" style="width: ${Math.min(lead.trust_score, 100)}%"></div>
                    </div>
                </td>
                <td class="p-3 text-gray-400 text-xs">${lead.source.replace('Targeted:', '').substring(0, 20)}</td>
                <td class="p-3 text-gray-500 text-xs">${lastContact}</td>
                <td class="p-3 flex items-center">${actions}</td>
            `;
            tbody.appendChild(tr);
        });
    }
};
