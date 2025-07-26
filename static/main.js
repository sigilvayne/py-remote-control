document.addEventListener("DOMContentLoaded", () => {
  const selectedServers = new Set();
  let panelCounter = 0;

  //-----------------------Folder toggling---------------------------//
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

  //-----------------------Commands click handling---------------------------//
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

  //-----------------------Dynamic Output Panels Management---------------------------//
  
  function createOutputPanel(serverId, command) {
    const container = document.getElementById('output-panels-container');
    const panelId = `panel-${++panelCounter}`;
    
    const panel = document.createElement('div');
    panel.className = 'output-panel';
    panel.id = panelId;
    
    const header = document.createElement('div');
    header.className = 'output-panel-header';
    
    const title = document.createElement('div');
    title.className = 'output-panel-title';
    title.textContent = `${serverId} - ${command.substring(0, 30)}${command.length > 30 ? '...' : ''}`;
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'output-panel-close';
    closeBtn.innerHTML = '×';
    closeBtn.onclick = () => removeOutputPanel(panelId);
    
    const content = document.createElement('div');
    content.className = 'output-panel-content';
    content.textContent = 'Очікування відповіді...';
    
    const status = document.createElement('div');
    status.className = 'output-panel-status running';
    status.textContent = 'Виконується...';
    
    header.appendChild(title);
    header.appendChild(closeBtn);
    panel.appendChild(header);
    panel.appendChild(content);
    panel.appendChild(status);
    container.appendChild(panel);
    
    return { panelId, content, status };
  }
  
  function updateOutputPanel(panelId, content, status = 'success') {
    const panel = document.getElementById(panelId);
    if (!panel) return;
    
    const contentEl = panel.querySelector('.output-panel-content');
    const statusEl = panel.querySelector('.output-panel-status');
    
    if (contentEl) contentEl.textContent = content;
    if (statusEl) {
      statusEl.textContent = status === 'success' ? 'Завершено' : 
                           status === 'error' ? 'Помилка' : 'Виконується...';
      statusEl.className = `output-panel-status ${status}`;
    }
  }
  
  function removeOutputPanel(panelId) {
    const panel = document.getElementById(panelId);
    if (panel) {
      panel.remove();
    }
  }

  //-----------------------Send command---------------------------//
  async function sendCommand() {
    const commandInput = document.getElementById('command-input');
    const command = commandInput.value.trim();

    // Detect if the selected command is complex
    let isComplex = false;
    const commandListItems = document.querySelectorAll('#command-list .nested-list li');
    commandListItems.forEach(item => {
      if (item.classList.contains('selected') || item === document.activeElement) {
        if (item.dataset.complex === 'true') isComplex = true;
      }
      // fallback: check if commandInput matches this script
      if (item.dataset && item.dataset.script && command.includes(item.dataset.script) && item.dataset.complex === 'true') {
        isComplex = true;
      }
    });

    if (selectedServers.size === 0 || !command) {
      alert("Оберіть хоча б один сервер та введіть команду.");
      return;
    }

    try {
      for (const serverId of selectedServers) {
        const { panelId, content, status } = createOutputPanel(serverId, command);
        
        const res = await fetch(`/set_command/${serverId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ command })
        });
        
        if (!res.ok) {
          updateOutputPanel(panelId, `Помилка при надсиланні команди: ${res.statusText}`, 'error');
          continue;
        }

        const { command_id } = await res.json();

        if (isComplex) {
          updateOutputPanel(panelId, 'Команду надіслано успішно (комплексна команда)', 'success');
          continue;
        }

        let tries = 30;
        while (tries-- > 0) {
          const resultRes = await fetch(`/get_result/${serverId}?command_id=${command_id}`);
          if (!resultRes.ok) {
            updateOutputPanel(panelId, `Помилка при отриманні результату: ${resultRes.statusText}`, 'error');
            break;
          }

          const data = await resultRes.json();
          if (data.status !== "no_result") {
            const output = data.stdout || JSON.stringify(data);
            updateOutputPanel(panelId, output, 'success');
            break;
          }
          
          updateOutputPanel(panelId, `Очікування... (${30 - tries}/30)`, 'running');
          await new Promise(r => setTimeout(r, 1000));
        }
        
        if (tries < 0) {
          updateOutputPanel(panelId, 'Час очікування вичерпано', 'error');
        }
      }
    } catch (error) {
      alert(error.message);
    }
  }

  window.sendCommand = sendCommand;

  //-----------------------Load servers---------------------------//
  async function loadServers() {
    const res = await fetch('/servers');
    const servers = await res.json();
    const list = document.getElementById('server-list');
    const emptyText = document.getElementById('empty-server-text');
    const toggleSelectBtn = document.getElementById('toggle-select-all');

    list.innerHTML = '';

    if (servers.length === 0) {
      emptyText.style.display = 'block';
      if (toggleSelectBtn) toggleSelectBtn.style.display = 'none';
    } else {
      emptyText.style.display = 'none';
      if (toggleSelectBtn) toggleSelectBtn.style.display = 'inline-block';

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
    }

    updateToggleSelectButton();
  }

  // Select/Deselect all toggle button
  const toggleSelectBtn = document.getElementById('toggle-select-all');
  if (toggleSelectBtn) {
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
  }

  function updateToggleSelectButton() {
    const listItems = document.querySelectorAll('#server-list li');
    const allSelected = [...listItems].every(li => li.classList.contains('selected'));
    if (toggleSelectBtn) {
      toggleSelectBtn.textContent = allSelected ? "Скасувати вибір" : "Вибрати всі";
    }
  }

  //-----------------------Clear output button---------------------------//
  const clearBtn = document.getElementById("clear-btn");
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      const container = document.getElementById('output-panels-container');
      container.innerHTML = '';
      panelCounter = 0;
    });
  }

  //-----------------------Navigation active class---------------------------//
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
