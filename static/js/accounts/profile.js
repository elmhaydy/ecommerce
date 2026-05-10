document.addEventListener("DOMContentLoaded", () => {
  const orders = document.querySelectorAll(".profile-order");

  orders.forEach((order, index) => {
    order.animate(
      [
        { opacity: 0, transform: "translateY(14px)" },
        { opacity: 1, transform: "translateY(0)" },
      ],
      {
        duration: 320,
        delay: index * 80,
        easing: "ease-out",
        fill: "forwards",
      },
    );
  });
});
