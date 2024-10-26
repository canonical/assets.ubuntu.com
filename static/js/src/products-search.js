import Fuse from 'fuse.js';
import {
  openPanel,
  addValueToHiddenInput,
  removeValueFromHiddenInput,
  isInActiveSearchComponent
} from './main.js';

/* 
 * Function that finds all the search and filter components on the page and
 * sets up the event listeners for opening the panel and handling the chips.
 * Also calls the specific setup functions for each type of search and filter component.
 **/
(function () {
  const productsSearch = document.querySelector('.js-products-search');
  productsSearch.addEventListener('focusin', function (e) {
    if (!isInActiveSearchComponent(e.target, productsSearch)) {
      openPanel(productsSearch, true);
      return;
    }
  });
  productsSearch.addEventListener('focusout', function (e) {
    if (isInActiveSearchComponent(e.target, productsSearch)) {
      return;
    }
    openPanel(productsSearch, false);
  });
  setUpProductFilter();
})();

/*
 * Function that handles the click event on a product chip.
 * It checks if the chip is selected or unselected and calls the specific function.
 * @param {HTMLElement} targetChip - The chip that was clicked.
 **/
export default function handleProductsChip(targetChip) {
  const updateQueryParams = document.querySelector('.js-asset-search');
  if (targetChip.classList.contains('js-unselected')) {
    selectChip(targetChip.id, updateQueryParams);
  } else if (targetChip.classList.contains('js-selected')) {
    deselectChip(targetChip.dataset.id, updateQueryParams);
  }
}

/*
 * Specific setup for the products filter.
 * Products comes from a predefined list (products.yaml) and are added to the page on load.
 * By default they are all hidden and are shown and hidden based on the search input.
 **/
function setUpProductFilter() {
  const productsPanel = document.querySelector('.js-products-search');
  handleExistingChips(productsPanel);
  const Fuse = setupFuse(productsPanel);
  setupInputChangeListener(Fuse, productsPanel.querySelector('.js-search-input'));
}

/*
 *
 */
function handleExistingChips(productsPanel) {
  const existingChips = Array.from(productsPanel.querySelectorAll('.p-chip.js-unselected.u-hide'));
  const updateQueryParams = document.querySelector('.js-asset-search');
  existingChips.forEach(chip => selectChip(chip.id, updateQueryParams));
}
/*
 * Setup fuse.js, as fuzzy search specfically for the products and return the instance.
 * @param {HTMLElement} productsPanel -   The panel containing the products chips.
 **/
function setupFuse(productsPanel) {
  // Map the chips to an object with the name and id.
  const chipsObj = Array.from(productsPanel.querySelectorAll('.p-chip.js-unselected')).map(chip => ({
    name: chip.dataset.name,
    id: chip.id
  }));
  const options = {
    keys: ['name'],
    threshold: 0.3
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
  input.addEventListener('input', () => {
    const query = document.querySelector('.js-search-input').value;
    const result = fuse.search(query);
    showAndHideProductChips(result.map(item => item.item), query);
  });
}

/*
 * When a chip is selected, it hides the one in the selection panel and shows the one in the input.
 * It adds/removes the selected chip value to/from the hidden input.
 * @param {Array} chip - The chip to show.
 * @param {HTMLElement} hiddenInput - The hidden input to store the selected chips value.
 **/
function selectChip(chipId, updateQueryParams) {
  const unselectedChip = document.querySelector(`.js-${chipId}-chip.js-unselected`);
  const selectedChip = document.querySelector(`.js-${chipId}-chip.js-selected`);
  unselectedChip.classList.add('u-hide');
  selectedChip.classList.remove('u-hide');
  addValueToHiddenInput(chipId, document.querySelector('.js-products-search .js-hidden-input'));
  if (updateQueryParams) {
    addValueToQueryParams('product_types', chipId);
  }

}

/*
 * When a chip is deselected, it shows the one in the selection panel and hides the one in the input.
 * It adds/removes the selected chip value to/from the hidden input.
 * We have to use dataset to avoid duplicate IDs.
 * @param {Array} chip - The chip to show.
 * @param {HTMLElement} hiddenInput - The hidden input to remove the selected chips value from.
 **/
function deselectChip(chipId, updateQueryParams) {
  const unselectedChip = document.querySelector(`.js-${chipId}-chip.js-unselected`);
  const selectedChip = document.querySelector(`.js-${chipId}-chip.js-selected`);
  unselectedChip.classList.remove('u-hide');
  selectedChip.classList.add('u-hide');
  removeValueFromHiddenInput(chipId, document.querySelector('.js-products-search .js-hidden-input'));
  if (updateQueryParams) {
    removeValueFromQueryParams('product_types', chipId);
  }
}

/* 
 * Function to add a value to a query parameter.
 * @param {String} key - The query parameter key.
 * @param {String} value - The value to add.
 **/
function addValueToQueryParams(key, value) {
  const url = new URL(window.location);
  const currentValues = url.searchParams.get(key)?.split(',') || [];
  if (!currentValues.includes(value)) {
    currentValues.push(value);
  }
  url.searchParams.set(key, currentValues.join(','));
  window.history.replaceState({}, '', url);
}

/* 
 * Function to add a value to a query parameter.
 * @param {String} key - The query parameter key.
 * @param {String} value - The value to add.
 **/
function removeValueFromQueryParams(key, value) {
  const url = new URL(window.location);
  let currentValues = url.searchParams.get(key)?.split(',') || [];
  currentValues = currentValues.filter((v) => v !== value);
  if (currentValues.length) {
    url.searchParams.set(key, currentValues.join(','));
  } else {
    url.searchParams.delete(key);
  }
  window.history.replaceState({}, '', url);
}

/*
 * Specfic handling for the product chips search results.
 * Starts by hiding all chips, then shows the ones that match the search query.
 * If there are no results, shows a message.
 * @param {Array} chips - The chips to show.
 * @param {String} query - The search query.
 **/
function showAndHideProductChips(chips, query) {
  const allChips = document.querySelectorAll('.p-chip.js-unselected');
  // If no query, show all chips
  if (!query) {
    allChips.forEach(chip => {
      chip.classList.remove('u-hide');
    });
    return;
  }
  // Start by hiding all chips
  allChips.forEach(chip => {
    chip.classList.add('u-hide');
  });
  if (chips.length > 0) {
    document.querySelector('.js-no-results').classList.add('u-hide');
    chips.forEach(chip => {
      if (document.querySelector(`.js-${chip.id}-chip.js-selected`).classList.contains('u-hide')) {
        const chipElement = document.querySelector(`.js-${chip.id}-chip.js-unselected`);
        chipElement.classList.remove('u-hide');
      }
    });
  } else {
    document.querySelector('.js-no-results').classList.remove('u-hide');
  }
}