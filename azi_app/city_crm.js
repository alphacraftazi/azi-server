window.CityCRM = {
    map: null,
    currentMode: 'view', // view, mark, ping
    layers: [],

    init: function () {
        if (this.map) return;

        // Haritayı Eskişehir merkezli başlat
        // Limitler (Eskişehir)
        const eskisehirBounds = [
            [39.60, 30.30], // Güney Batı
            [39.95, 30.75]  // Kuzey Doğu
        ];

        this.map = L.map('city-map', {
            center: [39.7767, 30.5206],
            zoom: 13,
            minZoom: 12, // Çok uzaklaşmayı engelle
            maxBounds: eskisehirBounds,
            maxBoundsViscosity: 1.0, // Kenarlardan çıkmayı engelle
            attributionControl: false,
            zoomControl: false
        });

        // OpenStreetMap (Daha güvenilir) + CSS Filter ile Karanlık Mod
        // Tile Layer için 'className' ekleyerek CSS'te filtreleyeceğiz
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            className: 'map-tiles-dark'
        }).addTo(this.map);

        // Map Click Event
        this.map.on('click', (e) => {
            if (this.currentMode === 'mark') {
                this.addActivity('mark', e.latlng);
            } else if (this.currentMode === 'ping') {
                this.addActivity('ping', e.latlng);
            }
        });

        this.loadActivities();
        this.generateCalendar();
        this.loadAnalysis();
    },

    setMode: function (mode) {
        this.currentMode = mode;
        const cursor = mode === 'view' ? 'grab' : 'crosshair';
        document.getElementById('city-map').style.cursor = cursor;

        const titles = { mark: 'KONUM İŞARETLE', ping: 'PİNG AT' };
        if (mode !== 'view') {
            Swal.fire({
                toast: true,
                position: 'top-end',
                icon: 'info',
                title: `${titles[mode]} MODU`,
                text: 'Haritada bir noktaya tıklayın.',
                timer: 3000,
                showConfirmButton: false
            });
        }
    },

    loadActivities: async function () {
        try {
            const apiBase = window.API_BASE || 'http://localhost:8001';
            const response = await fetch(`${apiBase}/api/city/activities`);
            const activities = await response.json();

            // Temizle
            this.layers.forEach(l => this.map.removeLayer(l));
            this.layers = [];
            document.getElementById('activity-feed').innerHTML = '';

            activities.forEach(act => {
                this.renderMarker(act);
                this.renderFeedItem(act);
            });
        } catch (e) {
            console.error("Activities Load Error:", e);
        }
    },

    addActivity: async function (type, latlng) {
        // Modal ile detay al
        const { value: formValues } = await Swal.fire({
            title: type === 'mark' ? 'Yeni Not / İşaret' : 'Ping Gönder',
            html: `
                <input id="swal-title" class="swal2-input" placeholder="Başlık">
                <input id="swal-desc" class="swal2-input" placeholder="Açıklama">
            `,
            background: '#0f172a',
            color: '#fff',
            focusConfirm: false,
            preConfirm: () => {
                return [
                    document.getElementById('swal-title').value,
                    document.getElementById('swal-desc').value
                ]
            }
        });

        if (formValues) {
            const [title, desc] = formValues;

            const apiBase = window.API_BASE || 'http://localhost:8001';
            try {
                const res = await fetch(`${apiBase}/api/city/activities`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        activity_type: type,
                        title: title || (type === 'mark' ? 'İşaretli Konum' : 'Ping'),
                        description: desc,
                        latitude: latlng.lat,
                        longitude: latlng.lng
                    })
                });

                if (res.ok) {
                    this.loadActivities();
                    this.loadAnalysis();
                    this.setMode('view');
                    Swal.fire({ toast: true, icon: 'success', title: 'Kaydedildi', timer: 2000, position: 'top-end', background: '#0f172a', color: '#fff' });
                }
            } catch (e) {
                console.error("Save Error:", e);
            }
        }
    },

    deleteActivity: async function (id) {
        try {
            const apiBase = window.API_BASE || 'http://localhost:8001';
            const res = await fetch(`${apiBase}/api/city/activities/${id}`, { method: 'DELETE' });
            if (res.ok) {
                // Remove from local (or just reload)
                this.loadActivities();
                this.loadAnalysis();
                Swal.fire({
                    toast: true,
                    icon: 'success',
                    title: 'Silindi',
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 1500,
                    background: '#0f172a',
                    color: '#fff'
                });
            } else {
                Swal.fire({ toast: true, icon: 'error', title: 'Hata', text: 'Silinemedi.' });
            }
        } catch (e) {
            console.error("Delete Error:", e);
        }
    },

    renderMarker: function (act) {
        const colors = { mark: '#ef4444', ping: '#00f2ff', note: '#facc15' };
        const iconHtml = `<div style="
            background: ${colors[act.activity_type] || '#fff'};
            width: 12px; height: 12px;
            border-radius: 50%;
            box-shadow: 0 0 10px ${colors[act.activity_type] || '#fff'};
            border: 2px solid white;">
        </div>`;

        const icon = L.divIcon({ html: iconHtml, className: 'custom-marker' });

        const marker = L.marker([act.latitude, act.longitude], { icon: icon })
            .bindPopup(`
                <div class="text-center">
                    <b class="text-cyan-400">${act.title}</b><br>
                    <div class="text-xs mb-2 text-gray-300">${act.description}</div>
                    <small class="text-gray-500 block mb-2">${new Date(act.date).toLocaleDateString()}</small>
                    <button onclick="CityCRM.deleteActivity(${act.id})" 
                        class="bg-red-900/50 hover:bg-red-600 border border-red-500 text-red-100 text-[10px] px-2 py-1 rounded w-full transition">
                        <i class="fa-solid fa-trash"></i> SİL
                    </button>
                </div>
            `)
            .addTo(this.map);

        this.layers.push(marker);
    },

    renderFeedItem: function (act) {
        const icons = { mark: 'fa-location-dot', ping: 'fa-signal', note: 'fa-note-sticky' };
        const colors = { mark: 'text-red-500', ping: 'text-cyan-400', note: 'text-yellow-400' };

        const html = `
            <div class="feed-item">
                <div class="feed-icon"><i class="fa-solid ${icons[act.activity_type] || 'fa-circle'} ${colors[act.activity_type]}"></i></div>
                <div>
                    <div class="font-bold text-sm text-gray-200">${act.title}</div>
                    <div class="text-xs text-gray-400">${act.description}</div>
                    <div class="text-[10px] text-gray-500 mt-1">${new Date(act.date).toLocaleString()}</div>
                </div>
            </div>
        `;
        document.getElementById('activity-feed').insertAdjacentHTML('afterbegin', html);
    },

    loadAnalysis: async function () {
        try {
            const apiBase = window.API_BASE || 'http://localhost:8001';
            const response = await fetch(`${apiBase}/api/city/analysis`);
            const data = await response.json();
            document.getElementById('azi-city-analysis').innerText = `"${data.analysis}"`;
        } catch (e) { }
    },

    generateCalendar: function () {
        const container = document.getElementById('mini-calendar');
        container.innerHTML = '';
        const today = new Date();
        // Basit 1 haftalık takvim
        for (let i = 0; i < 7; i++) {
            const d = new Date();
            d.setDate(today.getDate() + i);
            const isToday = i === 0;

            const cell = document.createElement('div');
            cell.className = `calendar-day ${isToday ? 'bg-blue-600 text-white border-blue-400' : 'text-gray-400'}`;
            cell.innerHTML = `
                <div class="font-bold">${d.getDate()}</div>
                <div class="text-[10px]">${d.toLocaleDateString('tr-TR', { weekday: 'short' })}</div>
            `;
            container.appendChild(cell);
        }
    },

    locateMe: function () {
        this.map.locate({ setView: true, maxZoom: 16 });
    }
};
