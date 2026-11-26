/* Course hub progressive enhancements: live mastery pill and module table filter. */
(function () {
  var masteryPills = document.querySelectorAll('[data-course-mastery]');
  masteryPills.forEach(function (pill) {
    var slug = pill.getAttribute('data-course-mastery');
    var total = parseInt(pill.getAttribute('data-course-mastery-total') || '0', 10);
    var prefix = pill.getAttribute('data-course-mastery-label') || 'Question Bank';
    var done = 0;
    try {
      var raw = localStorage.getItem('qb_mastery_' + slug);
      var parsed = raw ? JSON.parse(raw) : {};
      if (Array.isArray(parsed)) {
        done = parsed.length;
      } else if (parsed && typeof parsed === 'object') {
        done = Object.keys(parsed).length;
      }
      if (total > 0 && done > total) {
        done = total;
      }
    } catch (e) {
      done = 0;
    }
    if (total > 0) {
      pill.textContent = prefix + ' (' + done + '/' + total + ')';
      pill.classList.toggle('has-progress', done > 0);
    }
  });

  var input = document.getElementById('module-filter-input');
  var clearBtn = document.getElementById('module-filter-clear');
  var statusEl = document.getElementById('module-filter-status');
  var table = document.querySelector('#materials table.materials');
  if (!input || !table) {
    return;
  }

  var rows = Array.from(table.querySelectorAll('tr[id]'));
  if (rows.length === 0) {
    rows = Array.from(table.querySelectorAll('tr')).slice(1);
  }

  function applyFilter() {
    var q = input.value.trim().toLowerCase();
    var visible = 0;
    rows.forEach(function (row) {
      var match = !q || row.textContent.toLowerCase().indexOf(q) !== -1;
      row.style.display = match ? '' : 'none';
      if (match) {
        visible++;
      }
    });
    if (statusEl) {
      statusEl.textContent = 'Showing ' + visible + ' of ' + rows.length + ' modules';
    }
    if (clearBtn) {
      clearBtn.hidden = q.length === 0;
    }
  }

  input.addEventListener('input', applyFilter);
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      input.value = '';
      applyFilter();
      input.focus();
    });
  }
  applyFilter();
})();
