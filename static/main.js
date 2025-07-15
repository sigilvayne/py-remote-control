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
      label.classList.toggle('open');
      e.stopPropagation();
    });
  });

  // 2) Обробка кліків по командах у списку
  document.querySelectorAll('#command-list .nested-list li').forEach(item => {
    item.addEventListener('click', () => {
      const script = item.dataset.script;
      const dynamic = item.dataset.dynamic;
      const commandInput = document.getElementById('command-input');

      if (dynamic === "medoc-download") {
        fetch('/get_medoc_version')
          .then(res => res.json())
          .then(data => {
            if (data.version) {
              const version = data.version.trim();
              const url = `https://load.medoc.ua/update/${version}.zip`;
              commandInput.value = `download_and_run_script download-medoc-update.ps1 ${JSON.stringify(url)}`;
            } else {
              alert("Не вдалося отримати версію з medoc-ver.txt");
            }
          }).catch(err => {
            alert("Помилка при отриманні версії Medoc: " + err);
          });
      } else if (script) {
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

    try {
      for (const serverId of selectedServers) {
        // Відправляємо команду і отримуємо command_id
        const res = await fetch(`/set_command/${serverId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ command })
        });
        if (!res.ok) throw new Error(`Помилка при надсиланні команди на сервер ${serverId}`);

        const { command_id } = await res.json();

        // Чекаємо результат з конкретним command_id
        let tries = 10;
        while (tries-- > 0) {
          const resultRes = await fetch(`/get_result/${serverId}?command_id=${command_id}`);
          if (!resultRes.ok) throw new Error(`Помилка при отриманні результату з сервера ${serverId}`);

          const data = await resultRes.json();
          if (data.status !== "no_result") {
            output.value += `=== ${serverId} ===\n${data.stdout || JSON.stringify(data)}\n\n----------------------\n`;
            break;
          }
          await new Promise(r => setTimeout(r, 1000));
        }
      }
    } catch (error) {
      alert(error.message);
    } finally {
      sendBtn.disabled = false;
      sendBtn.textContent = "Надіслати";
    }
  }

  window.sendCommand = sendCommand;

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
        updateToggleSelectButton();
      });

      list.appendChild(li);
    });

    updateToggleSelectButton();
  }

  // Select/Deselect all toggle button
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

    updateToggleSelectButton();
  });

  function updateToggleSelectButton() {
    const listItems = document.querySelectorAll('#server-list li');
    const allSelected = [...listItems].every(li => li.classList.contains('selected'));
    toggleSelectBtn.textContent = allSelected ? "Скасувати вибір" : "Вибрати всі";
  }

  // Clear button
  const output = document.getElementById("command-output");
  const clearBtn = document.getElementById("clear-btn");
  clearBtn.addEventListener("click", () => {
    output.value = "";
  });

  //-----------------------Checking active class---------------------------//

  const currentPath = window.location.pathname.replace(/\/$/, "");

  document.querySelectorAll('.main-nav .nav-item').forEach(item => {
    const link = item.querySelector('a');
    if (!link) return;

    const href = link.getAttribute('href').replace(/\/$/, "");
    if (href === currentPath) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  //------------------------------Hamburger menu---------------------------------//

  const menuToggle = document.querySelector('.menu-toggle');
  const mainNav = document.querySelector('.main-nav');

  if (menuToggle && mainNav) {
    menuToggle.addEventListener('click', () => {
      mainNav.classList.toggle('open');
      menuToggle.classList.toggle('open');

      const isOpen = mainNav.classList.contains('open');
      menuToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
  }

  loadServers();
});
