document.querySelectorAll(".toggle-password").forEach((btn) => {
  btn.addEventListener("click", () => {
    const wrapper = btn.closest(".auth-input-wrap");
    const input = wrapper ? wrapper.querySelector("input") : null;

    if (!input) return;

    if (input.type === "password") {
      input.type = "text";
      btn.textContent = "🙈";
    } else {
      input.type = "password";
      btn.textContent = "👁";
    }
  });
});