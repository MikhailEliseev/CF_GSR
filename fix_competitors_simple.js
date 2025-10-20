// Простое решение для загрузки конкурентов
function loadCompetitorsSimple() {
    console.log('🔄 ПРОСТАЯ ЗАГРУЗКА КОНКУРЕНТОВ');
    
    const container = document.getElementById('competitorsList');
    if (!container) {
        console.error('❌ Элемент не найден');
        return;
    }
    
    container.innerHTML = '<div class="text-center text-primary p-3"><div class="spinner-border spinner-border-sm me-2"></div>Загружаем...</div>';
    
    fetch('/api/competitors')
        .then(response => response.json())
        .then(data => {
            console.log('📊 Данные:', data);
            if (data.success && data.competitors) {
                const competitors = data.competitors;
                container.innerHTML = `
                    <div class="table-responsive" style="max-height: 300px; overflow-y: auto;">
                        <table class="table table-sm table-bordered table-hover mb-0">
                            <thead class="table-dark sticky-top">
                                <tr>
                                    <th width="40"><input type="checkbox" id="selectAll" class="form-check-input"></th>
                                    <th width="60">№</th>
                                    <th>Конкурент</th>
                                    <th width="100">Платформа</th>
                                    <th width="80">Статус</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${competitors.map((comp, index) => `
                                    <tr>
                                        <td class="text-center">
                                            <input type="checkbox" value="${comp.username}" id="comp_${comp.id}" ${index === 0 ? 'checked' : ''} class="form-check-input">
                                        </td>
                                        <td class="text-center">${index + 1}</td>
                                        <td>@${comp.username}</td>
                                        <td class="text-center"><span class="badge bg-info">${comp.platform}</span></td>
                                        <td class="text-center"><span class="badge bg-success">${comp.status}</span></td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
                
                const countEl = document.getElementById('competitorsCount');
                if (countEl) countEl.textContent = competitors.length;
                
                console.log('✅ КОНКУРЕНТЫ ЗАГРУЖЕНЫ:', competitors.length);
            } else {
                container.innerHTML = '<div class="text-center text-danger p-3">Ошибка загрузки</div>';
            }
        })
        .catch(error => {
            console.error('❌ ОШИБКА:', error);
            container.innerHTML = '<div class="text-center text-danger p-3">Ошибка: ' + error.message + '</div>';
        });
}

// Автозагрузка
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Запуск простой загрузки конкурентов');
    setTimeout(loadCompetitorsSimple, 1000);
});
