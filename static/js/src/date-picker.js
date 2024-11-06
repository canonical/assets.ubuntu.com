import flatpickr from "flatpickr";

import { addValueToHiddenInput, addValueToQueryParams, } from "./main";

document.addEventListener("DOMContentLoaded", function () {
  flatpickr(".js-date-picker", {
    mode: "range",
    dateFormat: "Y-m-d",
    onChange: function(selectedDates, dateStr, instance) {
      const [startDate, endDate] = selectedDates;
      if (startDate) {
        addValueToHiddenInput(startDate.toISOString(), document.querySelector(".js-hidden-field-startdate"), replace = true);
        addValueToQueryParams("start_date", startDate.toISOString(), replace = true);
      }
      if (endDate) {
        addValueToHiddenInput(endDate.toISOString(), document.querySelector(".js-hidden-field-enddate"), replace = true);
        addValueToQueryParams("end_date", endDate.toISOString(), replace = true);
      }
    }
  });
});