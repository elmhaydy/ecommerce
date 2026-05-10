const mobileBtn = document.getElementById("mobileBtn");
const navMenu = document.getElementById("navMenu");
const scrollTopBtn = document.getElementById("scrollTop");
const topStripMessage = document.getElementById("topStripMessage");
const siteHeader = document.querySelector(".site-header");
const supportChatShell = document.getElementById("supportChatShell");
const supportChatPanel = document.getElementById("supportChatPanel");
const supportChatToggle = document.getElementById("supportChatToggle");
const supportChatBadge = document.getElementById("supportChatBadge");
const supportChatClose = document.getElementById("supportChatClose");
const supportChatForm = document.getElementById("supportChatForm");
const supportChatInput = document.getElementById("supportChatInput");
const supportChatMessages = document.getElementById("supportChatMessages");
const searchToggle = document.getElementById("searchToggle");
const searchDropdownShell = document.getElementById("searchDropdownShell");
const searchDropdownPanel = document.getElementById("searchDropdownPanel");
const headerSearchInput = document.getElementById("headerSearchInput");
const searchResultsSection = document.getElementById("searchResultsSection");
const searchResultsList = document.getElementById("searchResultsList");
const searchResultsEmpty = document.getElementById("searchResultsEmpty");
const searchViewAllLink = document.getElementById("searchViewAllLink");
const searchDiscoverySections = document.getElementById("searchDiscoverySections");
const profileMenu = document.getElementById("profileMenu");
const profileToggle = document.getElementById("profileToggle");
const languageMenu = document.getElementById("languageMenu");
const languageToggle = document.getElementById("languageToggle");
const cartToggle = document.getElementById("cartToggle");
const cartDrawer = document.getElementById("cartDrawer");
const cartDrawerOverlay = document.getElementById("cartDrawerOverlay");
const cartDrawerClose = document.getElementById("cartDrawerClose");
const cartCountBadge = cartToggle ? cartToggle.querySelector(".cart-count-badge") : null;
const scrollTopIcon = scrollTopBtn ? scrollTopBtn.querySelector("svg") : null;
let supportChatPollTimer = null;
let supportChatSignature = "";

const syncSupportBadge = (count) => {
  if (!supportChatBadge) return;
  const safeCount = Number(count) || 0;
  if (safeCount > 0) {
    supportChatBadge.textContent = safeCount > 99 ? "99+" : String(safeCount);
    supportChatBadge.hidden = false;
    return;
  }
  supportChatBadge.hidden = true;
};

if (mobileBtn && navMenu) {
  mobileBtn.addEventListener("click", () => {
    navMenu.classList.toggle("active");
  });
}

if (languageMenu && languageToggle) {
  languageToggle.addEventListener("click", (event) => {
    event.stopPropagation();
    const isOpen = languageMenu.classList.toggle("open");
    languageToggle.setAttribute("aria-expanded", String(isOpen));
  });

  document.addEventListener("click", (event) => {
    if (!languageMenu.contains(event.target)) {
      languageMenu.classList.remove("open");
      languageToggle.setAttribute("aria-expanded", "false");
    }
  });
}

const closeCartDrawer = () => {
  if (!cartDrawer || !cartDrawerOverlay || !cartToggle) return;
  cartDrawer.classList.remove("is-open");
  cartDrawerOverlay.classList.remove("is-open");
  cartDrawer.setAttribute("aria-hidden", "true");
  cartToggle.setAttribute("aria-expanded", "false");
  document.body.classList.remove("drawer-open");
};

const openCartDrawer = () => {
  if (!cartDrawer || !cartDrawerOverlay || !cartToggle) return;
  cartDrawer.classList.add("is-open");
  cartDrawerOverlay.classList.add("is-open");
  cartDrawer.setAttribute("aria-hidden", "false");
  cartToggle.setAttribute("aria-expanded", "true");
  document.body.classList.add("drawer-open");
};

const closeSearchDropdown = () => {
  if (!searchToggle || !searchDropdownShell) return;
  searchDropdownShell.classList.remove("is-open");
  searchToggle.setAttribute("aria-expanded", "false");
};

const openSearchDropdown = () => {
  if (!searchToggle || !searchDropdownShell) return;
  searchDropdownShell.classList.add("is-open");
  searchToggle.setAttribute("aria-expanded", "true");
  window.setTimeout(() => headerSearchInput?.focus(), 10);
};

const getSupportStatusMeta = (status) => {
  const map = {
    sending: { symbol: "○", className: "is-sending", title: "Sending" },
    sent: { symbol: "✓", className: "is-sent", title: "Sent" },
    delivered: { symbol: "✓✓", className: "is-delivered", title: "Delivered" },
    read: { symbol: "✓✓", className: "is-read", title: "Read" },
    failed: { symbol: "!", className: "is-failed", title: "Failed" },
  };
  return map[status] || null;
};

const getSupportDateKey = (timestampIso) => {
  if (!timestampIso) return "";
  const date = new Date(timestampIso);
  if (Number.isNaN(date.getTime())) return "";
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

const formatSupportDateLabel = (timestampIso) => {
  if (!timestampIso) return "";
  const date = new Date(timestampIso);
  if (Number.isNaN(date.getTime())) return "";
  const language = supportChatShell?.dataset.language || "fr";
  return new Intl.DateTimeFormat(language === "en" ? "en-GB" : "fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric"
  }).format(date);
};

const appendSupportDateDivider = (timestampIso) => {
  if (!supportChatMessages) return;
  const label = formatSupportDateLabel(timestampIso);
  const dateKey = getSupportDateKey(timestampIso);
  if (!label || !dateKey) return;

  const divider = document.createElement("div");
  divider.className = "support-chat-date-divider";
  divider.dataset.dateKey = dateKey;
  divider.textContent = label;
  supportChatMessages.appendChild(divider);
};

const appendSupportMessage = (text, role, status = "", timestamp = "") => {
  if (!supportChatMessages) return;

  const article = document.createElement("article");
  article.className = `support-message ${role === "user" ? "support-message-user" : "support-message-bot"}`;
  if (status) {
    article.dataset.status = status;
  }

  const bubble = document.createElement("div");
  bubble.className = "support-message-bubble";

  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  bubble.appendChild(paragraph);

  if (timestamp || (role === "user" && status)) {
    const metaLine = document.createElement("div");
    metaLine.className = "support-message-meta";

    if (timestamp) {
      const timeElement = document.createElement("small");
      timeElement.className = "support-message-time";
      timeElement.textContent = timestamp;
      metaLine.appendChild(timeElement);
    }

    if (role === "user" && status) {
      const meta = getSupportStatusMeta(status);
      const statusLine = document.createElement("small");
      statusLine.className = "support-message-status";
      if (meta) {
        statusLine.classList.add(meta.className);
        statusLine.textContent = meta.symbol;
        statusLine.setAttribute("title", meta.title);
        statusLine.setAttribute("aria-label", meta.title);
      }
      metaLine.appendChild(statusLine);
    }

    bubble.appendChild(metaLine);
  }

  article.appendChild(bubble);
  supportChatMessages.appendChild(article);
  supportChatMessages.scrollTop = supportChatMessages.scrollHeight;
  return article;
};

const renderSupportHistory = (messages) => {
  if (!supportChatMessages) return;

  supportChatMessages.innerHTML = "";

  if (!messages.length) {
    const language = supportChatShell?.dataset.language || "fr";
    const welcomeMessage = language === "en"
      ? supportChatShell?.dataset.welcomeEn
      : supportChatShell?.dataset.welcomeFr;

    if (welcomeMessage) {
      appendSupportMessage(welcomeMessage, "bot");
    }
    return;
  }

  let lastDateKey = "";
  messages.forEach((message) => {
    const currentDateKey = getSupportDateKey(message.created_at_iso);
    if (currentDateKey && currentDateKey !== lastDateKey) {
      appendSupportDateDivider(message.created_at_iso);
      lastDateKey = currentDateKey;
    }

    appendSupportMessage(
      message.body,
      message.is_staff ? "bot" : "user",
      message.is_staff ? "" : message.status,
      message.created_at || ""
    );
  });
};

const buildSupportSignature = (messages) => messages.map((message) => `${message.id}:${message.created_at_iso || message.created_at}:${message.status || ""}`).join("|");

const closeSupportChat = () => {
  if (!supportChatPanel || !supportChatToggle) return;
  supportChatPanel.classList.remove("is-open");
  supportChatPanel.setAttribute("aria-hidden", "true");
  supportChatToggle.setAttribute("aria-expanded", "false");
  if (supportChatPollTimer) {
    window.clearInterval(supportChatPollTimer);
    supportChatPollTimer = null;
  }
};

const openSupportChat = () => {
  if (!supportChatPanel || !supportChatToggle) return;
  supportChatPanel.classList.add("is-open");
  supportChatPanel.setAttribute("aria-hidden", "false");
  supportChatToggle.setAttribute("aria-expanded", "true");
  window.setTimeout(() => supportChatInput?.focus(), 10);
};

const loadSupportHistory = async () => {
  if (!supportChatShell || !supportChatMessages) return;

  const isAuthenticated = supportChatShell.dataset.authenticated === "true";
  const language = supportChatShell.dataset.language || "fr";

  if (!isAuthenticated) {
    const loginMessage = language === "en"
      ? supportChatShell.dataset.loginEn
      : supportChatShell.dataset.loginFr;
    renderSupportHistory([]);
    if (loginMessage) {
      supportChatMessages.innerHTML = "";
      appendSupportMessage(loginMessage, "bot");
    }
    supportChatForm?.classList.add("is-disabled");
    supportChatInput?.setAttribute("disabled", "disabled");
    return;
  }

  supportChatForm?.classList.remove("is-disabled");
  supportChatInput?.removeAttribute("disabled");

  const historyUrl = supportChatShell.dataset.historyUrl;
  if (!historyUrl) return;

  try {
    const response = await fetch(historyUrl, {
      headers: {
        "X-Requested-With": "XMLHttpRequest"
      },
      credentials: "same-origin"
    });

    if (!response.ok) {
      throw new Error("Support history request failed");
    }

    const payload = await response.json();
    const messages = payload.messages || [];
    const nextSignature = buildSupportSignature(messages);
    syncSupportBadge(payload.unread_count || 0);

    if (nextSignature !== supportChatSignature) {
      supportChatSignature = nextSignature;
      renderSupportHistory(messages);
    }
  } catch (error) {
    const fallback = language === "en"
      ? supportChatShell.dataset.errorEn
      : supportChatShell.dataset.errorFr;
    renderSupportHistory([]);
    if (fallback) {
      supportChatMessages.innerHTML = "";
      appendSupportMessage(fallback, "bot");
    }
  }
};

const loadSupportStatus = async () => {
  if (!supportChatShell || supportChatShell.dataset.authenticated !== "true") {
    syncSupportBadge(0);
    return;
  }

  const statusUrl = supportChatShell.dataset.statusUrl;
  if (!statusUrl) return;

  try {
    const response = await fetch(statusUrl, {
      headers: {
        "X-Requested-With": "XMLHttpRequest"
      },
      credentials: "same-origin"
    });

    if (!response.ok) {
      throw new Error("Support status request failed");
    }

    const payload = await response.json();
    syncSupportBadge(payload.unread_count || 0);
  } catch (error) {
    syncSupportBadge(0);
  }
};

const startSupportChatPolling = () => {
  if (supportChatPollTimer) {
    window.clearInterval(supportChatPollTimer);
  }

  supportChatPollTimer = window.setInterval(() => {
    if (supportChatPanel?.classList.contains("is-open")) {
      loadSupportHistory();
    } else {
      loadSupportStatus();
    }
  }, 5000);
};

const escapeHtml = (value) => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#39;");

const showSearchDiscovery = () => {
  searchDiscoverySections?.classList.remove("is-hidden");
  searchResultsSection?.classList.add("is-hidden");
};

const showSearchResults = () => {
  searchDiscoverySections?.classList.add("is-hidden");
  searchResultsSection?.classList.remove("is-hidden");
};

const renderSearchSuggestions = (results, query) => {
  if (!searchResultsList || !searchResultsEmpty || !searchViewAllLink || !searchDropdownShell) {
    return;
  }

  const viewAllUrl = `/products/?q=${encodeURIComponent(query)}`;
  searchViewAllLink.href = viewAllUrl;

  if (!results.length) {
    searchResultsList.innerHTML = "";
    searchResultsEmpty.classList.remove("is-hidden");
    showSearchResults();
    return;
  }

  const priceSuffix = searchDropdownShell.dataset.priceSuffix || "DH";

  searchResultsList.innerHTML = results.map((item) => `
    <a href="${escapeHtml(item.url)}" class="search-suggestion-item">
      <span class="search-suggestion-image">
        ${item.image_url ? `<img src="${escapeHtml(item.image_url)}" alt="${escapeHtml(item.name)}">` : ""}
      </span>
      <span class="search-suggestion-content">
        <strong>${escapeHtml(item.name)}</strong>
        ${item.category ? `<small>${escapeHtml(item.category)}</small>` : ""}
      </span>
      <span class="search-suggestion-price">
        <span>${escapeHtml(item.price)} ${priceSuffix}</span>
        ${item.old_price ? `<del>${escapeHtml(item.old_price)} ${priceSuffix}</del>` : ""}
      </span>
    </a>
  `).join("");

  searchResultsEmpty.classList.add("is-hidden");
  showSearchResults();
};

let searchSuggestionsTimer = null;
let searchSuggestionsController = null;

const requestSearchSuggestions = async (query) => {
  if (!searchDropdownShell) return;

  const trimmedQuery = query.trim();
  if (trimmedQuery.length < 2) {
    if (searchSuggestionsController) {
      searchSuggestionsController.abort();
      searchSuggestionsController = null;
    }
    showSearchDiscovery();
    return;
  }

  const suggestionsUrl = searchDropdownShell.dataset.suggestionsUrl;
  if (!suggestionsUrl) return;

  if (searchSuggestionsController) {
    searchSuggestionsController.abort();
  }

  searchSuggestionsController = new AbortController();

  try {
    const response = await fetch(`${suggestionsUrl}?q=${encodeURIComponent(trimmedQuery)}`, {
      headers: {
        "X-Requested-With": "XMLHttpRequest"
      },
      signal: searchSuggestionsController.signal
    });

    if (!response.ok) {
      throw new Error("Search suggestions request failed");
    }

    const payload = await response.json();
    renderSearchSuggestions(payload.results || [], trimmedQuery);
  } catch (error) {
    if (error.name !== "AbortError") {
      showSearchDiscovery();
    }
  }
};

const getCsrfToken = (form) => {
  const input = form?.querySelector("input[name='csrfmiddlewaretoken']");
  return input ? input.value : "";
};

const renderCartDrawer = (cart) => {
  if (!cartDrawer) return;

  const body = cartDrawer.querySelector(".cart-drawer-body");
  const footer = cartDrawer.querySelector(".cart-drawer-footer");
  const productBaseUrl = cartDrawer.dataset.productBaseUrl || "/products/";
  const cartUrl = cartDrawer.dataset.cartUrl || "#";
  const checkoutUrl = cartDrawer.dataset.checkoutUrl || "#";
  const emptyTitle = cartDrawer.dataset.emptyTitle || "Votre panier est vide";
  const emptyText = cartDrawer.dataset.emptyText || "";
  const subtotalLabel = cartDrawer.dataset.subtotalLabel || "Sous-total";
  const backCartLabel = cartDrawer.dataset.backCartLabel || "Retour au panier";
  const checkoutLabel = cartDrawer.dataset.checkoutLabel || "Verification";
  const removeLabel = cartDrawer.dataset.removeLabel || "Supprimer";
  const decreaseLabel = cartDrawer.dataset.decreaseLabel || "Reduire";
  const increaseLabel = cartDrawer.dataset.increaseLabel || "Augmenter";

  if (cartCountBadge) {
    if (cart.count > 0) {
      cartCountBadge.textContent = String(cart.count);
      cartCountBadge.hidden = false;
    } else {
      cartCountBadge.hidden = true;
    }
  }

  if (!body || !footer) return;

  if (!cart.items.length) {
    body.innerHTML = `
      <div class="cart-drawer-empty">
        <span class="cart-drawer-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <circle cx="9" cy="20" r="1.6"></circle>
            <circle cx="18" cy="20" r="1.6"></circle>
            <path d="M3 4h2l2.3 10.2a1 1 0 0 0 1 .8h9.7a1 1 0 0 0 1-.8L21 7H7"></path>
          </svg>
        </span>
        <strong>${emptyTitle}</strong>
        <p>${emptyText}</p>
      </div>
    `;
  } else {
    body.innerHTML = `
      <div class="cart-drawer-list">
        ${cart.items.map((item) => {
          const productHref = `${productBaseUrl}${encodeURIComponent(item.product_slug)}/`;
          return `
          <article class="cart-drawer-item">
            <span class="cart-drawer-check" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path d="M6 12.5 10 16l8-9"></path></svg>
            </span>
            <a href="${productHref}" class="cart-drawer-item-image">
              ${item.image_url ? `<img src="${item.image_url}" alt="${item.product_name}">` : `<span>${item.product_name}</span>`}
            </a>
            <div class="cart-drawer-item-content">
              <a href="${productHref}" class="cart-drawer-item-title">${item.product_name}</a>
              <div class="cart-drawer-price-row">
                <strong>${item.price} DH</strong>
                ${item.old_price ? `<del>${item.old_price} DH</del>` : ""}
              </div>
              <div class="cart-drawer-actions-row">
                <form method="post" action="/cart/update/${item.id}/" class="cart-drawer-qty-form">
                  <input type="hidden" name="csrfmiddlewaretoken" value="">
                  <button type="submit" name="action" value="decrease" aria-label="${decreaseLabel}">
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 12h12"></path></svg>
                  </button>
                  <span>${item.quantity}</span>
                  <button type="submit" name="action" value="increase" aria-label="${increaseLabel}">
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 6v12"></path><path d="M6 12h12"></path></svg>
                  </button>
                </form>
                <a href="/cart/remove/${item.id}/" class="cart-drawer-remove" aria-label="${removeLabel}">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M4 7h16"></path>
                    <path d="M9 7V5h6v2"></path>
                    <path d="M8 7l1 12h6l1-12"></path>
                    <path d="M10 11v5"></path>
                    <path d="M14 11v5"></path>
                  </svg>
                </a>
              </div>
            </div>
          </article>
        `;
        }).join("")}
      </div>
    `;

    const existingToken = document.querySelector("input[name='csrfmiddlewaretoken']");
    const tokenValue = existingToken ? existingToken.value : "";
    body.querySelectorAll(".cart-drawer-qty-form input[name='csrfmiddlewaretoken']").forEach((input) => {
      input.value = tokenValue;
    });
  }

  footer.innerHTML = `
    <div class="cart-drawer-summary">
      <span>${subtotalLabel}</span>
      <strong>${cart.total} DH</strong>
    </div>
    <a href="${cartUrl}" class="cart-drawer-secondary">${backCartLabel}</a>
    <a href="${checkoutUrl}" class="cart-drawer-btn">${checkoutLabel}</a>
  `;
};

const submitCartMutation = async (url, options = {}) => {
  const response = await fetch(url, {
    headers: {
      "X-Requested-With": "XMLHttpRequest"
    },
    credentials: "same-origin",
    ...options
  });

  if (!response.ok) {
    throw new Error("Cart request failed");
  }

  const payload = await response.json();
  if (payload?.cart) {
    renderCartDrawer(payload.cart);
  }
};

window.openCartDrawer = openCartDrawer;
window.closeCartDrawer = closeCartDrawer;
window.renderCartDrawer = renderCartDrawer;

if (searchToggle && searchDropdownShell) {
  searchToggle.addEventListener("click", (event) => {
    event.stopPropagation();
    const isOpen = searchDropdownShell.classList.contains("is-open");

    closeCartDrawer();
    if (profileMenu) {
      profileMenu.classList.remove("open");
      profileToggle?.setAttribute("aria-expanded", "false");
    }

    if (isOpen) {
      closeSearchDropdown();
      return;
    }

    openSearchDropdown();
  });

  document.addEventListener("click", (event) => {
    if (!searchDropdownShell.contains(event.target) && !searchToggle.contains(event.target)) {
      closeSearchDropdown();
    }
  });
}

if (supportChatToggle && supportChatPanel) {
  const supportTriggers = [supportChatToggle, ...document.querySelectorAll(".support-btn")];

  supportTriggers.forEach((trigger) => {
    trigger.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      const isOpen = supportChatPanel.classList.contains("is-open");

      if (isOpen) {
        closeSupportChat();
        return;
      }

      closeSearchDropdown();
      closeCartDrawer();
      if (profileMenu) {
        profileMenu.classList.remove("open");
        profileToggle?.setAttribute("aria-expanded", "false");
      }
      openSupportChat();
      loadSupportHistory();
      startSupportChatPolling();
    });
  });

  supportChatClose?.addEventListener("click", closeSupportChat);

  document.addEventListener("click", (event) => {
    if (
      supportChatPanel.classList.contains("is-open")
      && !supportChatPanel.contains(event.target)
      && !supportTriggers.some((trigger) => trigger.contains(event.target))
    ) {
      closeSupportChat();
    }
  });
}

if (supportChatShell) {
  loadSupportStatus();
  startSupportChatPolling();
}

if (supportChatForm && supportChatInput && supportChatMessages && supportChatShell) {
  supportChatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (supportChatShell.dataset.authenticated !== "true") {
      const loginUrl = supportChatShell.dataset.loginUrl;
      if (loginUrl) {
        window.location.href = `${loginUrl}?next=${encodeURIComponent(window.location.pathname)}`;
      }
      return;
    }

    const message = supportChatInput.value.trim();
    if (!message) return;

    const sendUrl = supportChatShell.dataset.sendUrl;
    const csrfToken = supportChatForm.querySelector("input[name='csrfmiddlewaretoken']")?.value || "";
    const language = supportChatShell.dataset.language || "fr";
    const defaultError = language === "en"
      ? supportChatShell.dataset.errorEn
      : supportChatShell.dataset.errorFr;

    const pendingDate = new Date();
    const pendingTimestamp = pendingDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const pendingTimestampIso = pendingDate.toISOString();
    const pendingDateKey = getSupportDateKey(pendingTimestampIso);
    const lastDivider = supportChatMessages.querySelector(".support-chat-date-divider:last-of-type");
    if (!lastDivider || lastDivider.dataset.dateKey !== pendingDateKey) {
      appendSupportDateDivider(pendingTimestampIso);
    }
    const pendingMessageElement = appendSupportMessage(message, "user", "sending", pendingTimestamp);
    supportChatInput.value = "";
    supportChatInput.style.height = "";

    const pendingMessage = document.createElement("article");
    pendingMessage.className = "support-message support-message-bot is-loading";
    pendingMessage.innerHTML = '<div class="support-message-bubble"><p>...</p></div>';
    supportChatMessages.appendChild(pendingMessage);
    supportChatMessages.scrollTop = supportChatMessages.scrollHeight;

    try {
      const response = await fetch(sendUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest"
        },
        credentials: "same-origin",
        body: JSON.stringify({ message })
      });

      const payload = await response.json();
      pendingMessage.remove();

      if (!response.ok || !payload.ok) {
        appendSupportMessage(payload.message || defaultError, "bot");
        if (pendingMessageElement) {
          const statusLine = pendingMessageElement.querySelector(".support-message-status");
          if (statusLine) {
            const meta = getSupportStatusMeta("failed");
            statusLine.className = `support-message-status ${meta.className}`;
            statusLine.textContent = meta.symbol;
            statusLine.setAttribute("title", meta.title);
            statusLine.setAttribute("aria-label", meta.title);
          }
        }
        return;
      }

      if (!payload.message?.body) {
        appendSupportMessage(defaultError, "bot");
        return;
      }

      loadSupportHistory();
    } catch (error) {
      pendingMessage.remove();
      if (pendingMessageElement) {
        const statusLine = pendingMessageElement.querySelector(".support-message-status");
        if (statusLine) {
          const meta = getSupportStatusMeta("failed");
          statusLine.className = `support-message-status ${meta.className}`;
          statusLine.textContent = meta.symbol;
          statusLine.setAttribute("title", meta.title);
          statusLine.setAttribute("aria-label", meta.title);
        }
      }
      appendSupportMessage(defaultError || "Support unavailable.", "bot");
    }
  });

  supportChatInput.addEventListener("input", () => {
    supportChatInput.style.height = "auto";
    supportChatInput.style.height = `${Math.min(supportChatInput.scrollHeight, 120)}px`;
  });

  supportChatInput.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" || event.shiftKey) {
      return;
    }

    event.preventDefault();

    if (typeof supportChatForm.requestSubmit === "function") {
      supportChatForm.requestSubmit();
      return;
    }

    supportChatForm.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
  });
}

if (headerSearchInput) {
  headerSearchInput.addEventListener("input", (event) => {
    const query = event.target.value;

    if (searchSuggestionsTimer) {
      window.clearTimeout(searchSuggestionsTimer);
    }

    searchSuggestionsTimer = window.setTimeout(() => {
      requestSearchSuggestions(query);
    }, 180);
  });
}

if (cartToggle && cartDrawer && cartDrawerOverlay && cartDrawerClose) {
  cartToggle.addEventListener("click", (event) => {
    event.stopPropagation();
    const isOpen = cartDrawer.classList.contains("is-open");
    if (isOpen) {
      closeCartDrawer();
      return;
    }
    closeSearchDropdown();
    closeCartDrawer();
    openCartDrawer();
  });

  cartDrawerClose.addEventListener("click", closeCartDrawer);
  cartDrawerOverlay.addEventListener("click", closeCartDrawer);

  cartDrawer.addEventListener("submit", async (event) => {
    const form = event.target.closest(".cart-drawer-qty-form");
    if (!form) return;

    event.preventDefault();
    const formActionUrl = form.getAttribute("action");
    const submitter = event.submitter;
    const formData = new FormData(form);

    if (submitter?.name) {
      formData.set(submitter.name, submitter.value);
    }

    try {
      await submitCartMutation(formActionUrl, {
        method: "POST",
        body: formData
      });
    } catch (error) {
      window.location.href = formActionUrl;
    }
  });

  cartDrawer.addEventListener("click", async (event) => {
    const removeLink = event.target.closest(".cart-drawer-remove");
    if (!removeLink) return;

    event.preventDefault();

    try {
      await submitCartMutation(removeLink.href);
    } catch (error) {
      window.location.href = removeLink.href;
    }
  });
}

if (profileMenu && profileToggle) {
  profileToggle.addEventListener("click", (event) => {
    event.stopPropagation();
    const isOpen = profileMenu.classList.toggle("open");
    profileToggle.setAttribute("aria-expanded", String(isOpen));
  });

  document.addEventListener("click", (event) => {
    if (!profileMenu.contains(event.target)) {
      profileMenu.classList.remove("open");
      profileToggle.setAttribute("aria-expanded", "false");
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      profileMenu.classList.remove("open");
      profileToggle.setAttribute("aria-expanded", "false");
      closeCartDrawer();
      closeSearchDropdown();
      closeSupportChat();
    }
  });
}

const syncScrollButton = () => {
  if (!scrollTopBtn) return;

  const nearTop = window.scrollY < 120;
  scrollTopBtn.classList.add("show");
  scrollTopBtn.classList.toggle("is-down", nearTop);
  scrollTopBtn.setAttribute(
    "aria-label",
    nearTop ? "Aller en bas" : "Retour en haut"
  );

  if (scrollTopIcon) {
    scrollTopIcon.setAttribute(
      "aria-hidden",
      "true"
    );
  }
};

window.addEventListener("scroll", syncScrollButton);

const syncHeaderOnScroll = () => {
  if (!siteHeader) return;
  siteHeader.classList.toggle("is-scrolled", window.scrollY > 10);
};

window.addEventListener("scroll", syncHeaderOnScroll);
syncHeaderOnScroll();
syncScrollButton();

if (scrollTopBtn) {
  scrollTopBtn.addEventListener("click", () => {
    const nearTop = window.scrollY < 120;
    window.scrollTo({
      top: nearTop ? Math.max(window.innerHeight * 0.92, 680) : 0,
      behavior: "smooth"
    });
  });
}

if (topStripMessage) {
  const fullText = topStripMessage.dataset.text || topStripMessage.textContent.trim();
  const typingSpeed = 55;
  const deletingSpeed = 30;
  const pauseAfterTyping = 1800;
  const pauseAfterDeleting = 450;

  let index = 0;
  let isDeleting = false;

  const tick = () => {
    if (!isDeleting) {
      index += 1;
      topStripMessage.textContent = fullText.slice(0, index);

      if (index >= fullText.length) {
        isDeleting = true;
        window.setTimeout(tick, pauseAfterTyping);
        return;
      }

      window.setTimeout(tick, typingSpeed);
      return;
    }

    index -= 1;
    topStripMessage.textContent = fullText.slice(0, Math.max(index, 0));

    if (index <= 0) {
      isDeleting = false;
      window.setTimeout(tick, pauseAfterDeleting);
      return;
    }

    window.setTimeout(tick, deletingSpeed);
  };

  topStripMessage.textContent = "";
  window.setTimeout(tick, 500);
}
