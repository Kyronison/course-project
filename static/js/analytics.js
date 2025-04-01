document.addEventListener('DOMContentLoaded', () => {
    initChartDemo();

    // Обработчики для кастомных селекторов
    document.querySelectorAll('.neo-select-wrapper').forEach(wrapper => {
        const trigger = wrapper.querySelector('.neo-select-trigger');
        const dropdown = wrapper.querySelector('.neo-select-dropdown');
        const options = wrapper.querySelectorAll('.neo-option');
        const searchInput = wrapper.querySelector('.neo-search-input');

        // Открытие/закрытие дропдауна
        trigger.addEventListener('click', () => {
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        });

        // Выбор опции
        options.forEach(option => {
            option.addEventListener('click', () => {
                // Снимаем выделение со всех опций
                options.forEach(opt => opt.classList.remove('selected'));

                // Выделяем выбранную опцию
                option.classList.add('selected');

                // Закрываем дропдаун после выбора
                dropdown.style.display = 'none';

                // Обновляем текст триггера
                updateSelectTriggerText(wrapper);
            });
        });

        // Поиск
        searchInput.addEventListener('input', (e) => {
            const searchText = e.target.value.toLowerCase();
            options.forEach(option => {
                const text = option.textContent.toLowerCase();
                option.style.display = text.includes(searchText) ? 'flex' : 'none';
            });
        });

        // Закрытие дропдауна при клике вне селектора
        document.addEventListener('click', (event) => {
            if (!wrapper.contains(event.target)) {
                dropdown.style.display = 'none';
            }
        });
    });

    // Кнопка "Сравнить"
    const compareBtn = document.getElementById('compareBtn');
    compareBtn.addEventListener('click', () => {
        updateComparison();
    });

    // Если есть heroBtn
    const heroBtn = document.getElementById('heroBtn');
    if (heroBtn) {
        heroBtn.addEventListener('click', () => {
            updateComparison();
        });
    }
});

let correlationChartInstance = null;

function initChartDemo() {
    drawChartFromServer('Technology', 'BTC');
}

function updateComparison() {
    const sector = getSelectedValue('#sectorSelectWrapper');
    const crypto = getSelectedValue('#cryptoSelectWrapper');

    if (!crypto) {
        console.warn('Криптовалюта не выбрана.');
        return;
    }

    if (!sector) {
        console.warn('Сектор не выбран.');
        return;
    }

    drawChartFromServer(sector, crypto);
}

function drawChartFromServer(sector, crypto) {
    fetch(`/api/yfinance/compare?sector=${sector}&crypto=${crypto}`)
        .then(response => response.json())
        .then(data => {
            const { dates, sector_values, crypto_values, correlation } = data;
            drawCorrelationChart(dates, sector_values, crypto_values, correlation, sector, crypto);
        })
        .catch(err => {
            console.error('Ошибка при получении данных с сервера:', err);
        });
}

function getSelectedValue(selector) {
    const selected = document.querySelector(`${selector} .option-item.selected`);
    return selected ? selected.dataset.value : null;
}


function drawCorrelationChart(labels, sectorData, cryptoData, correlation, sector, crypto) {
    if (correlationChartInstance) {
        correlationChartInstance.destroy();
    }

    const ctx = document.getElementById('correlationChart').getContext('2d');
    correlationChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: `Отрасль: ${sector}`,
                    data: sectorData,
                    borderColor: '#c78815',
                    backgroundColor: 'transparent',
                    tension: 0,
                    pointRadius: 0
                },
                {
                    label: `Криптовалюта: ${crypto}`,
                    data: cryptoData,
                    borderColor: '#00a3ff',
                    backgroundColor: 'transparent',
                    tension: 0,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                tooltip: {
                    enabled: true,
                    callbacks: {
                        label: function (tooltipItem) {
                            const datasetLabel = tooltipItem.dataset.label || '';
                            const yValue = tooltipItem.parsed.y;
                            return `${datasetLabel}: ${yValue}`;
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Сравнение отрасли и криптовалюты (Yahoo Finance)',
                    font: { size: 16 },
                    color: '#fff'
                },
                legend: {
                    labels: { color: '#fff' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#fff' },
                    grid: {
                        display: false
                    }
                },
                y: {
                    ticks: { color: '#fff' },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });

    const corrElem = document.getElementById('corrValue');
    if (corrElem) {
        corrElem.textContent = correlation.toFixed(2);
    }

    // Обновляем текст триггеров селекторов
    updateSelectTriggerText(document.querySelector('#sectorSelectWrapper'));
    updateSelectTriggerText(document.querySelector('#cryptoSelectWrapper'));
}

function updateSelectTriggerText(wrapper) {
    const selectedValue = getSelectedValue(`#${wrapper.id}`);
    const trigger = wrapper.querySelector('.neo-select-trigger span');

    if (selectedValue) {
        trigger.textContent = wrapper.querySelector(`.option-item[data-value="${selectedValue}"]`).textContent;
    } else {
        trigger.textContent = 'Выберите...';
    }
}
