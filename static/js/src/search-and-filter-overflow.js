/**
 * Return number of overflowing chips given a row threshold
 * @param {array} chips - An array of chips
 * @param {Integer} overflowRowLimit - Number of rows to show before counting
 * overflow
 */
export const overflowingChipsCount = (chips, overflowRowLimit) => {
  let overflowChips = 0;
  if (chips) {
    chips.forEach((chip) => {
      // If the offsetTop is more than double height of a single chip, consider it
      // overflowing
      if (chip.offsetTop > chip.offsetHeight * overflowRowLimit)
        overflowChips++;
    });
  }
  return overflowChips;
};

export const setOverflowCounter = (overflowCount, overflowCountEl) => {
  if (!overflowCountEl) return;
  if (overflowCount && overflowCount > 0) {
    overflowCountEl.textContent = `+${overflowCount}`;
    return;
  }
  overflowCountEl.textContent = "";
};

export const updateFlowCount = function (chipsContainerRef) {
  const chips = chipsContainerRef.querySelectorAll(
    ".p-chip.js-selected:not(.u-hide)"
  );
  const overflowCount = overflowingChipsCount(chips, 1);
  setOverflowCounter(
    overflowCount,
    chipsContainerRef.querySelector(".p-search-and-filter__selected-count")
  );
};

// Add click handler for clicks on elements with aria-controls
[].slice
  .call(document.querySelectorAll(".p-search-and-filter"))
  .forEach(function (pattern) {
    updateFlowCount(pattern);
    var overflowCount = pattern.querySelector(
      ".p-search-and-filter__selected-count"
    );
    var container = pattern.querySelector(
      ".p-search-and-filter__search-container"
    );

    if (container) {
      // Create a MutationObserver instance
      const observer = new MutationObserver((mutationsList, observer) => {
        for (const mutation of mutationsList) {
          if (
            mutation.type === "attributes" &&
            mutation.attributeName === "class"
          ) {
            updateFlowCount(pattern);
          }
        }
      });

      // Configure the observer
      const config = {
        subtree: true,
        attributeFilter: ["class"],
      };

      // Start observing
      observer.observe(container, config);
    }

    var searchBox = pattern.querySelector(".p-search-and-filter__box");

    var panel = pattern.querySelector(".p-search-and-filter__panel");

    if (overflowCount) {
      overflowCount.addEventListener("click", function (event) {
        searchBox.dataset.overflowing = "true";
        panel.setAttribute("aria-hidden", "false");
        container.setAttribute("aria-expanded", "true");
      });
    }
  });

export const setupOverflowingProductPanels = () => {
  [].slice
    .call(document.querySelectorAll(".p-filter-panel-section"))
    .forEach(function (section) {
      var overflowCountEl = section.querySelector(
        ".p-filter-panel-section__selected-count"
      );

      var container = section.querySelector(".p-filter-panel-section__chips");

      const chips = container.querySelectorAll(
        ".p-chip.js-unselected:not(.u-hide)"
      );

      const overflowCount = overflowingChipsCount(chips, 1);

      if (overflowCountEl) {
        setOverflowCounter(overflowCount, overflowCountEl);

        container.style.overflow = "hidden";
        container.style.height = "2.5rem";

        overflowCountEl.addEventListener("click", function (event) {
          container.style.height = "auto";
          overflowCountEl.classList.add("u-hide");
        });
      }
    });
};

document
  .querySelectorAll(".p-search-and-filter__selected-count")
  .forEach((el) => {
    el.addEventListener("click", function (e) {
      if (
        (searchEl = el
          .closest(".p-search-and-filter__search-container")
          ?.querySelector(".p-search-and-filter__input"))
      ) {
        searchEl.focus();
      }
    });
  });

setupOverflowingProductPanels();
