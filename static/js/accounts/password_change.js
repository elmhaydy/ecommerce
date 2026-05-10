document.addEventListener("DOMContentLoaded", () => {
  const firstPasswordField = document.querySelector('.password-form input[type="password"]');

  if (firstPasswordField) {
    firstPasswordField.focus();
  }
});
