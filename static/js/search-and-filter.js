function togglePanel(searchContainer, panel, collapse) {
  if (typeof collapse === 'undefined') {
    collapse = panel.getAttribute('aria-hidden') !== 'false';
  }
  if (panel && searchContainer) {
    if (collapse) {
      panel.setAttribute('aria-hidden', 'true');
      searchContainer.setAttribute('aria-expanded', 'false');
    } else {
      panel.setAttribute('aria-hidden', 'false');
      searchContainer.setAttribute('aria-expanded', 'true');
    }
  }
}

function updateInputValue(input, chipId, action) {
  // Updates the value of the hidden input field with the selected chips
  let selectedChips = input.value.split(',').filter(Boolean);
  if (action === 'add' && !selectedChips.includes(chipId)) {
    selectedChips.push(chipId);
  } else if (action === 'remove') {
    selectedChips = selectedChips.filter(id => id !== chipId);
  }
  input.setAttribute('value', selectedChips.join(','));
}

function handleChipClick(chip, input) {
  console.log("chip", chip);
  const activeChip = document.querySelector(`#${chip.id}-selected`);
  activeChip.addEventListener('click', function dismissChip(e) {
    e.preventDefault();
    updateInputValue(input, chip.id, 'remove');
    // Show the original chip and hide the active chip
    document.querySelector(`#${chip.id}`).classList.remove('u-hide');
    this.classList.add('u-hide');
    this.removeEventListener('click', dismissChip, false);
  });
  updateInputValue(input, chip.id, 'add');
  // Hide the original chip and show the active chip
  chip.classList.add('u-hide');
  activeChip.classList.remove('u-hide');
}

function setupFuse(JSON, input) {
  const options = {
    keys: ['chipName'],
    threshold: 0.3
  };
  const fuse = new Fuse(JSON, options);
  input.addEventListener('input', () => {
    const query = document.querySelector('.js-search-input').value;
    const result = fuse.search(query);
    updateDisplayedChips(result.map(item => item.item), query);
  });
}

function updateDisplayedChips(chips, query) {
  const allChips = document.querySelectorAll('.js-chip');
  // If no query, show all chips
  if (!query) {
    allChips.forEach(chip => {
      chip.classList.remove('u-hide');
    });
  }
  // Initially hide all chips
  allChips.forEach(chip => {
    chip.classList.add('u-hide');
  });
  // If there are no results show the 'no results' message, otherwise show the filtered chips
  if (!chips.length) {
    document.querySelector('.js-no-results').classList.remove('u-hide');
  } else {
    document.querySelector('.js-no-results').classList.add('u-hide');
    chips.forEach(chip => {
      const chipElement = document.querySelector(`#${chip.chipId}`);
      chipElement.classList.remove('u-hide');
    });
  }
}

// Add click handler for clicks on elements with aria-controls
[].slice.call(document.querySelectorAll('.p-search-and-filter')).forEach(function(pattern) {
  const searchContainer = pattern.querySelector('.p-search-and-filter__search-container');
  const chipsContainer = pattern.querySelector('.p-filter-panel-section__chips');
  const targetPanel = pattern.querySelector('.p-search-and-filter__panel');
  const chipsToggle = pattern.querySelector('.js-toggle-chips-container');
  const input = pattern.querySelector('.p-search-and-filter__input');
  const chipJSON = Array.from(pattern.querySelectorAll('.js-chip')).map(chip => ({
    chipName: chip.dataset.name,
    chipId: chip.id
  }));
  const isInSearchComponent = element => element.closest('.p-search-and-filter') === pattern;
  // Open the panel when the input is focused
  pattern.addEventListener('focusin', function(e) {
    togglePanel(searchContainer, targetPanel, false);
  });
  // Close the panel when focus leaves the search component
  pattern.addEventListener('focusout', function(e) {
    console.log("here");
    if (isInSearchComponent(e.target)) {
      return;
    }
    togglePanel(searchContainer, targetPanel, true);
  });
  // Close the panel when a click occurs outside the search component
  // Also handle clicks on chips
  document.addEventListener("click", function(e) {
    if (!isInSearchComponent(e.target)) {
      togglePanel(searchContainer, targetPanel, true);
      return;
    }
    const targetChip = e.target.closest('.js-chip');
    if (targetChip) {
      e.preventDefault();
      handleChipClick(targetChip, pattern.querySelector('.js-hidden-input'));
    }
  });
  // Add handler for expanding and shrinking the chips panel
  chipsToggle.addEventListener('click', function(e) {
    e.preventDefault();
    const isExpanded = chipsContainer.getAttribute('aria-expanded') === 'true';
    chipsContainer.setAttribute('aria-expanded', isExpanded ? 'false' : 'true');
    chipsToggle.textContent = isExpanded ? 'Show more' : 'Show less';
  });
  setupFuse(chipJSON, input);
});
