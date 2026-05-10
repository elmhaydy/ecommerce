const slides = document.querySelectorAll(".hero-slide");
const dots = document.querySelectorAll("#heroDots button");
const prevBtn = document.getElementById("heroPrev");
const nextBtn = document.getElementById("heroNext");
const productsCarousel = document.getElementById("productsCarousel");
const productsTrack = document.getElementById("productsTrack");
const productsPrev = document.getElementById("productsPrev");
const productsNext = document.getElementById("productsNext");

let currentSlide = 0;
let sliderTimer = null;

function showSlide(index) {
  slides.forEach((slide) => slide.classList.remove("active"));
  dots.forEach((dot) => dot.classList.remove("active"));

  slides[index].classList.add("active");
  dots[index].classList.add("active");

  currentSlide = index;
}

function nextSlide() {
  const next = (currentSlide + 1) % slides.length;
  showSlide(next);
}

function prevSlide() {
  const prev = (currentSlide - 1 + slides.length) % slides.length;
  showSlide(prev);
}

function startSlider() {
  sliderTimer = setInterval(nextSlide, 4500);
}

function resetSlider() {
  clearInterval(sliderTimer);
  startSlider();
}

if (slides.length > 0) {
  startSlider();
}

if (nextBtn) {
  nextBtn.addEventListener("click", () => {
    nextSlide();
    resetSlider();
  });
}

if (prevBtn) {
  prevBtn.addEventListener("click", () => {
    prevSlide();
    resetSlider();
  });
}

dots.forEach((dot, index) => {
  dot.addEventListener("click", () => {
    showSlide(index);
    resetSlider();
  });
});

if (productsCarousel && productsTrack && productsPrev && productsNext) {
  const productCards = Array.from(productsTrack.querySelectorAll(".product-card"));
  let productsIndex = 0;
  let visibleCards = 4;

  const getVisibleCards = () => {
    if (window.innerWidth <= 650) return 1;
    if (window.innerWidth <= 1050) return 2;
    return 4;
  };

  const syncProductsTrack = () => {
    visibleCards = getVisibleCards();
    const maxIndex = Math.max(productCards.length - visibleCards, 0);
    productsIndex = Math.min(productsIndex, maxIndex);

    const cardWidth = productCards[0]?.getBoundingClientRect().width || 0;
    const trackStyle = window.getComputedStyle(productsTrack);
    const gap = parseFloat(trackStyle.columnGap || trackStyle.gap || "0");
    const offset = (cardWidth + gap) * productsIndex;

    productsTrack.style.transform = `translateX(-${offset}px)`;
    productsPrev.disabled = productsIndex <= 0;
    productsNext.disabled = productsIndex >= maxIndex;
  };

  productsPrev.addEventListener("click", () => {
    productsIndex = Math.max(productsIndex - 1, 0);
    syncProductsTrack();
  });

  productsNext.addEventListener("click", () => {
    const maxIndex = Math.max(productCards.length - visibleCards, 0);
    productsIndex = Math.min(productsIndex + 1, maxIndex);
    syncProductsTrack();
  });

  window.addEventListener("resize", syncProductsTrack);
  syncProductsTrack();
}
