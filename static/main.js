document.addEventListener("DOMContentLoaded", () => {
    const selectedServers = new Set();

    document.querySelectorAll('#command-list li').forEach(item => {
        item.addEventListener('click', () => {
            document.getElementById('command-input').value = item.innerText;
        });
    });

async function sendCommand() {
    const command = document.getElementById('command-input').value.trim();
    const sendBtn = document.getElementById('send-btn');

    if (selectedServers.size === 0 || !command) {
        alert("Оберіть хоча б один сервер та введіть команду.");
        return;
    }

    sendBtn.disabled = true;                    // 🔒 Блокуємо кнопку
    sendBtn.textContent = "Надсилання...";      // (опціонально) змінюємо текст

    const output = document.getElementById('command-output');

    for (const serverId of selectedServers) {
        await fetch(`/set_command/${serverId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command })
        });
    }

    for (const serverId of selectedServers) {
        let tries = 30;
        while (tries-- > 0) {
            const res = await fetch(`/get_result/${serverId}`);
            const data = await res.json();
            if (data.status !== "no_result") {
                output.innerHTML += `<div><strong>${serverId}:</strong><br><pre>${data.stdout || JSON.stringify(data)}</pre></div><hr>`;
                break;
            }
            await new Promise(r => setTimeout(r, 1000));
        }
    }

    sendBtn.disabled = false;                   // ✅ Активуємо кнопку назад
    sendBtn.textContent = "Надіслати";          // Повертаємо текст
}


    async function loadServers() {
        const res = await fetch('/servers');
        const servers = await res.json();
        const list = document.getElementById('server-list');
        list.innerHTML = '';

        servers.forEach(server => {
            const li = document.createElement('li');
            li.textContent = server;

            li.addEventListener('click', () => {
                li.classList.toggle('selected');
                if (selectedServers.has(server)) {
                    selectedServers.delete(server);
                } else {
                    selectedServers.add(server);
                }
            });

            list.appendChild(li);
        });
    }

    window.sendCommand = sendCommand;

    loadServers();
});
