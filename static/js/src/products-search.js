import Fuse from 'fuse.js';
import {
  openPanel,
  addValueToHiddenInput,
  removeValueFromHiddenInput,
  addValueToQueryParams,
  removeValueFromQueryParams,
} from './main.js';

// Define whether we are in search and thus need to update query params
const updateQueryParams = document.querySelector('.js-asset-search');

/* 
 * Sets up the event listeners for opening the panel.
 * Also calls the specific setup function.
 **/
(function () {
  const productsSearchComponent = document.querySelector('.js-products-search');
  if (productsSearchComponent) {
    productsSearchComponent.addEventListener('focusin', function (e) {
      openPanel(productsSearchComponent, true, "focusin");
    });
    productsSearchComponent.addEventListener('focusout', function (e) {
      if (!e.relatedTarget) {
        return;
      }
      openPanel(productsSearchComponent, false, "focusout");
    });
    setUpProductSearchField();
  }
})();

/*
 * Function that handles the click event on a product chip.
 * It checks if the chip is selected or unselected and calls the specific function.
 * @param {HTMLElement} targetChip - The chip that was clicked.
 **/
export default function handleProductsChip(targetChip) {
  if (targetChip.classList.contains('js-unselected')) {
    selectProductsChip(targetChip.id);
  } else if (targetChip.classList.contains('js-selected')) {
    deselectProductsChip(targetChip.dataset.id);
  }
}

/*
 * Specific setup for the products filter.
 * Products comes from a predefined list (products.yaml) and are added to the page on load.
 * By default they are all hidden and are shown and hidden based on the search input.
 **/
function setUpProductSearchField() {
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
  existingChips.forEach(chip => selectProductsChip(chip.id));
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
function selectProductsChip(chipId) {
  const unselectedChip = document.querySelector(`.js-${chipId}-chip.js-unselected`);
  const selectedChip = document.querySelector(`.js-${chipId}-chip.js-selected`);
  unselectedChip.classList.add('u-hide');
  selectedChip.classList.remove('u-hide');
  addValueToHiddenInput(chipId, document.querySelector('.js-products-search .js-hidden-field'));
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
function deselectProductsChip(chipId) {
  const unselectedChip = document.querySelector(`.js-${chipId}-chip.js-unselected`);
  const selectedChip = document.querySelector(`.js-${chipId}-chip.js-selected`);
  unselectedChip.classList.remove('u-hide');
  selectedChip.classList.add('u-hide');
  removeValueFromHiddenInput(chipId, document.querySelector('.js-products-search .js-hidden-field'));
  if (updateQueryParams) {
    removeValueFromQueryParams('product_types', chipId);
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