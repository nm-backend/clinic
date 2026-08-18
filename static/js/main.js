// =============================================
// Минимальный JavaScript
// Всё остальное работает на чистом HTML + CSS:
//   - Модалки: нативный <dialog>
//   - Табы: radio buttons + CSS :checked
//   - Аккордеон: нативный <details>/<summary>
//   - Версия для слабовидящих: checkbox + CSS
//   - Формы: обычная отправка на Django
// =============================================


// =============================================
// Форматирование телефона: (XXX) XXX-XX-XX
// Работает с любым полем <input data-phone>
// =============================================

function formatPhoneNumber(value) {
  // Оставляем только цифры, максимум 11 штук
  var digits = value.replace(/\D/g, '').slice(0, 11);

  if (digits.length === 0) {
    return '';
  }

  // Если начинается с 8 — заменяем на 7
  if (digits[0] === '8') {
    digits = '7' + digits.slice(1);
  }

  // Если не начинается с 7 — ставим 7 в начало
  if (digits[0] !== '7') {
    digits = '7' + digits;
  }

  // Собираем формат: +7 (XXX) XXX-XX-XX
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

// Автоматически форматируем телефон при вводе
document.addEventListener('input', function (event) {
  if (event.target.matches('[data-phone]')) {
    event.target.value = formatPhoneNumber(event.target.value);
  }
});


// =============================================
// Кнопка "Показать ещё" для списка врачей
// Скрывает/показывает дополнительные карточки
// =============================================

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
