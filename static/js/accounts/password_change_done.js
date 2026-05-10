document.addEventListener("DOMContentLoaded", () => {
  const card = document.querySelector(".password-done-card");

  if (card) {
    card.animate(
      [
        { opacity: 0, transform: "translateY(18px)" },
        { opacity: 1, transform: "translateY(0)" },
      ],
      { duration: 450, easing: "ease-out", fill: "forwards" },
    );
  }
});
