
// Premium Seed Data for AlphaCraftPro2
APP.data.seedPremiumData = async () => {
    console.log("Seeding Premium Data...");

    // 1. Clear existing data
    await db._set('personnel', []);
    await db._set('shifts', []);
    await db._set('schedule', {});
    await db._set('completed_shifts', []);
    await db._set('time_cards', []);

    // 2. Add Premium Personnel
    const staffList = [
        { name: "Ahmet Yılmaz", role: "Müdür", phone: "555-0001", freq: "monthly", dayOff: ["Paz"], hourlyRate: 150.00 },
        { name: "Ayşe Demir", role: "Şef Garson", phone: "555-0002", freq: "daily", dayOff: ["Pzt"], hourlyRate: 85.00 },
        { name: "Mehmet Öz", role: "Baş Aşçı", phone: "555-0003", freq: "monthly", dayOff: ["Sal"], hourlyRate: 120.00 },
        { name: "Zeynep Kaya", role: "Barista", phone: "555-0004", freq: "daily", dayOff: ["Çar"], hourlyRate: 65.00 },
        { name: "Ali Vural", role: "Komi", phone: "555-0005", freq: "daily", dayOff: ["Per"], hourlyRate: 45.00 },
        { name: "Selin Çelik", role: "Barmen", phone: "555-0006", freq: "daily", dayOff: ["Cum"], hourlyRate: 75.00 },
        { name: "Caner Erkin", role: "Bulaşıkçı", phone: "555-0007", freq: "daily", dayOff: ["Cmt"], hourlyRate: 50.00 },
    ];

    const personnelIds = [];
    for (const p of staffList) {
        const id = db.addDoc('personnel', p);
        personnelIds.push({ ...p, id });
    }

    // 3. Add Standard Shifts
    const shifts = [
        {
            name: "Sabah Vardiyası",
            startTime: "08:00",
            endTime: "16:00",
            days: ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"],
            requiredRoles: { "Şef Garson": 1, "Barista": 1, "Aşçı": 1, "Komi": 1 }
        },
        {
            name: "Akşam Vardiyası",
            startTime: "16:00",
            endTime: "00:00",
            days: ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"],
            requiredRoles: { "Müdür": 1, "Şef Garson": 1, "Barmen": 1, "Aşçı": 1, "Komi": 2, "Bulaşıkçı": 1 }
        }
    ];

    for (const s of shifts) {
        db.addDoc('shifts', s);
    }

    // 4. Set Financial Config
    const config = {
        targetBudget: 150000,
        costHistory: [],
        labels: []
    };
    db._set('financial_config', config);

    // Refresh UI
    APP.actions.refreshAllData();
    Swal.fire({
        icon: 'success',
        title: 'Premium Veriler Yüklendi',
        text: 'Personel ve vardiya verileri başarıyla sıfırlandı ve yeniden oluşturuldu.',
        timer: 2000,
        showConfirmButton: false
    });
};
