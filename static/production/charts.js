(function () {
  function readJson(id) {
    var node = document.getElementById(id);
    return node ? JSON.parse(node.textContent) : [];
  }

  function drawAxes(ctx, w, h, padding) {
    ctx.strokeStyle = "#d8e0e2";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, h - padding);
    ctx.lineTo(w - padding, h - padding);
    ctx.stroke();
  }

  function maxValue(series) {
    var values = [];
    series.forEach(function (items) {
      values = values.concat(items);
    });
    return Math.max(1, Math.max.apply(Math, values));
  }

  function formatNumber(value, compact) {
    return Number(value || 0).toLocaleString("fa-IR", {
      maximumFractionDigits: compact ? 0 : 2,
    });
  }

  function drawLineChart(canvas, labels, total, useful) {
    if (!canvas) return;
    var ctx = canvas.getContext("2d");
    var ratio = window.devicePixelRatio || 1;
    var rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * ratio;
    canvas.height = rect.height * ratio;
    ctx.scale(ratio, ratio);

    var w = rect.width;
    var h = rect.height;
    var p = 34;
    ctx.clearRect(0, 0, w, h);
    drawAxes(ctx, w, h, p);

    var max = maxValue([total, useful]);
    var count = Math.max(labels.length, 2);
    function point(value, index) {
      var x = p + (index * (w - p * 2)) / (count - 1);
      var y = h - p - (value / max) * (h - p * 2);
      return [x, y];
    }
    function line(values, color) {
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      values.forEach(function (value, index) {
        var pt = point(value, index);
        if (index === 0) ctx.moveTo(pt[0], pt[1]);
        else ctx.lineTo(pt[0], pt[1]);
      });
      ctx.stroke();
    }
    line(total, "#0f766e");
    line(useful, "#f59e0b");
  }

  function drawBarChart(canvas, labels, values, options) {
    if (!canvas) return;
    options = options || {};
    var ctx = canvas.getContext("2d");
    var ratio = window.devicePixelRatio || 1;
    var rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * ratio;
    canvas.height = rect.height * ratio;
    ctx.scale(ratio, ratio);

    var w = rect.width;
    var h = rect.height;
    var p = 44;
    ctx.clearRect(0, 0, w, h);
    drawAxes(ctx, w, h, p);
    var max = maxValue([values]);
    var barArea = w - p * 2;
    var gap = values.length > 18 ? 2 : 12;
    var barWidth = Math.max(2, (barArea - gap * Math.max(values.length - 1, 0)) / Math.max(values.length, 1));
    var labelStep = Math.max(1, Math.ceil(values.length / 18));
    values.forEach(function (value, index) {
      var height = (value / max) * (h - p * 2);
      var x = p + index * (barWidth + gap);
      var y = h - p - height;
      ctx.fillStyle = options.color || "#0f766e";
      ctx.fillRect(x, y, barWidth, height);
      ctx.fillStyle = "#172026";
      ctx.font = "10px Tahoma";
      ctx.textAlign = "center";
      if (index % labelStep === 0 || values.length <= 18) {
        ctx.fillText(formatNumber(value, true), x + barWidth / 2, Math.max(12, y - 6));
      }
      ctx.fillStyle = "#54646b";
      ctx.font = values.length > 18 ? "9px Tahoma" : "11px Tahoma";
      var label = labels[index] || "";
      if (values.length > 18 && index % Math.ceil(values.length / 12) !== 0) {
        label = "";
      }
      ctx.fillText(label, x + barWidth / 2, h - 10);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    drawLineChart(
      document.getElementById("trendChart"),
      readJson("trend-labels"),
      readJson("trend-total"),
      readJson("trend-useful")
    );
    drawBarChart(document.getElementById("lineChart"), readJson("line-labels"), readJson("line-totals"));
    drawBarChart(
      document.getElementById("dailyComparisonChart"),
      readJson("daily-labels"),
      readJson("daily-totals"),
      { color: "#0f766e" }
    );
    drawBarChart(
      document.getElementById("monthlyComparisonChart"),
      readJson("monthly-labels"),
      readJson("monthly-totals"),
      { color: "#f59e0b" }
    );
    drawBarChart(
      document.getElementById("dailyUsefulChart"),
      readJson("daily-labels"),
      readJson("daily-useful"),
      { color: "#2563eb" }
    );
    drawBarChart(
      document.getElementById("lineYieldChart"),
      readJson("comparison-line-labels"),
      readJson("comparison-line-yields"),
      { color: "#7c3aed" }
    );
    drawBarChart(
      document.getElementById("dailyRangeTotalChart"),
      readJson("daily-range-labels"),
      readJson("daily-range-totals"),
      { color: "#0f766e" }
    );
    drawBarChart(
      document.getElementById("dailyRangeUsefulChart"),
      readJson("daily-range-labels"),
      readJson("daily-range-useful"),
      { color: "#2563eb" }
    );
    Array.prototype.forEach.call(document.querySelectorAll(".report-chart"), function (canvas) {
      drawBarChart(
        canvas,
        readJson(canvas.dataset.labels),
        readJson(canvas.dataset.values),
        { color: canvas.dataset.color || "#0f766e" }
      );
    });
  });
})();
