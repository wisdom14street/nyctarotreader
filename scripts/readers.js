/* Progressive filtering only: booking anchors work without scripts or analytics. */
(function () {
  var root = document.querySelector('[data-reader-directory]');
  if (!root) return;
  var controls = root.querySelector('[data-reader-filters]');
  var format = root.querySelector('#reader-format');
  var budget = root.querySelector('#reader-budget');
  var cards = Array.from(root.querySelectorAll('[data-reader-card]'));
  function readPreferences() {
    var query = new URLSearchParams(location.search);
    [ [format, 'format'], [budget, 'budget'] ].forEach(function (pair) {
      var value = query.get(pair[1]) || '';
      pair[0].value = Array.from(pair[0].options).some(function (option) { return option.value === value; }) ? value : '';
    });
  }
  function savePreferences() {
    try {
      var url = new URL(location.href);
      [ [format, 'format'], [budget, 'budget'] ].forEach(function (pair) {
        if (pair[0].value) url.searchParams.set(pair[1], pair[0].value);
        else url.searchParams.delete(pair[1]);
      });
      history.replaceState(null, '', url.href);
    } catch (_) { /* Filtering must still work when history access is restricted. */ }
  }
  function update(track) {
    var count = 0;
    cards.forEach(function (card) {
      var matches = (!format.value || card.dataset.formats.split(' ').includes(format.value)) &&
        (!budget.value || Number(card.dataset.price) <= Number(budget.value));
      card.hidden = !matches;
      if (matches) count++;
    });
    root.querySelectorAll('[data-reader-group]').forEach(function (group) {
      group.hidden = !group.querySelector('[data-reader-card]:not([hidden])');
    });
    root.querySelector('[data-reader-count]').textContent = count + ' readers match your preferences. Check Square for open times.';
    root.querySelector('[data-reader-empty]').hidden = count !== 0;
    if (track) savePreferences();
    if (track && typeof window.niGA === 'function') window.niGA('reader_filter', {
      session_format: format.value || 'all', guide_budget: budget.value || 'all', result_count: count
    });
  }
  controls.hidden = false;
  controls.addEventListener('change', function () { update(true); });
  root.querySelector('[data-reader-reset]').addEventListener('click', function () {
    format.value = ''; budget.value = ''; update(true); format.focus();
  });
  readPreferences();
  update(false);
  window.addEventListener('popstate', function () { readPreferences(); update(false); });
})();
