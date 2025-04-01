document.addEventListener('DOMContentLoaded', () => {
    // Конфигурация элементов UI
    const ui = {
        amount: {
            input: document.getElementById('investment-amount'),
            slider: document.getElementById('amount-slider')
        },
        maxShare: {
            input: document.getElementById('max-share-input'),
            slider: document.getElementById('max-share-slider')
        },
        risk: {
            slider: document.getElementById('risk-slider'),
            tiles: document.querySelectorAll('.risk-tile')
        },
        cryptoCheckbox: document.getElementById('include-crypto'),
        generateBtn: document.getElementById('generate-portfolio'),
        sectorsContainer: document.getElementById('sectors-container'),
        portfolioResults: document.querySelector('.portfolio-results')
    };

    // Объявляем переменные, чтобы они были доступны во всей области видимости
    const loadingOverlay = document.querySelector('.loading-overlay');
    const completionAnimation = document.getElementById('completionAnimation');

    // Функция для показа/скрытия анимации завершения
    const toggleCompletionAnimation = (show) => {
        completionAnimation.style.display = show ? 'flex' : 'none';
    };

    // Функция для показа/скрытия блока результатов
    const togglePortfolioResults = (show) => {
        ui.portfolioResults.style.display = show ? 'block' : 'none';
    };

    // Подключаем все функции
    const PRELOADED_PORTFOLIO = {
        total_allocated: 950000,
        forecast_amount: 1092500,
        forecast_percent: 15.0,
        top_analysts_count: 23,
        purchases: [
            {
                ticker: "AAPL",
                company_name: "Apple Inc",
                image_url: "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
                type: "stock",
                price_per_share: 185.32,
                shares: 5,
                allocation_percent: 25,
                forecast: { change_percent: 18.5 }
            },
            {
                ticker: "BTC-USD",
                company_name: "Bitcoin",
                image_url: "https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=040",
                type: "crypto",
                cost_rub: 4200000,
                quantity: 0.023,
                allocation_percent: 15,
                forecast: { change_percent: 12.8 }
            }
        ]
    };

    const formatCurrency = (value) => {
        if (typeof value === 'undefined' || value === null) {
            return '0.00'; // или другое значение по умолчанию
        }
        return value.toLocaleString('ru-RU', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    // Конфигурация секторов
    const sectorsConfig = [
        {id: 'IT', name: 'IT', icon: '<i class="fa fa-industry"></i>', default: true},
        {id: 'Raw', name: 'Сырье', icon: '<i class="fas fa-industry"></i>', default: true},
        {id: 'Transport', name: 'Транспорт', icon: '<i class="fas fa-plane"></i>', default: false},
        {id: 'HealthCare', name: 'Здравоохранение', icon: '<i class="fas fa-heartbeat"></i>', default: false},
        {id: 'RealEstate', name: 'Недвижимость', icon: '<i class="fas fa-building"></i>', default: false},
        {id: 'Basic', name: 'Базовые товары', icon: '<i class="fas fa-shopping-cart"></i>', default: false},
        {id: 'Telecom', name: 'Телекоммуникации', icon: '<i class="fas fa-signal"></i>', default: false},
        {id: 'Finance', name: 'Финансы', icon: '<i class="fas fa-coins"></i>', default: true},
        {id: 'ElectroEnergy', name: 'Электроэнергия', icon: '<i class="fas fa-bolt"></i>', default: false},
        {id: 'Energy', name: 'Энергетика', icon: '<i class="fas fa-gas-pump"></i>', default: false}
    ];

    // Состояние приложения
    let appState = {
        selectedRisk: 0.2,
        selectedSectors: ['IT', 'Raw', 'Finance']
    };

    const applyDefaultSettings = () => {
        // Устанавливаем значения по умолчанию
        ui.amount.input.value = 1000000;
        ui.amount.slider.value = 1000000;
        ui.maxShare.input.value = 25;
        ui.maxShare.slider.value = 25;
        ui.cryptoCheckbox.checked = true;

        // Обновляем визуальные элементы
        updateSliderBackground(ui.amount.slider);
        updateSliderBackground(ui.maxShare.slider);
    };

    // Инициализация приложения
    const init = () => {
        initSectors();
        initEventListeners();
        applyDefaultSettings();
        updateSliderBackground(ui.amount.slider);
        updateSliderBackground(ui.maxShare.slider);
        // displayPortfolioResults(PRELOADED_PORTFOLIO); // Показываем данные сразу
    };

    const setupInstantUpdates = () => {
        // Обновление данных при изменении настроек
        [ui.amount.input, ui.amount.slider, ui.maxShare.input, ui.maxShare.slider].forEach(element => {
            element.addEventListener('input', () => {
                displayPortfolioResults(PRELOADED_PORTFOLIO);
            });
        });
    };
    // Инициализация секторов
    const initSectors = () => {
        ui.sectorsContainer.innerHTML = '';
        sectorsConfig.forEach(sector => {
            const tile = document.createElement('div');
            tile.className = 'sector-tile';
            tile.dataset.sector = sector.id;

            if (sector.default) {
                tile.classList.add('selected');
            }

            tile.innerHTML = `
                <div class="sector-icon">${sector.icon}</div>
                <span>${sector.name}</span>
            `;
            tile.addEventListener('click', () => toggleSector(tile));
            ui.sectorsContainer.appendChild(tile);
        });
    };

    // Инициализация обработчиков событий
    const initEventListeners = () => {
        // Обработчики для суммы инвестиций
        ui.amount.input.addEventListener('input', () => syncInputWithSlider(ui.amount));
        ui.amount.slider.addEventListener('input', () => syncSliderWithInput(ui.amount));

        // Обработчики для максимальной доли
        ui.maxShare.input.addEventListener('input', () => syncInputWithSlider(ui.maxShare));
        ui.maxShare.slider.addEventListener('input', () => syncSliderWithInput(ui.maxShare));

        // Обработчики для риска
        ui.risk.tiles.forEach(tile => {
            tile.addEventListener('click', () => handleRiskSelection(tile));
        });

        // Обработчик кнопки генерации
        ui.generateBtn.addEventListener('click', handleGeneratePortfolio);
    };

    // Логика синхронизации элементов формы
    const syncInputWithSlider = ({input, slider}) => {
        const value = parseFloat(input.value);
        if (!isNaN(value)) {
            slider.value = value;
            updateSliderBackground(slider);
        }
    };

    const syncSliderWithInput = ({input, slider}) => {
        input.value = slider.value;
        updateSliderBackground(slider);
    };

    // Обновление фона слайдера
    const updateSliderBackground = (slider) => {
        const {min, max, value} = slider;
        const percentage = ((value - min) / (max - min)) * 100;
        slider.style.background = `linear-gradient(to right, #4763e4 0%, #4763e4 ${percentage}%, #e2e8f0 ${percentage}%, #e2e8f0 100%)`;
    };

    // Обработка выбора риска
    const handleRiskSelection = (tile) => {
        ui.risk.tiles.forEach(t => t.classList.remove('selected'));
        tile.classList.add('selected');
        appState.selectedRisk = parseFloat(tile.dataset.risk);
    };

    // Обработка выбора сектора
    const toggleSector = (tile) => {
        tile.classList.toggle('selected');
        const sectorId = tile.dataset.sector;
        appState.selectedSectors = appState.selectedSectors.includes(sectorId)
            ? appState.selectedSectors.filter(id => id !== sectorId)
            : [...appState.selectedSectors, sectorId];
    };

    // Основная функция генерации портфеля
        const handleGeneratePortfolio = async () => {
        showLoadingState(true); // Показать индикатор

        try {
            const portfolioData = await generatePortfolio();
            displayPortfolioResults(portfolioData);
            ui.portfolioResults.style.display = 'block'; // Показываем результаты
        } catch (error) {
            console.error('Ошибка генерации:', error);
            showErrorNotification('Не удалось загрузить данные');
        } finally {
            showLoadingState(false); // Скрыть индикатор
        }
    };


    // Сбор параметров и генерация запроса
    const generatePortfolio = async () => {
        const params = {
            amount: parseFloat(ui.amount.input.value),
            max_share: parseFloat(ui.maxShare.slider.value) / 100,
            risk_level: appState.selectedRisk,
            include_crypto: ui.cryptoCheckbox.checked,
            sectors: appState.selectedSectors
        };

        try {

            const response = await fetch('/api/generate-portfolio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            });

            if (!response.ok) throw new Error('Ошибка сервера');
            return await response.json();

        } catch (error) {
            console.error('Ошибка:', error);
            showErrorNotification('Не удалось сформировать портфель');
            throw error;
        }
    };
    /*
    const generatePortfolio = async () => {
    const params = {
        amount: parseFloat(ui.amount.input.value),
        max_share: parseFloat(ui.maxShare.slider.value) / 100,
        risk_level: appState.selectedRisk,
        include_crypto: ui.cryptoCheckbox.checked,
        sectors: appState.selectedSectors
    };

    try {
        // Заменяем реальный запрос на моковый
        return await mockApiRequest(params);

    } catch (error) {
        console.error('Ошибка:', error);
        showErrorNotification('Не удалось сформировать портфель');
        throw error;
    }
};
    */
    // Отображение состояния загрузки
    // Обновите функцию showLoadingState в portfolio.js

    // Обновите функцию displayPortfolioResults

    // Обновите блок с подтверждением
    let loadingTimeout;
    function showLoadingState(show) {
        const overlay = document.querySelector('.loading-overlay');
        const body = document.body;

        if (show) {
            // Показываем через 300мс для плавности
            loadingTimeout = setTimeout(() => {
                body.classList.add('loading-active');
                overlay.classList.add('active');
            }, 300);
        } else {
            clearTimeout(loadingTimeout);
            body.classList.remove('loading-active');
            overlay.classList.remove('active');
        }

        // Блокировка элементов управления
        const interactiveElements = document.querySelectorAll(
            'button, input, select, textarea, .sector-tile'
        );
        interactiveElements.forEach(el => el.disabled = show);
    }

    // Отображение результатов
    const displayPortfolioResults = (data) => {

        if (!data || !data.purchases || !Array.isArray(data.purchases)) {
            showErrorNotification('Некорректные данные от сервера');
            return;
        }

        // Добавьте отладочный вывод
        console.log('Полученные данные:', data);

        // Расчет прогноза
        let currentTotal = 0;
        let forecastTotal = 0;

        try {
            data.purchases.forEach(asset => {
                const assetValue = Number(asset.cost_rub) || 0;
                const growth = Number(asset.forecast?.change_percent) || 0;

                currentTotal += assetValue;
                forecastTotal += assetValue * (1 + growth / 100);
            });
        } catch (e) {
            console.error('Ошибка расчета:', e);
            showErrorNotification('Ошибка обработки данных');
            return;
        }

        // Показываем секцию результатов
        ui.portfolioResults.style.display = 'block';
        ui.portfolioResults.scrollIntoView({ behavior: 'smooth' });

        // Расчет общего процента роста
        const forecastPercent = currentTotal > 0
            ? ((forecastTotal / currentTotal - 1) * 100)
            : 0;

        // Обновление данных
        const safeData = {
            total_allocated: currentTotal,
            forecast_amount: forecastTotal,
            forecast_percent: forecastPercent,
            purchases: data.purchases
        };

        // Обновляем метрики
        document.getElementById('total-invested').textContent = formatCurrency(safeData.total_allocated);
        document.getElementById('forecast-amount').textContent = formatCurrency(safeData.forecast_amount);
        document.getElementById('forecast-percent').textContent = `${forecastPercent >= 0 ? '+' : ''}${forecastPercent.toFixed(2)}%`;

        // Очищаем предыдущие результаты
        const assetsContainer = document.getElementById('assets-container');
        assetsContainer.innerHTML = '';

        // Добавляем новые активы
        data.purchases.forEach(asset => {
            const row = document.createElement('tr');
            row.innerHTML = createAssetRow(asset);
            assetsContainer.appendChild(row);
        });

        /*
        const forecastElement = document.createElement('div');
        forecastElement.className = 'portfolio-forecast';
        const forecastPercent = Number(data?.forecast_percent ?? 0);
        const forecastAmount = data?.forecast_amount ?? 0;
        forecastElement.innerHTML = `
            <h3>Прогноз роста через год:</h3>
            <div class="forecast-container">
                <div class="forecast-item">
                    <span class="forecast-label">Ожидаемая доходность:</span>
                    <span class="forecast-value ${forecastPercent >= 0 ? 'positive' : 'negative'}">
                        ${Math.abs(forecastPercent).toFixed(2)}%
                    </span>
                </div>
                <div class="forecast-item">
                    <span class="forecast-label">Прогнозируемая сумма:</span>
                    <span class="forecast-value">${formatCurrency(forecastAmount)}</span>
                </div>
            </div>
        `;
        ui.portfolioResults.prepend(forecastElement);
        */
    };

    // Вспомогательные функции

    const createAssetRow = (asset) => {
        const isCrypto = asset.type === 'crypto';

        // Рассчитываем значения
        const price = isCrypto
            ? (asset.cost_rub / asset.quantity)
            : asset.price_per_share;

        const total = isCrypto
            ? asset.cost_rub
            : (asset.price_per_share * asset.shares);

        // Форматируем числа
        const formatter = new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });

        return `
            <tr>
                <td>
                    <div class="asset-header">
                        <img src="${asset.image_url}" alt="${asset.company_name}" style="width: 30px; height: 30px; border-radius: 4px">
                        <div>
                            <div class="asset-name">${asset.company_name}</div>
                            <div class="asset-ticker">${asset.ticker}</div>
                        </div>
                    </div>
                </td>
                <td>${formatter.format(price)}</td>
                <td>${isCrypto ? asset.quantity.toFixed(4) : asset.shares}</td>
                <td>${formatter.format(total)}</td>
                <td>${asset.forecast?.change_percent.toFixed(2)}%</td>
            </tr>
        `;
    };

    // Показ ошибок
    function showErrorNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 5000); // Исчезает через 5 секунд
    }

    init();
});
