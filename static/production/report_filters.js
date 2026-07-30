(function () {
  var form = document.querySelector("[data-report-filters]");
  if (!form) return;
  var group = form.querySelector("[data-filter-group]");
  var line = form.querySelector("[data-filter-line]");
  if (!group || !line) return;

  function filterLines() {
    var selectedGroup = group.value;
    var selectedLineVisible = true;
    Array.prototype.forEach.call(line.options, function (option) {
      if (!option.value) return;
      var visible = !selectedGroup || option.dataset.group === selectedGroup;
      option.hidden = !visible;
      option.disabled = !visible;
      if (option.selected && !visible) selectedLineVisible = false;
    });
    if (!selectedLineVisible) line.value = "";
  }

  group.addEventListener("change", filterLines);
  filterLines();
})();
