// Here we define the handlers for generic fields

import { addValueToQueryParams } from "./main";

// Define whether we are in search and thus need to update query params
const updateQueryParams = document.querySelector('.js-asset-search');

/*
 * Function to handle multiselects as they were not submitting all the selected values.
 **/
const multiSelects = document.querySelectorAll('.js-multiselect');
multiSelects?.forEach(multiSelect => {
  const hiddenField = multiSelect.querySelector('.js-hidden-field');
  multiSelect = multiSelect.tagName.toLowerCase() === 'select' ? multiSelect : multiSelect.querySelector('select');
  multiSelect.addEventListener('change', function() {
    const values = Array.from(multiSelect.selectedOptions).map(option => option.value).join(',');
    hiddenField.value = values;
    if (updateQueryParams) {
      addValueToQueryParams(hiddenField.name, values, replace = true);
    }
  });
});

/*
 * Function to handle select as they were not submitting all the selected values.
 **/
function handleSelectInputs() {
  const selects = document.querySelectorAll('.js-select');
  selects?.forEach(select => {
    select = select.querySelector('select');
    select.addEventListener('change', function() {
      addValueToQueryParams(select.name, select.value, replace = true);
    });
  });
}

/*
 * Function to handle tags input
 */
function handleTagInput() {
  const tagsInput = document.querySelector('.js-tags');
  tagsInput?.addEventListener('input', function(e) {
    addValueToQueryParams(tagsInput.name, tagsInput.value, replace = true);
  });
}

/*
 * Function to handle salesforce id input
 */
function handleSalesforceIdInput() {
  const salesforceIdInput = document.querySelector('.js-salesforce-campaign-id');
  salesforceIdInput?.addEventListener('input', function(e) {
    addValueToQueryParams(salesforceIdInput.name, salesforceIdInput.value, replace = true);
  });
}

// These field will auto submit and only need to be handled if we are on search and want to add them to the query params
if (updateQueryParams) {
  handleSelectInputs();
  handleTagInput();
  handleSalesforceIdInput();
}