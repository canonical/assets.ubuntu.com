import "./products-search";
import handleProductsChip from "./products-search";

import "./authors-search";
import handleAuthorsChip from "./authors-search";
import "./sf_campaign-search";
import handleCampaignChip from "./sf_campaign-search";

import "./date-picker";
import "./generic-fields";

/*
 * Event delgation to handle the click event for search and filter.
 **/
document.addEventListener("click", function (e) {
  const targetChip = e.target.closest(".p-chip");
  // Handle chip clicks
  if (targetChip) {
    e.preventDefault();
    if (targetChip.closest(".js-products-search")) {
      handleProductsChip(targetChip);
      return;
    }
    if (targetChip.closest(".js-authors-search")) {
      handleAuthorsChip(targetChip);
      return;
    }
    if (targetChip.closest(".js-campaign-search")) {
      handleCampaignChip(targetChip);
      return;
    }
    // Handle clicks outside the search and filter
  } else if (!e.target.closest(".js-active-search")) {
    openPanel(document.querySelector(".js-active-search"), false, "click");
  }
});

/*
 * Generic function to show and hide the chips selection panel.
 * @param {HTMLElement} searchContainer - The whole pannel container.
 * @param {Boolean} opening - Whether the panel should being opening or not. Default is false.
 **/
export function openPanel(searchComponent, opening = "false") {
  if (searchComponent) {
    const searchContainer = searchComponent.querySelector(
      ".p-search-and-filter__search-container"
    );
    const panel = searchComponent.querySelector(".p-search-and-filter__panel");
    if (panel && searchContainer) {
      if (opening) {
        panel.setAttribute("aria-hidden", "false");
        searchContainer.setAttribute("aria-expanded", "true");
        searchComponent.classList.add("js-active-search");
      } else {
        panel.setAttribute("aria-hidden", "true");
        searchContainer.setAttribute("aria-expanded", "false");
        searchComponent.classList.remove("js-active-search");
      }
    }
  }
}

/*
 * Generic function to add the value of a selected chip, to the value of a hidden input.
 * We have to do this as the chips will not be submitted with the form.
 * @param {String} value - The value of the chip.
 * @param {HTMLElement} input - The hidden input to store the values.
 * @param {Boolean} replace - Whether to replace the current value or not. Default is false.
 **/
export function addValueToHiddenInput(value, input, replace = false) {
  let selectedChips = replace ? [] : input.value.split(",").filter(Boolean);
  if (!selectedChips.includes(value)) {
    selectedChips.push(value);
  }
  input.setAttribute("value", selectedChips.join(","));
}

/*
 * Generic function to remove the value of a selected chip, from the value of a hidden input.
 * @param {String} value - The value of the chip.
 * @param {HTMLElement} input - The hidden input to store the values.
 **/
export function removeValueFromHiddenInput(value, input) {
  let selectedChips = input.value.split(",").filter(Boolean);
  selectedChips = selectedChips.filter((id) => id !== value);
  input.setAttribute("value", selectedChips.join(","));
}

/*
 * Function to add a value to a query parameter.
 * @param {String} key - The query parameter key.
 * @param {String} value - The value to add.
 * @param {Boolean} replace - Whether to replace the current value or not. Default is false.
 **/
export function addValueToQueryParams(key, value, replace = false) {
  const url = new URL(window.location);
  if (replace) {
    url.searchParams.set(key, value);
  } else {
    const currentValues = url.searchParams.get(key)?.split(",") || [];
    if (!currentValues.includes(value)) {
      currentValues.push(value);
    }
    url.searchParams.set(key, currentValues.join(","));
  }
  window.history.replaceState({}, "", url);
}

/*
 * Function to add a value to a query parameter.
 * @param {String} key - The query parameter key.
 * @param {String} value - The value to add.
 **/
export function removeValueFromQueryParams(key, value) {
  const url = new URL(window.location);
  let currentValues = url.searchParams.get(key)?.split(",") || [];
  currentValues = currentValues.filter((v) => v !== value);
  if (currentValues.length) {
    url.searchParams.set(key, currentValues.join(","));
  } else {
    url.searchParams.delete(key);
  }
  window.history.replaceState({}, "", url);
}

/**
 * Sanitizes a given input string by performing the following transformations:
 * 1. Trims leading and trailing whitespace.
 * 2. Converts all characters to lowercase.
 * 3. Replaces spaces with hyphens.
 * 4. Removes all characters that are not lowercase letters, digits, or hyphens.
 * 5. Removes leading and trailing hyphens.
 *
 * @param {string} input - The input string to sanitize.
 * @returns {string} - The sanitized string.
 */

export function sanitizeInput(input) {
  return input
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9-]/g, "")
    .replace(/^-+|-+$/g, "");
}

function attachLoadingSpinner(submitButton) {
  let spinnerClassName = "p-icon--spinner u-animation--spin";
  if (submitButton.classList.contains("p-button--positive")) {
    spinnerClassName += " is-light";
  }

  const spinnerIcon = document.createElement("i");
  spinnerIcon.className = spinnerClassName;
  const buttonRect = submitButton.getBoundingClientRect();
  submitButton.style.width = buttonRect.width + "px";
  submitButton.style.height = buttonRect.height + "px";
  submitButton.classList.add("is-processing");
  submitButton.disabled = true;
  submitButton.innerText = "";
  submitButton.appendChild(spinnerIcon);
}

document.querySelectorAll("form").forEach((form) => {
  form.addEventListener("submit", (event) => {
    const submitButtons = form.querySelectorAll("button[type='submit']");
    submitButtons?.forEach((submitButton) => {
      attachLoadingSpinner(submitButton);
    });
  });
});

/**
 * Function to debounce a function call.
 * @param {Function} func - The function to debounce.
 * @param {Number} delay - The delay in ms.
 **/
export function debounce(func, delay) {
  let timer;
  return function (...args) {
    const context = this;
    clearTimeout(timer);
    timer = setTimeout(() => func.apply(context, args), delay);
  };
}
