document.getElementById('registerBtn').addEventListener('click', async (event) => {
    event.preventDefault();
    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/registration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ login, password }),
        });

        const data = await response.json();
        if (response.ok) {
            alert('Регистрация прошла успешно!');
            window.location.href = 'index.html'; // Перенаправление на главную страницу
        } else {
            alert(`Ошибка: ${data.error}`);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при регистрации.');
    }
});