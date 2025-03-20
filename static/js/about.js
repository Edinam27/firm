AOS.init({
  duration: 1000,
  once: true,
});

// Add number counter animation
const countElements = document.querySelectorAll('.stat-number');

const animateCount = (element) => {
    const target = parseInt(element.dataset.count);
    const duration = 2000;
    const step = target / duration * 10;
    let current = 0;
    
    const timer = setInterval(() => {
        current += step;
        element.textContent = Math.floor(current).toLocaleString();
        
        if (current >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        }
    }, 10);
};

// Trigger animation when element is in view
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateCount(entry.target);
            observer.unobserve(entry.target);
        }
    });
});

countElements.forEach(element => observer.observe(element));