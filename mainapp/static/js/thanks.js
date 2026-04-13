const canvas = document.getElementById('fireworks');
const ctx = canvas.getContext('2d');

let particles = [];
let fireworks = [];

// === НАЛАШТУВАННЯ СЕРІЇ ===
const TOTAL_FIREWORKS = 12;        // кількість феєрверків
const STAGGER_DELAY = 80;          // затримка між запусками (мс)

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

class Firework {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = canvas.height;
        this.targetY = Math.random() * (canvas.height * 0.32);
        this.speed = Math.random() * 6 + 8;        // трохи швидше
        this.color = ['#7c5cff', '#22d3ee', '#22c55e', '#ff4d6d'][Math.floor(Math.random() * 4)];
        this.exploded = false;
        this.radius = 3.5;
    }

    update() {
        if (!this.exploded) {
            this.y -= this.speed;
            this.speed *= 0.965;                    // трохи м’якше сповільнення

            // ГАРАНТОВАНИЙ ВИБУХ
            if (this.y <= this.targetY || this.speed < 0.8) {
                this.explode();
            }
        }
    }

    explode() {
        this.exploded = true;
        const particleCount = 70;                   // яскраві вибухи
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle(this.x, this.y, this.color));
        }
    }

    draw() {
        if (!this.exploded) {
            ctx.save();
            ctx.shadowBlur = 18;
            ctx.shadowColor = this.color;
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }
}

class Particle {
    constructor(x, y, color) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.size = Math.random() * 5.5 + 2;
        this.speedX = Math.random() * 9.5 - 4.75;
        this.speedY = Math.random() * 9.5 - 8;
        this.gravity = 0.13;
        this.life = 78;
        this.alpha = 1;
    }

    update() {
        this.speedY += this.gravity;
        this.x += this.speedX;
        this.y += this.speedY;
        this.life--;
        this.alpha = this.life / 78;
    }

    draw() {
        ctx.save();
        ctx.globalAlpha = this.alpha * 0.95;
        ctx.shadowBlur = 14;
        ctx.shadowColor = this.color;
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x - this.size/2, this.y - this.size/2, this.size, this.size);
        ctx.restore();
    }
}

function launchFirework() {
    fireworks.push(new Firework());
}

function animate() {
    ctx.fillStyle = 'rgba(11, 15, 25, 0.22)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // феєрверки
    for (let i = fireworks.length - 1; i >= 0; i--) {
        fireworks[i].update();
        fireworks[i].draw();
        if (fireworks[i].exploded) fireworks.splice(i, 1);
    }

    // частинки
    for (let i = particles.length - 1; i >= 0; i--) {
        particles[i].update();
        particles[i].draw();
        if (particles[i].life <= 0) particles.splice(i, 1);
    }

    requestAnimationFrame(animate);
}

// === ЗАПУСК СКІНЧЕННОЇ СЕРІЇ ===
function startFireworksShow() {
    for (let i = 0; i < TOTAL_FIREWORKS; i++) {
        setTimeout(() => {
            launchFirework();
        }, i * STAGGER_DELAY);
    }
}

// Ініціалізація
window.addEventListener('resize', resizeCanvas);
resizeCanvas();
animate();

// Запускаємо святковий салют
setTimeout(startFireworksShow, 250);

console.log('%c✅ Салют виправлений — тепер феєрверки 100% вибухають!', 'color:#22d3ee; font-size:16px');