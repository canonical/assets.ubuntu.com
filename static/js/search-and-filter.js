/* 
 * Function that finds all the search and filter components on the page and
 * sets up the event listeners for opening the panel and handling the chips.
 * Also calls the specific setup functions for each type of search and filter component.
 **/
(function() {
  const patternMap = new Map();
  [].slice.call(document.querySelectorAll('.js-search-and-filter')).forEach(function(pattern) {
    const searchContainer = pattern.querySelector('.p-search-and-filter__search-container');
    const chipsContainer = pattern.querySelector('.p-filter-panel-section__chips');
    const targetPanel = pattern.querySelector('.p-search-and-filter__panel');
    const hiddenInput = pattern.querySelector('.js-hidden-input');
    // Here we ceate a map for each search and filter. This allow us to have only one document event listner.
    patternMap.set(pattern, {
      searchContainer,
      chipsContainer,
      targetPanel,
      hiddenInput,
      // This function checks if the target is in an active search component.
      isInActiveSearchComponent: (element, pattern) => {
        const isActive = pattern.classList.contains('js-active')
        return element.closest('.p-search-and-filter') === pattern && !isActive;
      }
    });
    // When you focus a specifc input, open the associated chips panel
    pattern.addEventListener('focusin', function(e) {
      openPanel(searchContainer, targetPanel, true);
    });
    // When you focus out of the input, close the chips panel.
    pattern.addEventListener('focusout', function(e) {
      if (patternMap.get(pattern).isInActiveSearchComponent(e.target, pattern)) {
        return;
      }
      openPanel(searchContainer, targetPanel, false);
    });
  });
  // Event delegation for clicks inside and outside the search and filter components.
  document.addEventListener('click', function(e) {
    patternMap.forEach((element, pattern) => {
      const { searchContainer, targetPanel, isInActiveSearchComponent, hiddenInput } = element;
      if (!isInActiveSearchComponent(e.target, pattern)) {
        openPanel(searchContainer, targetPanel, false);
        return;
      }
      const targetChip = e.target.closest('.js-chip');
      // If the click is on a chip, handle the selection
      if (targetChip) {
        e.preventDefault();
        if (targetChip.closest('.js-products')) {
          handleProductsChipSelection(targetChip, hiddenInput);
        } else if (targetChip.closest('.js-authors')) {
          handleAuthorsChipSelection(targetChip, searchContainer);
        }
      }
    });
  });
  // Each of the search and filters have different data sources and act slightly differently.
  // So we have to set up each one individually.
  setUpProductFilter();
  setUpOtherTagsFilter();
  setUpAuthorFilter();
})();

/* 
 * Generic function to show and hide the chips selection panel.
 * @param {HTMLElement} searchContainer - The whole pannel container.
 * @param {HTMLElement} panel - Where the chips are displayed.
 * @param {Boolean} isOpen - Whether the panel should end open or closed.
 **/
function openPanel(searchContainer, panel, isOpen) {
  if (typeof isOpen === 'undefined') {
    isOpen = panel.getAttribute('aria-hidden') === 'false';
  }
  if (panel && searchContainer) {
    if (!isOpen) {
      panel.setAttribute('aria-hidden', 'true');
      searchContainer.setAttribute('aria-expanded', 'false');
      panel.classList.remove('js-active');
    } else {
      panel.setAttribute('aria-hidden', 'false');
      searchContainer.setAttribute('aria-expanded', 'true');
      panel.classList.add('js-active');
    }
  }
}

/* 
 * Generic function to add the value of a selected chip, to the value of a hidden input.
 * We have to do this as the chips will not be submitted with the form.
 * @param {String} value - The value of the chip.
 * @param {HTMLElement} input - The hidden input to store the values.
 **/
function addChipValueToHiddenInput(value, input) {
  let selectedChips = input.value.split(',').filter(Boolean);
  if (!selectedChips.includes(value)) {
    selectedChips.push(value);
  }
  input.setAttribute('value', selectedChips.join(','));
}

/* 
 * Generic function to remove the value of a selected chip, from the value of a hidden input.
 * @param {String} value - The value of the chip.
 * @param {HTMLElement} input - The hidden input to store the values.
 **/
function removeChipValueFromHiddenInput(value, input) {
  let selectedChips = input.value.split(',').filter(Boolean);
  selectedChips = selectedChips.filter(id => id !== value);
  input.setAttribute('value', selectedChips.join(','));
}

/*
 * Specific setup for the products filter.
 * Products comes from a predefined list (products.yaml) and are added to the page on load.
 * By default they are all hidden and are shown and hidden based on the search input.
 **/
function setUpProductFilter() {
  const productsPanel = document.querySelector('.js-products');
  const fuse = setupFuse(productsPanel);
  handleProductInputChange(fuse, productsPanel.querySelector('.js-search-input'));
  // If we are on the /update route, the asset may have existing chips, we need to add them to the page.
  const existingChips = Array.from(productsPanel.querySelectorAll('.js-chip.is-inactive.u-hide'));
  existingChips.forEach(chip => handleProductsChipSelection(chip, productsPanel.querySelector('.js-hidden-input')));
}

/*
 * Setup fuse.js, as fuzzy search specfically for the products and return the instance.
 * @param {HTMLElement} productsPanel - The panel containing the products chips.
 **/
function setupFuse(productsPanel) {
  // Map the chips to an object with the name and id.
  const chipsObj = Array.from(productsPanel.querySelectorAll('.js-chip.is-inactive')).map(chip => ({
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
 **/
function handleProductInputChange(fuse, input) {
  input.addEventListener('input', () => {
    const query = document.querySelector('.js-search-input').value;
    const result = fuse.search(query);
    showAndHideProductChips(result.map(item => item.item), query);
  });
}

/*
 * Specfic setup for product chips. 
 * When a chip is selected, it hides the one the selection panel and shows the one in the input.
 * It adds/removes the selected chip to the hidden input.
 * Attaches a dismiss handler to the active chip.
 * @param {Array} chips - The chips to show.
 * @param {HTMLElement} hiddenInput - The hidden input to store the selected chips values.
 **/
function handleProductsChipSelection(chip, hiddenInput) {
  const activeChip = document.querySelector(`.js-${chip.id}.is-active`);
  activeChip.addEventListener('click', function dismissChip(e) {
    e.preventDefault();
    removeChipValueFromHiddenInput(chip.id, hiddenInput);
    document.querySelector(`#${chip.id}`).classList.remove('u-hide');
    this.classList.add('u-hide');
    this.removeEventListener('click', dismissChip, false);
  });
  addChipValueToHiddenInput(chip.id, hiddenInput);
  chip.classList.add('u-hide');
  activeChip.classList.remove('u-hide');
}

/*
 * Specfic handling for the product chips search results.
 * Starts by hiding all chips, then shows the ones that match the search query.
 * If there are no results, shows a message.
 * @param {Array} chips - The chips to show.
 * @param {String} query - The search query.
 **/
function showAndHideProductChips(chips, query) {
  const allChips = document.querySelectorAll('.js-chip.is-inactive');
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
  if (!chips.length) {
    // If there are no results, show a message
    document.querySelector('.js-no-results').classList.remove('u-hide');
  } else {
    // If there are results, show those chips
    document.querySelector('.js-no-results').classList.add('u-hide');
    chips.forEach(chip => {
      if (document.querySelector(`.js-${chip.id}.is-active`).classList.contains('u-hide')) {
        const chipElement = document.querySelector(`.js-${chip.id}.is-inactive`);
        chipElement.classList.remove('u-hide');
      }
    });
  }
}

/*
 * Sets up a query to the directory API to search for authors.
 * Calls the function that shows the search results
 **/
function setUpAuthorFilter() {
  const authorsInput = document.querySelector('.js-authors-input');
  authorsInput.addEventListener('input', debounce(async function() {
    const username = this.value;
    if (username.trim() !== "") {
      try {
        const response = await fetch(`/v1/get-users/${(username)}`, {
          method: 'GET',
        });
        if (response.ok) {
          const data = await response.json();
          addAndRemoveAuthorsChips(data);
        } else {
          console.log("No user found");
        }
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    }
  }, 300));
  // If in upload there may be an existing chips, handle them
  const existingChip = document.querySelector('.js-authors .js-chip');
  if (existingChip?.length) {
    handleAuthorsChipSelection(existingChip, document.querySelector('.js-authors .p-search-and-filter__search-container'));
  }
}

/*
 * Adds and removes the author chips to the search panel.
 * As this comes from an API call, we can not setupo the chips on load (like with products).
 * We have to create the chips on the fly. Limited to 10 results.
 * @param {Array} data - The data from the API call.
 **/
function addAndRemoveAuthorsChips(data) {
  const chipContainer = document.querySelector('.js-authors-chip-container');
  chipContainer.innerHTML = '';
  if (data.length === 0) {
    chipContainer.innerHTML = '<p><strong>No results found...</strong></p>';
  }
  const template = document.querySelector('#author-inactive-chip-template');
  const limitedData = data.slice(0, 10);
  limitedData.forEach(author => {
    const chipClone = template.content.cloneNode(true);
    const chip = chipClone.querySelector('.js-chip');
    chip.querySelector('.js-value').textContent = author.firstName + ' ' + author.surname;
    chip.setAttribute('data-email', author.email);
    chip.setAttribute('data-firstName', author.firstName);
    chip.setAttribute('data-lastName', author.surname);
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
function handleAuthorsChipSelection(chip, activeChipContainer) {
  const template = document.querySelector('#author-active-chip-template');
  // Clone the chip template
  const activeChip = template.content.cloneNode(true);
  // Remove the cuurent active chip as we only want one at a time
  activeChipContainer.querySelector('.js-chip')?.remove();
  activeChip.querySelector('.js-value').textContent = chip.dataset.firstname + ' ' + chip.dataset.lastname;
  activeChip.querySelector('.js-chip').addEventListener('click', function dismissChip(e) {
    e.preventDefault();
    // Reset the three hidden inputs, firstname, lastname and email
    removeChipValueFromHiddenInput(chip.dataset.email, activeChipContainer.querySelector('.js-hidden-input-email'));
    removeChipValueFromHiddenInput(chip.dataset.firstname, activeChipContainer.querySelector('.js-hidden-input-firstname'));
    removeChipValueFromHiddenInput(chip.dataset.lastname, activeChipContainer.querySelector('.js-hidden-input-lastname'));
    this.remove();
  });
  // Add the chip values to the three hidden inputs, firstname, lastname and email
  addChipValueToHiddenInput(chip.dataset.email, activeChipContainer.querySelector('.js-hidden-input-email'));
  addChipValueToHiddenInput(chip.dataset.firstname, activeChipContainer.querySelector('.js-hidden-input-firstname'));
  addChipValueToHiddenInput(chip.dataset.lastname, activeChipContainer.querySelector('.js-hidden-input-lastname'));
  activeChipContainer.prepend(activeChip);
}

/*
 * Specific setup for the other tags filter.
 * We don't want to use the search here, but still want to add/remove chips.
 **/ 
function setUpOtherTagsFilter() {
  const panel = document.querySelector('.js-other-tags');
  const input = panel.querySelector('.js-input');
  const hiddenInput = panel.querySelector('.js-hidden-input');
  const container = panel.querySelector('.js-container');
  const template = document.querySelector('#other-tag-chip-template');
  const existingChips = Array.from(container.querySelectorAll('.js-chip'));
  handleExisitngOtherTagsChips(existingChips, hiddenInput);
  // On 'enter' click, add the chip to the select panel.
  input.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      const tagClone = template.content.cloneNode(true);
      tagClone.querySelector('.js-value').textContent = input.value;
      attachDismissOtherTagChip(tagClone.querySelector('.js-chip'), hiddenInput);
      container.prepend(tagClone);
      // Update the hidden input value
      addChipValueToHiddenInput(input.value, hiddenInput);
      // Reset the input value
      input.value = '';
    }
  });
}

/*
 * Attach the dismiss handler for other tags chip.
 **/
function attachDismissOtherTagChip(target, hiddenInput) {
  target.addEventListener('click', function dismissChip(e) {
    e.preventDefault();
    const value = this.querySelector('.js-value').textContent;
    removeChipValueFromHiddenInput(value, hiddenInput);
    this.remove();
  });
}

/* 
 * When editing a asset, check if it had existing other tags and handle them.
 **/
function handleExisitngOtherTagsChips(chips, hiddenInput) {
  if (chips.length) {
    chips.forEach(chip => {
      attachDismissOtherTagChip(chip, hiddenInput);
      addChipValueToHiddenInput(chip.dataset.value, hiddenInput)
    });
  }
}

/* 
 * Function to debounce a function call.
 * @param {Function} func - The function to debounce.
 * @param {Number} delay - The delay in ms.
 **/
function debounce(func, delay) {
  let timer;
  return function (...args) {
    const context = this;
    clearTimeout(timer);
    timer = setTimeout(() => func.apply(context, args), delay);
  };
}

/*
 * Function to handle multiselects as they were not submitting all the selected values.
 **/
document.querySelector('#create-update-asset').addEventListener('submit', function(e) {
  e.preventDefault();
  const multiSelects = document.querySelectorAll('.js-multiselect');
  multiSelects.forEach(select => {
    const selectedOptions = Array.from(select.selectedOptions).map(option => option.value);
    document.querySelector(`.js-${select.id}-hidden`).value = selectedOptions.join(',');
  });
  this.submit();
});