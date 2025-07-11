document.addEventListener("DOMContentLoaded", () => {
  const selectedServers = new Set();

  // 1) Обробка кліків на папках — згортання/розгортання
  document.querySelectorAll('.folder-label').forEach(label => {
    label.style.cursor = 'pointer';
    label.addEventListener('click', (e) => {
      const nested = label.nextElementSibling;
      if (nested) {
        nested.classList.toggle('collapsed');
      }
      label.classList.toggle('open'); // Для підсвітки активної папки
      e.stopPropagation();
    });
  });

  // 2) Обробка кліків по командах у списку
  document.querySelectorAll('#command-list .nested-list li').forEach(item => {
    item.addEventListener('click', () => {
      const script = item.dataset.script;
      const commandInput = document.getElementById('command-input');
      if (script) {
        commandInput.value = `download_and_run_script ${script}`;
      } else {
        commandInput.value = item.innerText;
      }
    });
  });

  // 3) Відправка команди
  async function sendCommand() {
    const commandInput = document.getElementById('command-input');
    const command = commandInput.value.trim();
    const sendBtn = document.getElementById('send-btn');
    const output = document.getElementById('command-output');

    if (selectedServers.size === 0 || !command) {
      alert("Оберіть хоча б один сервер та введіть команду.");
      return;
    }

    sendBtn.disabled = true;
    sendBtn.textContent = "Надсилання...";

    for (const serverId of selectedServers) {
      await fetch(`/set_command/${serverId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command })
      });
    }

    for (const serverId of selectedServers) {
      let tries = 10;
      while (tries-- > 0) {
        const res = await fetch(`/get_result/${serverId}`);
        const data = await res.json();
        if (data.status !== "no_result") {
          output.value += `=== ${serverId} ===\n${data.stdout || JSON.stringify(data)}\n\n----------------------\n`;
          break;
        }
        await new Promise(r => setTimeout(r, 1000));
      }
    }

    sendBtn.disabled = false;
    sendBtn.textContent = "Надіслати";
  }

  // 4) Завантаження списку серверів
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

  //----------------Select/Deselect all toggle button------------------------//

  // Select/Deselect all toggle button logic
  const toggleSelectBtn = document.getElementById('toggle-select-all');
  toggleSelectBtn.addEventListener('click', () => {
    const listItems = document.querySelectorAll('#server-list li');
    const selectAll = toggleSelectBtn.textContent === "Вибрати всі";

    listItems.forEach(li => {
      const server = li.textContent;

      if (selectAll && !selectedServers.has(server)) {
        li.classList.add('selected');
        selectedServers.add(server);
      } else if (!selectAll && selectedServers.has(server)) {
        li.classList.remove('selected');
        selectedServers.delete(server);
      }
    });

    toggleSelectBtn.textContent = selectAll ? "Скасувати вибір" : "Вибрати всі";
  });

  // Optional: update toggle button text depending on selection state
  function updateToggleSelectButton() {
    const listItems = document.querySelectorAll('#server-list li');
    const allSelected = [...listItems].every(li => li.classList.contains('selected'));
    toggleSelectBtn.textContent = allSelected ? "Скасувати вибір" : "Вибрати всі";
  }

  // -----------------------Clear button------------------------//
  const output = document.getElementById("command-output");
  const clearBtn = document.getElementById("clear-btn");
  clearBtn.addEventListener("click", () => {
    output.value = "";
  });
});
