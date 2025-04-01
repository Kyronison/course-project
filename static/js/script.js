// ------------------------------------------------
// Настраиваем Canvas
// ------------------------------------------------
const canvas = document.getElementById('networkCanvas');
const ctx = canvas.getContext('2d');

// Устанавливаем реальные размеры canvas по размеру окна
function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas(); // при загрузке

// ------------------------------------------------
// Параметры частиц
// ------------------------------------------------
const PARTICLE_COUNT = 500;        // Кол-во частиц
const MAX_DISTANCE = 120;         // Дистанция, при которой частицы соединяются линией
const CURSOR_DISTANCE = 60;      // Дистанция, при которой частица соединяется с курсором
const PARTICLE_RADIUS = 3;        // Радиус рисуемой частицы

// Массив для частиц
const particles = [];

// Положение курсора (по умолчанию где-то за пределами экрана)
const mouse = {
    x: null,
    y: null
};

// ------------------------------------------------
// Класс частицы
// ------------------------------------------------
class Particle {
    constructor() {
        // Случайные начальные координаты в пределах окна
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;

        // Случайная небольшая скорость, чтобы частицы слегка двигались
        // (можно сделать скорость очень маленькой, чтобы &laquo;еле дрожали&raquo;)
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = (Math.random() - 0.5) * 0.5;
    }

    update() {
        // Двигаем частицу
        this.x += this.vx;
        this.y += this.vy;

        // Если частица вылетает за край, разворачиваем скорость
        if (this.x < 0 || this.x > canvas.width)  this.vx *= -1;
        if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
    }

    draw() {
        // Рисуем саму частицу (круг)
        ctx.beginPath();
        ctx.arc(this.x, this.y, PARTICLE_RADIUS, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';  // Цвет самих точек
        ctx.fill();
    }
}

// ------------------------------------------------
// Инициализация: создаём частицы
// ------------------------------------------------
function initParticles() {
    for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push(new Particle());
    }
}

// ------------------------------------------------
// Анимация
// ------------------------------------------------
function animate() {
    // Очищаем canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Обновляем и рисуем частицы
    for (let i = 0; i < particles.length; i++) {
        particles[i].update();
        particles[i].draw();
    }

    // Соединяем линии между близкими частицами
    connectParticles();

    // Просим браузер вызвать animate() перед следующим кадром
    requestAnimationFrame(animate);
}

// ------------------------------------------------
// Функция для соединения частиц линиями, если расстояние маленькое
// И линия к курсору, если курсор рядом
// ------------------------------------------------
function connectParticles() {
    for (let i = 0; i < particles.length; i++) {
        const p1 = particles[i];

        // Проверяем расстояние до курсора
        const dx1 = p1.x - mouse.x;
        const dy1 = p1.y - mouse.y;
        const dist1 = Math.sqrt(dx1 * dx1 + dy1 * dy1);
        if (dist1 < CURSOR_DISTANCE) {
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(mouse.x, mouse.y);
            ctx.strokeStyle = '#ffffff'; // цвет линий
            ctx.lineWidth = 1;
            ctx.stroke();
        }

        // Проверяем расстояние между p1 и остальными p2
        for (let j = i + 1; j < particles.length; j++) {
            const p2 = particles[j];
            const dx = p1.x - p2.x;
            const dy = p1.y - p2.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < MAX_DISTANCE) {
                // Рисуем линию
                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);

                // Можно менять прозрачность в зависимости от дистанции,
                // например, чем дальше друг от друга – тем меньше opacity
                const opacity = 1 - dist / MAX_DISTANCE;
                ctx.strokeStyle = `rgba(45, 52, 54, ${opacity})`;
                ctx.lineWidth = 1;
                ctx.stroke();
            }
        }
    }
}

// ------------------------------------------------
// Обработчик движения мыши
// ------------------------------------------------
window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
});

// Если мышь уходит за пределы окна – делаем x,y = null,
// чтобы линии не тащились за "несуществующим" курсором
window.addEventListener('mouseout', () => {
    mouse.x = null;
    mouse.y = null;
});

// Запускаем
initParticles();
animate();