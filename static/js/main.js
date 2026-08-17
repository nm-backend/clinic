(function () {
  'use strict';

  function getCsrfToken() {
    var input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : '';
  }

  function openModal(modal) {
    var overlay = document.querySelector('[data-modal="' + modal + '"]');
    if (overlay) {
      overlay.classList.add('is-open');
      document.body.style.overflow = 'hidden';
    }
  }

  function closeModal(overlay) {
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
  }

  document.addEventListener('click', function (event) {
    var accessibility = event.target.closest('.header-accessibility');
    if (accessibility) {
      document.body.classList.toggle('accessibility-mode');
      var enabled = document.body.classList.contains('accessibility-mode');
      accessibility.textContent = enabled ? 'Обычная версия' : 'Версия для слабовидящих';
      return;
    }

    var showMore = event.target.closest('[data-show-more]');
    if (showMore) {
      var grid = document.querySelector('.doctors-grid');
      if (grid) {
        grid.classList.add('is-open');
        showMore.closest('.show-more').style.display = 'none';
      }
      return;
    }

    var opener = event.target.closest('[data-modal-open]');
    if (opener) {
      event.preventDefault();
      openModal(opener.getAttribute('data-modal-open'));
      return;
    }

    var closer = event.target.closest('[data-modal-close]');
    if (closer) {
      closeModal(closer.closest('.modal-overlay'));
      return;
    }

    if (event.target.classList.contains('modal-overlay')) {
      closeModal(event.target);
    }

    var accordionHeader = event.target.closest('.accordion-header');
    if (accordionHeader) {
      var item = accordionHeader.closest('.accordion-item');
      var body = item.querySelector('.accordion-body');
      var isOpen = item.classList.contains('is-open');
      var group = item.parentElement;
      group.querySelectorAll('.accordion-item.is-open').forEach(function (other) {
        other.classList.remove('is-open');
        var otherBody = other.querySelector('.accordion-body');
        if (otherBody) otherBody.style.maxHeight = null;
      });
      if (!isOpen) {
        item.classList.add('is-open');
        body.style.maxHeight = body.scrollHeight + 'px';
      }
    }
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.is-open').forEach(closeModal);
    }
  });

  function showToast(message) {
    var toast = document.querySelector('[data-toast]');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('is-visible');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(function () {
      toast.classList.remove('is-visible');
    }, 4000);
  }

  function formatPhone(value) {
    var digits = value.replace(/\D/g, '').slice(0, 11);
    if (digits.length === 0) return '';
    if (digits[0] === '8') digits = '7' + digits.slice(1);
    if (digits[0] !== '7') digits = '7' + digits;
    var result = '+7';
    if (digits.length > 1) result += ' (' + digits.slice(1, 4);
    if (digits.length >= 4) result += ')';
    if (digits.length > 4) result += ' ' + digits.slice(4, 7);
    if (digits.length > 7) result += '-' + digits.slice(7, 9);
    if (digits.length > 9) result += '-' + digits.slice(9, 11);
    return result;
  }

  document.addEventListener('input', function (event) {
    if (event.target.matches('[data-phone]')) {
      event.target.value = formatPhone(event.target.value);
    }
  });

  document.addEventListener('submit', function (event) {
    var form = event.target.closest('form[data-form]');
    if (!form) return;

    var overlay = form.closest('.modal-overlay');
    var name = form.querySelector('[name="full_name"]').value.trim();
    var phone = form.querySelector('[name="phone"]').value.trim();
    var valid = name.length >= 3 && phone.replace(/\D/g, '').length >= 10;

    if (!valid) {
      event.preventDefault();
      showToast('Пожалуйста, укажите ФИО (не менее 3 символов) и корректный номер телефона');
      return;
    }

    event.preventDefault();
    var action = form.getAttribute('action');
    var data = new FormData(form);

    fetch(action, {
      method: 'POST',
      body: data,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCsrfToken(),
      },
      credentials: 'same-origin',
    })
      .then(function (response) {
        if (response.ok) {
          form.reset();
          if (overlay) closeModal(overlay);
          showToast('Заявка отправлена! Мы свяжемся с вами в ближайшее время.');
        } else {
          return response.json().then(function (body) {
            showToast(body.detail || 'Не удалось отправить заявку. Попробуйте ещё раз.');
          });
        }
      })
      .catch(function () {
        showToast('Ошибка соединения. Попробуйте ещё раз.');
      });
  });
})();