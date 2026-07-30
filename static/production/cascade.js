(function () {
  function toNumber(value) {
    var normalized = String(value || "").replace(",", ".");
    var number = Number(normalized);
    return Number.isFinite(number) ? number : 0;
  }

  function filterSelect(select, groupId) {
    if (!select) return;
    var selectedStillVisible = false;
    Array.prototype.forEach.call(select.options, function (option) {
      var optionGroup = option.getAttribute("data-group");
      var visible = !option.value || (groupId && optionGroup === groupId);
      option.hidden = !visible;
      option.disabled = !visible;
      if (option.selected && visible) {
        selectedStillVisible = true;
      }
    });
    if (!selectedStillVisible) {
      select.value = "";
    }
  }

  function applyCascade() {
    var groupSelect = document.getElementById("id_product_group");
    var groupId = groupSelect ? groupSelect.value : "";
    Array.prototype.forEach.call(document.querySelectorAll("[data-cascade]"), function (select) {
      filterSelect(select, groupId);
    });
  }

  function updateTotals() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-formset]"), function (container) {
      var name = container.getAttribute("data-formset");
      var total = 0;
      Array.prototype.forEach.call(container.querySelectorAll("[data-form-row]"), function (row) {
        var deleteInput = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
        if (deleteInput && deleteInput.checked) return;
        var quantity = row.querySelector('input[name$="-quantity"]');
        total += toNumber(quantity ? quantity.value : 0);
      });
      var target = document.querySelector('[data-total="' + name + '"]');
      if (target) {
        target.textContent = total.toLocaleString("fa-IR", { maximumFractionDigits: 2 });
      }
    });
  }

  function addRow(name) {
    var template = document.querySelector('[data-empty-form="' + name + '"]');
    var container = document.querySelector('[data-formset="' + name + '"]');
    var totalForms = document.getElementById("id_" + name + "-TOTAL_FORMS");
    if (!template || !container || !totalForms) return;

    var index = Number(totalForms.value);
    var html = template.innerHTML.replace(/__prefix__/g, String(index));
    container.insertAdjacentHTML("beforeend", html);
    totalForms.value = String(index + 1);
    applyCascade();
    updateTotals();

    var newRow = container.querySelector("[data-form-row]:last-child");
    var firstSelect = newRow ? newRow.querySelector("select") : null;
    if (firstSelect) firstSelect.focus();
  }

  function handleDelete(event) {
    var checkbox = event.target.closest('input[type="checkbox"][name$="-DELETE"]');
    if (!checkbox) return;
    var row = checkbox.closest("[data-form-row]");
    if (row) {
      row.classList.toggle("is-deleted", checkbox.checked);
    }
    updateTotals();
  }

  document.addEventListener("DOMContentLoaded", function () {
    var groupSelect = document.getElementById("id_product_group");
    applyCascade();
    updateTotals();
    if (groupSelect) {
      groupSelect.addEventListener("change", function () {
        applyCascade();
        updateTotals();
      });
    }
    document.addEventListener("click", function (event) {
      var button = event.target.closest("[data-add-row]");
      if (button) {
        addRow(button.getAttribute("data-add-row"));
      }
    });
    document.addEventListener("input", updateTotals);
    document.addEventListener("change", handleDelete);
  });
})();
