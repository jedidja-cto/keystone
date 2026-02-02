document.addEventListener('DOMContentLoaded', () => {
    // 1. Reveal animations on scroll
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Elements to animate
    const animateElements = document.querySelectorAll('.feature-card, .phase-item, h2');
    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(40px)';
        el.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
        observer.observe(el);
    });

    // 2. Parallax effect for blobs
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const blob1 = document.querySelector('.blob-1');
        const blob2 = document.querySelector('.blob-2');

        blob1.style.transform = `translate(${scrolled * 0.1}px, ${scrolled * 0.1}px)`;
        blob2.style.transform = `translate(${scrolled * -0.1}px, ${scrolled * -0.1}px)`;
    });

    // 3. Smooth scroll for navigation
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});
