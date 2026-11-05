document.addEventListener("DOMContentLoaded", function() {
    // 2. Функция для расчета "времени назад"
    const rtf = new Intl.RelativeTimeFormat('ru', { numeric: 'auto' });
    
    const timeAgo = (dateString) => {
        // Парсим дату из атрибута datetime (она в UTC)
        const past = new Date(dateString);
        const now = new Date();
        const diffMs = now - past; // Разница в миллисекундах (положительная, т.к. прошлое)
        
        // Переводим в отрицательное значение для Intl.RelativeTimeFormat (прошлое = минус)
        const diffSec = Math.round(diffMs / 1000);
        const diffMin = Math.round(diffSec / 60);
        const diffHour = Math.round(diffMin / 60);
        const diffDay = Math.round(diffHour / 24);

        if (Math.abs(diffSec) < 60) return rtf.format(-diffSec, 'second');
        if (Math.abs(diffMin) < 60) return rtf.format(-diffMin, 'minute');
        if (Math.abs(diffHour) < 24) return rtf.format(-diffHour, 'hour');
        return rtf.format(-diffDay, 'day');
    };

    // 3. Применяем ко всем элементам с классом js-timeago
    document.querySelectorAll('.js-timeago').forEach(el => {
        const dateStr = el.getAttribute('datetime');
        if (dateStr) {
            // Меняем текст внутри тега на "10 минут назад"
            el.textContent = timeAgo(dateStr);
            
            // 4. Обновляем Tooltip на точное локальное время с зоной
            // toLocaleString() автоматически подставит зону браузера пользователя
            const localTime = new Date(dateStr).toLocaleString('ru-RU', {
                year: 'numeric', month: 'long', day: 'numeric',
                hour: '2-digit', minute: '2-digit',
                timeZoneName: 'short'
            });
            
            // Обновляем атрибут title и пересоздаем тултип, чтобы он показал новое значение
            el.setAttribute('data-bs-title', localTime);
        }
    });
});