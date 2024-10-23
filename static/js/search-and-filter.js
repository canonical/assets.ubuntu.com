// Setup the search and filter patterns
(function() {
  const patternMap = new Map();
  [].slice.call(document.querySelectorAll('.js-search-and-filter')).forEach(function(pattern) {
    const searchContainer = pattern.querySelector('.p-search-and-filter__search-container');
    const chipsContainer = pattern.querySelector('.p-filter-panel-section__chips');
    const targetPanel = pattern.querySelector('.p-search-and-filter__panel');
    const hiddenInput = pattern.querySelector('.js-hidden-input');
    patternMap.set(pattern, {
      searchContainer,
      chipsContainer,
      targetPanel,
      hiddenInput,
      isInSearchActiveComponent: (element, pattern) => {
        const isActive = pattern.classList.contains('js-active')
        return element.closest('.p-search-and-filter') === pattern && !isActive;
      }
    });
    pattern.addEventListener('focusin', function(e) {
      openPanel(searchContainer, targetPanel, true);
    });
    pattern.addEventListener('focusout', function(e) {
      if (patternMap.get(pattern).isInSearchActiveComponent(e.target, pattern)) {
        return;
      }
      openPanel(searchContainer, targetPanel, false);
    });
  });
  document.addEventListener('click', function(e) {
    patternMap.forEach((element, pattern) => {
      const { searchContainer, targetPanel, isInSearchActiveComponent, hiddenInput } = element;
      if (!isInSearchActiveComponent(e.target, pattern)) {
        openPanel(searchContainer, targetPanel, false);
        return;
      }
      const targetChip = e.target.closest('.js-chip');
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
  setUpProductFilter();
  setUpOtherTagsFilter();
  setUpAuthorFilter();
})();

// Generic function to show and hide the cips selection panel
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

// Generic function to add chip value from hidden input
function addChipValueToHiddenInput(value, input) {
  let selectedChips = input.value.split(',').filter(Boolean);
  if (!selectedChips.includes(value)) {
    selectedChips.push(value);
  }
  input.setAttribute('value', selectedChips.join(','));
}

// Generic function to remove chip value from hidden input
function removeChipValueFromHiddenInput(value, input) {
  let selectedChips = input.value.split(',').filter(Boolean);
  selectedChips = selectedChips.filter(id => id !== value);
  input.setAttribute('value', selectedChips.join(','));
}

// Product specific setup
function setUpProductFilter() {
  const productsPanel = document.querySelector('.js-products');
  const fuse = setupFuse(productsPanel);
  handleInputChange(fuse, productsPanel.querySelector('.js-search-input'));
  // If there are existing chips, because you are updating, handle them
  const existingChips = Array.from(productsPanel.querySelectorAll('.js-chip.is-inactive.u-hide'));
  existingChips.forEach(chip => handleProductsChipSelection(chip, productsPanel.querySelector('.js-hidden-input')));
}

// Setup for fuse.js, specific to products
function setupFuse(productsPanel) {
  const chipsObj = Array.from(productsPanel.querySelectorAll('.js-chip.is-inactive')).map(chip => ({
    name: chip.dataset.name,
    id: chip.id

  }));
  const input = productsPanel.querySelector('.js-search-input');
  const options = {
    keys: ['name'],
    threshold: 0.3
  };
  const fuse = new Fuse(chipsObj, options);
  return fuse;
}

// Function to handle input change for products
function handleInputChange(fuse, input) {
  input.addEventListener('input', () => {
    const query = document.querySelector('.js-search-input').value;
    const result = fuse.search(query);
    showAndHideProductChips(result.map(item => item.item), query);
  });
}

// Product specific handling for clicking chips
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

// Product specific handling for showing the results from fuse
function showAndHideProductChips(chips, query) {
  const allChips = document.querySelectorAll('.js-chip.is-inactive');
  if (!query) {
    allChips.forEach(chip => {
      chip.classList.remove('u-hide');
    });
  }
  allChips.forEach(chip => {
    chip.classList.add('u-hide');
  });
  if (!chips.length) {
    document.querySelector('.js-no-results').classList.remove('u-hide');
  } else {
    document.querySelector('.js-no-results').classList.add('u-hide');
    chips.forEach(chip => {
      if (document.querySelector(`.js-${chip.id}.is-active`).classList.contains('u-hide')) {
        const chipElement = document.querySelector(`.js-${chip.id}.is-inactive`);
        chipElement.classList.remove('u-hide');
      }
    });
  }
}

// Author specific setup
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

// Author specfic handling for chips selection dropdown
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

// Author specfic handling clicking author chip
function handleAuthorsChipSelection(chip, chipContainer) {
  const template = document.querySelector('#author-active-chip-template');
  const activeChip = template.content.cloneNode(true);
  chipContainer.querySelector('.js-chip')?.remove();
  activeChip.querySelector('.js-value').textContent = chip.dataset.firstname + ' ' + chip.dataset.lastname;
  activeChip.querySelector('.js-chip').addEventListener('click', function dismissChip(e) {
    e.preventDefault();
    removeChipValueFromHiddenInput(chip.dataset.email, chipContainer.querySelector('.js-hidden-input-email'));
    removeChipValueFromHiddenInput(chip.dataset.firstname, chipContainer.querySelector('.js-hidden-input-firstname'));
    removeChipValueFromHiddenInput(chip.dataset.lastname, chipContainer.querySelector('.js-hidden-input-lastname'));
    this.remove();
  });
  addChipValueToHiddenInput(chip.dataset.email, chipContainer.querySelector('.js-hidden-input-email'));
  addChipValueToHiddenInput(chip.dataset.firstname, chipContainer.querySelector('.js-hidden-input-firstname'));
  addChipValueToHiddenInput(chip.dataset.lastname, chipContainer.querySelector('.js-hidden-input-lastname'));
  chipContainer.prepend(activeChip);
}

// Other tags specific setup
function setUpOtherTagsFilter() {
  const panel = document.querySelector('.js-other-tags');
  const input = panel.querySelector('.js-input');
  const hiddenInput = panel.querySelector('.js-hidden-input');
  const container = panel.querySelector('.js-container');
  const template = document.querySelector('#other-tag-chip-template');
  const existingChips = Array.from(container.querySelectorAll('.js-chip'));
  handleExisitngOtherTagsChips(existingChips, hiddenInput);
  input.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      const tagClone = template.content.cloneNode(true);
      tagClone.querySelector('.js-value').textContent = input.value;
      attachDismissChipHandler(tagClone.querySelector('.js-chip'), hiddenInput);
      container.prepend(tagClone);
      addChipValueToHiddenInput(input.value, hiddenInput);
      input.value = '';
    }
  });
}

// Dissmiss other tags chip handler
function attachDismissChipHandler(target, hiddenInput) {
  target.addEventListener('click', function dismissChip(e) {
    e.preventDefault();
    const value = this.querySelector('.js-value').textContent;
    removeChipValueFromHiddenInput(value, hiddenInput);
    this.remove();
  });
}

// Handle exising chips
function handleExisitngOtherTagsChips(chips, hiddenInput) {
  if (chips.length) {
    chips.forEach(chip => {
      attachDismissChipHandler(chip, hiddenInput);
      addChipValueToHiddenInput(chip.dataset.value, hiddenInput)
    });
  }
}
// Debounce for directory api call
function debounce(func, delay) {
  let timer;
  return function (...args) {
    const context = this;
    clearTimeout(timer);
    timer = setTimeout(() => func.apply(context, args), delay);
  };
}

// Presubmit actions
document.querySelector('#create-update-asset').addEventListener('submit', function(e) {
  e.preventDefault();
  const multiSelects = document.querySelectorAll('.js-multiselect');
  multiSelects.forEach(select => {
    const selectedOptions = Array.from(select.selectedOptions).map(option => option.value);
    document.querySelector(`.js-${select.id}-hidden`).value = selectedOptions.join(',');
  });
  this.submit();
});