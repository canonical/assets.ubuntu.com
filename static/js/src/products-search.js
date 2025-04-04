import Fuse from "fuse.js";
import {
  openPanel,
  addValueToHiddenInput,
  removeValueFromHiddenInput,
  addValueToQueryParams,
  removeValueFromQueryParams,
  sanitizeInput,
} from "./main.js";

// Define whether we are in search and thus need to update query params
const updateQueryParams = document.querySelector(".js-asset-search");

/*
 * Sets up the event listeners for opening the panel.
 * Also calls the specific setup function.
 **/
(function () {
  const productsSearchComponent = document.querySelector(".js-products-search");
  if (productsSearchComponent) {
    const productSearchInput = productsSearchComponent.querySelector(".js-search-input");
    if (productSearchInput) {
      // only open the options panel if there is a value in the input
      productSearchInput.addEventListener("input", function (e) {
        const shouldOpen = e.target.value.trim().length > 0;
        openPanel(productsSearchComponent, shouldOpen);
      });
      setUpProductSearchField();
    }
  }
})();

/*
 * Function that handles the click event on a product chip.
 * It checks if the chip is selected or unselected and calls the specific function.
 * @param {HTMLElement} targetChip - The chip that was clicked.
 **/
export default function handleProductsChip(targetChip) {
  if (targetChip.classList.contains("js-unselected")) {
    selectProductsChip(targetChip.id);
  } else if (targetChip.classList.contains("js-selected")) {
    deselectProductsChip(targetChip.dataset.id);
  }
}

/*
 * Specific setup for the products filter.
 * Products comes from a predefined list (products.yaml) and are added to the page on load.
 * By default they are all hidden and are shown and hidden based on the search input.
 **/
function setUpProductSearchField() {
  const productsPanel = document.querySelector(".js-products-search");
  handleExistingChips(productsPanel);
  const Fuse = setupFuse(productsPanel);
  setupInputChangeListener(
    Fuse,
    productsPanel.querySelector(".js-search-input")
  );
}

/*
 *
 */
function handleExistingChips(productsPanel) {
  const existingChips = Array.from(
    productsPanel.querySelectorAll(".p-chip.js-unselected.u-hide")
  );
  existingChips.forEach((chip) => selectProductsChip(chip.id));
}
/*
 * Setup fuse.js, as fuzzy search specfically for the products and return the instance.
 * @param {HTMLElement} productsPanel -   The panel containing the products chips.
 **/
function setupFuse(productsPanel) {
  // Map the chips to an object with the name and id.
  const chipsObj = Array.from(
    productsPanel.querySelectorAll(".p-chip.js-unselected")
  ).map((chip) => ({
    name: chip.dataset.name,
    id: chip.id,
  }));
  const options = {
    keys: ["name"],
    threshold: 0.3,
  };
  const fuse = new Fuse(chipsObj, options);
  return fuse;
}

/*
 * Specfic handling for the product search input.
 * It calls the fuse.js instance and shows/hides the results.
 * @param {Fuse} fuse - The fuse.js instance.
 * @param {HTMLElement} input - The search input.
 **/
function setupInputChangeListener(fuse, input) {
  input.addEventListener("input", () => {
    const query = document.querySelector(".js-search-input").value;
    const result = fuse.search(query);
    showAndHideProductChips(
      result.map((item) => item.item),
      query
    );
  });
}

/*
 * When a chip is selected, it hides the one in the selection panel and shows the one in the input.
 * It adds/removes the selected chip value to/from the hidden input.
 * @param {Array} chip - The chip to show.
 * @param {HTMLElement} hiddenInput - The hidden input to store the selected chips value.
 **/
function selectProductsChip(chipId) {
  const unselectedChip = document.querySelector(
    `.js-${chipId}-chip.js-unselected`
  );
  const selectedChip = document.querySelector(`.js-${chipId}-chip.js-selected`);
  unselectedChip.classList.add("u-hide");
  selectedChip.classList.remove("u-hide");
  addValueToHiddenInput(
    chipId,
    document.querySelector(".js-products-search .js-hidden-field")
  );
  // clear the entered value after selecting a chip
  const inputField = document.querySelector(".js-products-search .js-search-input");
  inputField.value = "";
  inputField.focus();
  // close the chips panel
  const chipsPanel = document.querySelector(".js-products-search .js-chips-panel");
  chipsPanel.setAttribute("aria-hidden", "true");
  if (updateQueryParams) {
    addValueToQueryParams("product_types", chipId);
  }
}

/*
 * When a chip is deselected, it shows the one in the selection panel and hides the one in the input.
 * It adds/removes the selected chip value to/from the hidden input.
 * We have to use dataset to avoid duplicate IDs.
 * @param {Array} chip - The chip to show.
 * @param {HTMLElement} hiddenInput - The hidden input to remove the selected chips value from.
 **/
function deselectProductsChip(chipId) {
  const unselectedChip = document.querySelector(
    `.js-${chipId}-chip.js-unselected`
  );
  const selectedChip = document.querySelector(`.js-${chipId}-chip.js-selected`);
  unselectedChip.classList.remove("u-hide");
  selectedChip.classList.add("u-hide");
  removeValueFromHiddenInput(
    chipId,
    document.querySelector(".js-products-search .js-hidden-field")
  );
  if (updateQueryParams) {
    removeValueFromQueryParams("product_types", chipId);
  }
}

/*
 * Specfic handling for the product chips search results.
 * Starts by hiding all chips, then shows the ones that match the search query.
 * If there are no results, shows a message.
 * @param {Array} chips - The chips to show.
 * @param {String} query - The search query.
 **/
function showAndHideProductChips(chips, query) {
  const allChips = document.querySelectorAll(".p-chip.js-unselected");
  // If no query, show all chips
  if (!query) {
    allChips.forEach((chip) => {
      chip.classList.remove("u-hide");
    });
    return;
  }
  // Start by hiding all chips
  allChips.forEach((chip) => {
    chip.classList.add("u-hide");
  });
  if (chips.length > 0) {
    document.querySelector(".js-no-results").classList.add("u-hide");
    chips.forEach((chip) => {
      if (
        document
          .querySelector(`.js-${chip.id}-chip.js-selected`)
          .classList.contains("u-hide")
      ) {
        const chipElement = document.querySelector(
          `.js-${chip.id}-chip.js-unselected`
        );
        chipElement.classList.remove("u-hide");
      }
    });
  } else {
    document.querySelector(".js-no-results").classList.remove("u-hide");
  }
}

/**
 * Attaches an event listener to an input element to create chips when the Enter key is pressed.
 *
 * @param {HTMLInputElement} input - The input element to attach the event listener to.
 */
function chips_in_input(input) {
  const parent_chips_container = input.closest(".add-and-edit-chips");
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      const value = sanitizeInput(input.value);
      if (value) {
        createChip(value, parent_chips_container);
        input.value = ""; // Clear input field
      }
    }
  });
}

/**
 * Creates a chip element with the given value and appends it to the parent chips container.
 * If the value is not already present in the hidden input field, it adds the chip.
 * The chip includes a dismiss button to remove the chip and update the hidden input field.
 *
 * @param {string} value - The value to be displayed in the chip.
 * @param {HTMLElement} parent_chips_container - The container element where the chip will be added.
 */

function createChip(value, parent_chips_container) {
  input_field = parent_chips_container.querySelector(".js-hidden-field");
  added_chips_container = parent_chips_container.querySelector(".added-chips");
  selectedChips = input_field.value.split(",").filter(Boolean);
  if (!selectedChips.includes(value)) {
    const chip = document.createElement("span");
    chip.classList.add("p-chip");

    const chipValue = document.createElement("span");
    chipValue.classList.add("p-chip__value");
    chipValue.textContent = value;

    const dismissButton = document.createElement("button");
    dismissButton.classList.add("p-chip__dismiss");
    dismissButton.textContent = "Dismiss";
    dismissButton.addEventListener("click", () => {
      removeValueFromHiddenInput(value, input_field);
      chip.remove();
    });
    chip.appendChild(chipValue);
    chip.appendChild(dismissButton);
    added_chips_container.appendChild(chip);
  }
  addValueToHiddenInput(value, input_field, (replace = false));
}

/**
 * Handles existing chips in the input field by finding hidden chips and creating visible chips from them.
 *
 * @param {HTMLInputElement} input - The input element where chips are being managed.
 */
function handleExistingChips_in_input(input) {
  const parent_chips_container = input.closest(".add-and-edit-chips");
  console.log(parent_chips_container);
  const existing_chips = Array.from(
    parent_chips_container.querySelectorAll(".added-chips .u-hide")
  );
  existing_chips.forEach((chip) =>
    createChip(chip.textContent, parent_chips_container)
  );
}

handleExistingChips_in_input(document.getElementById("assets-chips-input"));
chips_in_input(document.getElementById("assets-chips-input"));
