document.addEventListener("DOMContentLoaded", () => {
  const emailInput = document.querySelector('.profile-edit-form input[name="email"]');

  if (emailInput) {
    emailInput.setAttribute("autocomplete", "email");
  }
});
