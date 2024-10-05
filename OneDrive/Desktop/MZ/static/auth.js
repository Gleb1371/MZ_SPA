document.getElementById('loginBtn').addEventListener('click', async (event) => {
    event.preventDefault();
    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/auth', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ login, password }),
        });

        const data = await response.json();
        if (response.ok) {
            window.location.href = 'LK.html'; // Перенаправление на страницу личного кабинета
        } else {
            alert(`Ошибка: ${data.error}`);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при входе.');
    }
});
