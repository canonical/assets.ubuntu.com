import { openPanel, debounce } from "./main.js";

const template = document.querySelector("#campaign-unselected-chip-template");
const chipContainer = document.querySelector(".p-chips--selected_campaigns");
const hidden_input_store = document.querySelector(
  ".js-campaign-search .js-hidden-field"
);
// Sets up the event listeners for opening the panel.
// Also calls the specific setup function.
(function () {
  const campaignsSearchComponent = document.querySelector(
    ".js-campaign-search"
  );
  if (campaignsSearchComponent) {
    const campaignsSearchInput =
      campaignsSearchComponent.querySelector(".js-campaign-input");
    if (campaignsSearchInput) {
      campaignsSearchInput.addEventListener("input", function (e) {
        const shouldOpen = e.target.value.trim().length > 0;
        openPanel(campaignsSearchComponent, shouldOpen);
      });
      setUpCampaignSearchField();
    }
  }
})();

// Sets up a query to the Salesforce Campaign DB via backend to search for campaigns.
// Calls the function that shows the search results
function setUpCampaignSearchField() {
  const campaignsInput = document.querySelector(".js-campaign-input");
  const chipContainer = document.querySelector(".js-campaign-chip-container");
  campaignsInput.addEventListener(
    "input",
    debounce(async function () {
      const query = this.value;
      chipContainer.innerHTML = "Loading...";
      if (query.trim() !== "") {
        try {
          const response = await fetch(
            `/manager/salesforce_campaigns/${query}`,
            {
              method: "GET",
            }
          );
          if (response.ok) {
            const data = await response.json();
            updateSearchResults(data);
          }
        } catch (error) {
          console.error("Error fetching campaign data:", error);
        }
      } else {
        updateSearchResults([]);
      }
    }, 700)
  );
}

function updateSearchResults(data) {
  const chipContainer = document.querySelector(".js-campaign-chip-container");
  let selectedChips = [];

  try {
    selectedChips = JSON.parse(hidden_input_store.value || "[]");
  } catch (e) {
    console.error("Failed to parse selected chips JSON:", e);
  }

  const selectedIds = new Set(selectedChips.map((chip) => chip.id));

  // Remove already selected campaigns from the results
  const filteredData = data.filter((campaign) => !selectedIds.has(campaign.id));

  chipContainer.innerHTML = "";
  if (filteredData.length === 0) {
    chipContainer.innerHTML = "<p><strong>No results found...</strong></p>";
  }
  filteredData.forEach((campaign) => {
    const chipClone = template.content.cloneNode(true);
    const chip = chipClone.querySelector(".p-chip.js-unselected");
    chip.querySelector(".js-content").textContent = campaign.name;
    chip.setAttribute("data-id", campaign.id);
    chip.setAttribute("data-name", campaign.name);
    chipContainer.appendChild(chip);
  });
}

function removeValueFromHiddenInput(chip, hiddenField) {
  let currentValues = hiddenField.value ? JSON.parse(hiddenField.value) : [];
  currentValues = currentValues.filter(
    (item) => !(item.id === chip.dataset.id)
  );
  hiddenField.value = JSON.stringify(currentValues);
}

function deselectCampaignChip(chip) {
  removeValueFromHiddenInput(chip, hidden_input_store);
  chip.remove();
}

// This function adds a value to a hidden input field.
// This is a bit different since it is made to add json string
function addValueToHiddenInput(chip, hiddenField) {
  const chipDetails = {
    id: chip.dataset.id,
    name: chip.dataset.name,
  };

  const currentValues = hiddenField.value ? JSON.parse(hiddenField.value) : [];

  const alreadyExists = currentValues.some(
    (item) => item.id === chipDetails.id
  );

  if (!alreadyExists) {
    currentValues.push(chipDetails);
    hiddenField.value = JSON.stringify(currentValues);
    return true; // Indicates that the value was added
  }
  return false; // Indicates that the value already exists
}

function selectCampaignChip(chip) {
  const unique = addValueToHiddenInput(chip, hidden_input_store);
  if (!unique) {
    return; // If the value already exists, do not proceed
  }

  const chipClone = template.content.cloneNode(true);

  const dismissButton = document.createElement("button");
  dismissButton.classList.add("p-chip__dismiss");
  dismissButton.textContent = "Dismiss";

  const newchip = chipClone.querySelector(".p-chip.js-unselected");
  newchip.appendChild(dismissButton);
  newchip.classList.remove("js-unselected");
  newchip.classList.add("js-selected");
  newchip.setAttribute("data-id", chip.dataset.id);
  newchip.setAttribute("data-name", chip.dataset.name);
  newchip.querySelector(".js-content").textContent = chip.dataset.name;
  chipContainer.appendChild(newchip);

  // clear the entered value after selecting a chip
  const inputField = document.querySelector(
    ".js-campaign-search .js-campaign-input"
  );
  inputField.value = "";
  inputField.focus();

  // Hide panel and reset the chips panel
  const chipsPanel = document.querySelector(
    ".js-campaign-search .js-chips-panel"
  );
  chipsPanel.setAttribute("aria-hidden", "true");
  chipsPanel.querySelector(".js-campaign-chip-container").innerHTML =
    "Loading...";
}

export default function handleCampaignChip(targetChip) {
  if (targetChip.classList.contains("js-unselected")) {
    selectCampaignChip(targetChip);
  } else if (targetChip.classList.contains("js-selected")) {
    deselectCampaignChip(targetChip);
  }
}
