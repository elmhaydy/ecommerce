document.addEventListener("DOMContentLoaded", () => {
  const shippingZone = document.getElementById("shippingZone");
  const shippingFeeText = document.getElementById("shippingFee");
  const shippingCardFee = document.getElementById("shippingCardFee");
  const checkoutTotalText = document.getElementById("checkoutTotal");
  const cartFinalTotalInput = document.getElementById("cartFinalTotalValue");
  const checkoutCityMirror = document.getElementById("checkoutCityMirror");

  const summaryEmail = document.getElementById("summaryEmail");
  const summaryName = document.getElementById("summaryName");
  const summaryPhone = document.getElementById("summaryPhone");
  const summaryAddress = document.getElementById("summaryAddress");

  const emailInput = document.getElementById("checkoutEmail");
  const firstNameInput = document.getElementById("checkoutFirstName");
  const lastNameInput = document.getElementById("checkoutLastName");
  const phoneInput = document.getElementById("checkoutPhone");
  const addressInput = document.getElementById("checkoutAddress");
  const postalInput = document.getElementById("checkoutPostal");

  const openButtons = document.querySelectorAll("[data-open-modal]");
  const closeButtons = document.querySelectorAll("[data-close-modal]");
  const saveAddressButton = document.querySelector("[data-save-address]");

  const dealSwitchButton = document.querySelector("[data-deal-switch]");
  const dealProducts = Array.from(document.querySelectorAll("[data-deal-product]"));

  const toNumber = (value) => Number(String(value).replace(",", ".")) || 0;
  const formatPrice = (value) => `${value.toFixed(2)} DH`;

  function updateAddressSummary() {
    const selectedLabel = shippingZone?.options[shippingZone.selectedIndex]?.textContent || "";
    const selectedCity = selectedLabel.split("-")[0]?.trim() || "";

    const fullName = `${firstNameInput?.value || ""} ${lastNameInput?.value || ""}`.trim();

    const fullAddress = [
      addressInput?.value || "",
      selectedCity,
      postalInput?.value || ""
    ].filter(Boolean).join(" ");

    if (summaryEmail) summaryEmail.textContent = emailInput?.value || "-";
    if (summaryName) summaryName.textContent = fullName || "-";
    if (summaryPhone) summaryPhone.textContent = phoneInput?.value || "-";
    if (summaryAddress) summaryAddress.textContent = fullAddress || "-";
    if (checkoutCityMirror) checkoutCityMirror.value = selectedCity;
  }

  function updateTotal() {
    if (!shippingZone || !shippingFeeText || !checkoutTotalText || !cartFinalTotalInput) return;

    const selected = shippingZone.options[shippingZone.selectedIndex];
    const cartTotal = toNumber(cartFinalTotalInput.value);

    let fee = toNumber(selected.dataset.fee);
    const threshold = toNumber(selected.dataset.threshold);

    if (threshold > 0 && cartTotal >= threshold) {
      fee = 0;
    }

    shippingFeeText.textContent = formatPrice(fee);

    if (shippingCardFee) {
      shippingCardFee.textContent = formatPrice(fee);
    }

    checkoutTotalText.textContent = formatPrice(cartTotal + fee);

    updateAddressSummary();
  }

  function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.classList.remove("is-hidden");
    document.body.style.overflow = "hidden";
  }

  function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.classList.add("is-hidden");
    document.body.style.overflow = "";
  }

  openButtons.forEach((button) => {
    button.addEventListener("click", () => {
      openModal(button.dataset.openModal);
    });
  });

  closeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      closeModal(button.dataset.closeModal);
    });
  });

  document.querySelectorAll(".modal-overlay").forEach((overlay) => {
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) {
        overlay.classList.add("is-hidden");
        document.body.style.overflow = "";
      }
    });
  });

  saveAddressButton?.addEventListener("click", () => {
    updateAddressSummary();
    closeModal("addressModal");
  });

  [emailInput, firstNameInput, lastNameInput, phoneInput, addressInput, postalInput].forEach((input) => {
    input?.addEventListener("input", updateAddressSummary);
  });

  shippingZone?.addEventListener("change", updateTotal);

  if (dealProducts.length > 0) {
    let activeDealIndex = dealProducts.findIndex((item) => !item.classList.contains("is-hidden"));

    if (activeDealIndex < 0) {
      activeDealIndex = 0;
    }

    dealProducts.forEach((item, index) => {
      item.classList.toggle("is-hidden", index !== activeDealIndex);
    });

    dealSwitchButton?.addEventListener("click", () => {
      dealProducts[activeDealIndex].classList.add("is-hidden");

      activeDealIndex = (activeDealIndex + 1) % dealProducts.length;

      dealProducts[activeDealIndex].classList.remove("is-hidden");
    });
  }

  document.querySelectorAll(".deal-add-toggle").forEach((button) => {
    button.addEventListener("click", () => {
      button.classList.toggle("is-selected");
    });
  });

  updateTotal();
  updateAddressSummary();
});