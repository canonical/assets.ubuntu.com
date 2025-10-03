import {
  openPanel,
  addValueToHiddenInput,
  removeValueFromHiddenInput,
  addValueToQueryParams,
  removeValueFromQueryParams,
  debounce,
  closePanels,
} from "./main.js";

// Define whether we are in search and thus need to update query params
const updateQueryParams = document.querySelector(".js-asset-search");

/*
 * Sets up the event listeners for opening the panel.
 * Also calls the specific setup function.
 **/
(function () {
  const authorsSearchComponent = document.querySelector(".js-authors-search");
  if (authorsSearchComponent) {
    const authorsSearchInput =
      authorsSearchComponent.querySelector(".js-authors-input");
    if (authorsSearchInput) {
      authorsSearchInput.addEventListener("input", function (e) {
        const shouldOpen = e.target.value.trim().length > 0;
        openPanel(authorsSearchComponent, shouldOpen);
      });
      authorsSearchInput.addEventListener("focus", function () {
        closePanels([".js-products-search", ".js-campaign-search"]);
      });
      setUpAuthorSearchField();
    }
  }
})();

/*
 * Sets up a query to the directory API to search for authors.
 * Calls the function that shows the search results
 **/
function setUpAuthorSearchField() {
  const authorsInput = document.querySelector(".js-authors-input");
  authorsInput.addEventListener(
    "input",
    debounce(async function () {
      const username = this.value;
      if (username.trim() !== "") {
        try {
          const response = await fetch(`/v1/get-users/${username}`, {
            method: "GET",
          });
          if (response.ok) {
            const data = await response.json();
            updateSearchResults(data);
          }
        } catch (error) {
          console.error("Error fetching user data:", error);
        }
      } else {
        updateSearchResults([]);
      }
    }, 300)
  );
}

/*
 * Function that handles the click event on a product chip.
 * It checks if the chip is selected or unselected and calls the specific function.
 * @param {HTMLElement} targetChip - The chip that was clicked.
 **/
export default function handleAuthorsChip(targetChip) {
  const selectedAuthorChip = document.querySelector(".js-author-chip");
  if (targetChip.classList.contains("js-unselected")) {
    selectAuthorChip(targetChip, selectedAuthorChip);
  } else {
    deselectAuthorChip(targetChip);
  }
}

/*
 * Adds and removes the author chips to the search panel.
 * As this comes from an API call, we can not setup the chips on load (like with products).
 * We have to create the chips on the fly. Limited to 10 results.
 * @param {Array} data - The data from the API call.
 **/
function updateSearchResults(data) {
  const chipContainer = document.querySelector(".js-authors-chip-container");
  chipContainer.innerHTML = "";
  if (data.length === 0) {
    chipContainer.innerHTML = "<p><strong>No results found...</strong></p>";
  }
  const template = document.querySelector("#author-unselected-chip-template");
  const limitedData = data.slice(0, 10);
  limitedData.forEach((author) => {
    const chipClone = template.content.cloneNode(true);
    const chip = chipClone.querySelector(".p-chip.js-unselected");
    chip.querySelector(".js-content").textContent =
      author.firstName + " " + author.surname;
    chip.setAttribute("data-email", author.email);
    chip.setAttribute("data-firstName", author.firstName);
    chip.setAttribute("data-lastName", author.surname);
    chipContainer.appendChild(chip);
  });
}

/*
 * When a chip is selected, it adds the chip to the search panel.
 * It also adds the chip value to three hidden inputs, as we have to pass the email, firstname and lastname.
 * Attaches a dismiss handler to the active chip. Limited to 1 selected chip.
 * @param {HTMLElement} chip - The chip to select.
 * @param {HTMLElement} activeChipContainer - The container to add the active chip.
 **/
function selectAuthorChip(chip, selectedAuthorChip) {
  selectedAuthorChip.classList.remove("u-hide");
  selectedAuthorChip.querySelector(".js-content").textContent =
    chip.dataset.firstname + " " + chip.dataset.lastname;
  selectedAuthorChip.setAttribute("data-email", chip.dataset.email);
  selectedAuthorChip.setAttribute("data-firstname", chip.dataset.firstname);
  selectedAuthorChip.setAttribute("data-lastname", chip.dataset.lastname);
  addValueToHiddenInput(
    chip.dataset.email,
    document.querySelector(".js-hidden-field-email"),
    (replace = true)
  );
  addValueToHiddenInput(
    chip.dataset.firstname,
    document.querySelector(".js-hidden-field-firstname"),
    (replace = true)
  );
  addValueToHiddenInput(
    chip.dataset.lastname,
    document.querySelector(".js-hidden-field-lastname"),
    (replace = true)
  );
  // clear the entered value after selecting a chip
  const inputField = document.querySelector(
    ".js-authors-search .js-authors-input"
  );
  inputField.value = "";
  // close the chips panel
  const chipsPanel = document.querySelector(
    ".js-authors-search .js-chips-panel"
  );
  chipsPanel.setAttribute("aria-hidden", "true");
  if (updateQueryParams) {
    addValueToQueryParams("author_email", chip.dataset.email, (replace = true));
    addValueToQueryParams(
      "author_firstname",
      chip.dataset.firstname,
      (replace = true)
    );
    addValueToQueryParams(
      "author_lastname",
      chip.dataset.lastname,
      (replace = true)
    );
  }
}

function deselectAuthorChip(chip) {
  chip.classList.add("u-hide");
  removeValueFromHiddenInput(
    chip.dataset.email,
    document.querySelector(".js-hidden-field-email")
  );
  removeValueFromHiddenInput(
    chip.dataset.firstname,
    document.querySelector(".js-hidden-field-firstname")
  );
  removeValueFromHiddenInput(
    chip.dataset.lastname,
    document.querySelector(".js-hidden-field-lastname")
  );
  if (updateQueryParams) {
    removeValueFromQueryParams("author_email", chip.dataset.email);
    removeValueFromQueryParams("author_firstname", chip.dataset.firstname);
    removeValueFromQueryParams("author_lastname", chip.dataset.lastname);
  }
  chip.removeAttribute("data-email", chip.dataset.email);
  chip.removeAttribute("data-firstname", chip.dataset.firstname);
  chip.removeAttribute("data-lastname", chip.dataset.lastname);
}
