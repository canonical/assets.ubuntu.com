import './products-search';
import handleProductsChip from './products-search';

/*
 * Event delgation to handle the click event on the document.
 **/
document.addEventListener('click', function (e) {
  const targetChip = e.target.closest('.p-chip');
  if (targetChip) {
    e.preventDefault();
    if (targetChip.closest('.js-products-search')) {
      handleProductsChip(targetChip);
      return;
    }
  }
  const activeSearchComponent = document.querySelector('.js-active-search');
  if (!activeSearchComponent) {
    return;
  }
  if (!isInActiveSearchComponent(e.target, activeSearchComponent)) {
    openPanel(activeSearchComponent, false);
    return;
  }
});

/* 
 * Generic function to show and hide the chips selection panel.
 * @param {HTMLElement} searchContainer - The whole pannel container.
 * @param {HTMLElement} panel - Where the chips are displayed.
 * @param {Boolean} isOpen - Whether the panel should end open or closed.
 **/
export function openPanel(searchComponent, opening = 'false') {
  const searchContainer = searchComponent.querySelector('.p-search-and-filter__search-container');
  const panel = searchComponent.querySelector('.p-search-and-filter__panel');
  if (panel && searchContainer) {
    if (opening) {
      panel.setAttribute('aria-hidden', 'false');
      searchContainer.setAttribute('aria-expanded', 'true');
      searchComponent.classList.add('js-active-search');
    } else {
      panel.setAttribute('aria-hidden', 'true');
      searchContainer.setAttribute('aria-expanded', 'false');
      searchComponent.classList.remove('js-active-search');
    }
  }
}

/* 
 * Generic function to add the value of a selected chip, to the value of a hidden input.
 * We have to do this as the chips will not be submitted with the form.
 * @param {String} value - The value of the chip.
 * @param {HTMLElement} input - The hidden input to store the values.
 **/
export function addValueToHiddenInput(value, input) {
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
export function removeValueFromHiddenInput(value, input) {
  let selectedChips = input.value.split(',').filter(Boolean);
  selectedChips = selectedChips.filter(id => id !== value);
  input.setAttribute('value', selectedChips.join(','));
}

/*
 * Generic function to check if a search component is active.
 * @param {HTMLElement} target - The element that triggered the event.
 * @param {HTMLElement} searchComponent - The search component.
 **/ 
export function isInActiveSearchComponent(target, searchComponent) {
  const componentIsActive = searchComponent.classList.contains('js-active-search');
  return target.closest('.p-search-and-filter') === searchComponent && componentIsActive;
}