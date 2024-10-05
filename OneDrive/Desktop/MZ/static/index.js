document.addEventListener('DOMContentLoaded', function() {
    // Находим элементы
    const toggleText = document.querySelector('.toggle-text');
    const ramText = document.querySelector('.ram-text');

    // Скрываем текст при загрузке страницы
    ramText.style.display = 'none';

    // Добавляем обработчик события клика
    toggleText.addEventListener('click', function() {
        // Переключаем видимость текста и изменяем иконку
        ramText.style.display = ramText.style.display === 'none' ? 'block' : 'none';
        const toggleIcon = toggleText.querySelector('.toggle-icon');
        toggleIcon.textContent = ramText.style.display === 'none' ? '+' : '-';
    });
});