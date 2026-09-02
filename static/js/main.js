function formatPhoneNumber(value) {
  var digits = value.replace(/\D/g, '').slice(0, 11);

  if (digits.length === 0) {
    return '';
  }

  if (digits[0] === '8') {
    digits = '7' + digits.slice(1);
  }

  if (digits[0] !== '7') {
    digits = '7' + digits;
  }

  var result = '+7';

  if (digits.length > 1) {
    result += ' (' + digits.slice(1, 4);
  }
  if (digits.length >= 4) {
    result += ')';
  }
  if (digits.length > 4) {
    result += ' ' + digits.slice(4, 7);
  }
  if (digits.length > 7) {
    result += '-' + digits.slice(7, 9);
  }
  if (digits.length > 9) {
    result += '-' + digits.slice(9, 11);
  }

  return result;
}

document.addEventListener('input', function (event) {
  if (event.target.matches('[data-phone]')) {
    event.target.value = formatPhoneNumber(event.target.value);
  }
});

document.addEventListener('click', function (event) {
  var showMoreButton = event.target.closest('[data-show-more]');
  if (showMoreButton) {
    var doctorsGrid = document.querySelector('.doctors-grid');
    if (doctorsGrid) {
      doctorsGrid.classList.add('is-open');
      showMoreButton.closest('.show-more').style.display = 'none';
    }
  }
});

var burger = document.getElementById('header-burger');
var menu = document.getElementById('header-menu');

if (burger && menu) {
  burger.addEventListener('click', function () {
    var isOpen = menu.classList.toggle('is-open');
    burger.classList.toggle('is-active', isOpen);
    burger.setAttribute('aria-expanded', isOpen);
  });

  document.addEventListener('click', function (e) {
    if (!burger.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.remove('is-open');
      burger.classList.remove('is-active');
      burger.setAttribute('aria-expanded', 'false');
    }
  });
}

document.addEventListener('click', function (e) {
  var dropdownToggle = e.target.closest('.header-dropdown-toggle');
  if (dropdownToggle) {
    var dropdown = dropdownToggle.closest('.header-dropdown');
    if (dropdown && window.innerWidth <= 768) {
      e.preventDefault();
      dropdown.classList.toggle('is-open');
    }
  }
});