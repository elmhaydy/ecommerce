document.addEventListener("DOMContentLoaded", () => {

  const card = document.querySelector(".success-card");

  if(card){
    card.animate(
      [
        {
          opacity:0,
          transform:"translateY(20px)"
        },
        {
          opacity:1,
          transform:"translateY(0)"
        }
      ],
      {
        duration:500,
        easing:"ease-out"
      }
    );
  }

});