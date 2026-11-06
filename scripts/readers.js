/* Progressive filtering only: booking anchors work without scripts or analytics. */
(function () {
  var root = document.querySelector('[data-reader-directory]');
  if (!root) return;
  var controls = root.querySelector('[data-reader-filters]');
  var format = root.querySelector('#reader-format');
  var budget = root.querySelector('#reader-budget');
  var cards = Array.from(root.querySelectorAll('[data-reader-card]'));
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
    if (track && typeof window.niGA === 'function') window.niGA('reader_filter', {
      session_format: format.value || 'all', guide_budget: budget.value || 'all', result_count: count
    });
  }
  controls.hidden = false;
  controls.addEventListener('change', function () { update(true); });
  root.querySelector('[data-reader-reset]').addEventListener('click', function () {
    format.value = ''; budget.value = ''; update(true); format.focus();
  });
  update(false);
})();
