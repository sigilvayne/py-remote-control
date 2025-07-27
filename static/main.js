document.addEventListener("DOMContentLoaded", () => {
  const selectedServers = new Set();
  const outputWindows = new Map(); // Для збереження output windows по command_id
  let commandCounter = 0; // Counter для унікальних ID команд

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

   // ------------------Add tooltips from data-desc------------------ //
  document.querySelectorAll('#command-list li[data-desc]').forEach(li => {
  const desc = li.getAttribute('data-desc');
  if (desc) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip-text';
    tooltip.textContent = desc;
    li.style.position = 'relative';
    li.appendChild(tooltip);
  }
});

  //-----------------------Send command---------------------------//

  async function sendCommand() {
    const commandInput = document.getElementById('command-input');
    const command = commandInput.value.trim();
  
    let isComplex = false;
    const commandListItems = document.querySelectorAll('#command-list .nested-list li');
    commandListItems.forEach(item => {
      if (item.classList.contains('selected') || item === document.activeElement) {
        if (item.dataset.complex === 'true') isComplex = true;
      }
      if (item.dataset && item.dataset.script && command.includes(item.dataset.script) && item.dataset.complex === 'true') {
        isComplex = true;
      }
    });
  
    if (selectedServers.size === 0 || !command) {
      alert("Оберіть хоча б один сервер та введіть команду.");
      return;
    }
  
    // Start command execution in background without blocking the UI
    executeCommandInBackground(command, selectedServers, isComplex);
  }

  // Function to create a new output window
  function createOutputWindow(command, serverId, commandId) {
    const outputContainer = document.getElementById('output-container');
    const windowId = `output-${commandCounter++}`;
    
    const outputWindow = document.createElement('div');
    outputWindow.className = 'output-window';
    outputWindow.id = windowId;
    
    const header = document.createElement('div');
    header.className = 'output-header';
    
    const title = document.createElement('div');
    title.className = 'output-title';
    title.textContent = `${serverId} - ${command.substring(0, 30)}${command.length > 30 ? '...' : ''}`;
    
    const status = document.createElement('span');
    status.className = 'output-status running';
    status.textContent = 'Running';
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'output-close';
    closeBtn.innerHTML = '×';
    closeBtn.onclick = () => {
      outputWindow.remove();
      outputWindows.delete(commandId);
    };
    
    header.appendChild(title);
    header.appendChild(status);
    header.appendChild(closeBtn);
    
    const content = document.createElement('textarea');
    content.className = 'output-content';
    content.placeholder = 'Waiting for output...';
    content.readOnly = true;
    
    outputWindow.appendChild(header);
    outputWindow.appendChild(content);
    outputContainer.appendChild(outputWindow);
    
    // Store reference to the window
    outputWindows.set(commandId, {
      window: outputWindow,
      content: content,
      status: status,
      serverId: serverId
    });
    
    return windowId;
  }

  // Function to update output window content
  function updateOutputWindow(commandId, content, status = null) {
    const windowData = outputWindows.get(commandId);
    if (windowData) {
      windowData.content.value = content;
      if (status) {
        windowData.status.textContent = status;
        windowData.status.className = `output-status ${status.toLowerCase()}`;
      }
    }
  }

  // New function to handle command execution in background
  async function executeCommandInBackground(command, servers, isComplex) {
    try {
      for (const serverId of servers) {
        const res = await fetch(`/set_command/${serverId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ command })
        });
        if (!res.ok) throw new Error(`Помилка при надсиланні команди на сервер ${serverId}`);
  
        const { command_id } = await res.json();
        
        // Create output window for this command
        createOutputWindow(command, serverId, command_id);
        
        // Start monitoring the command result
        monitorCommandResult(serverId, command_id, isComplex);
      }
    } catch (error) {
      alert(error.message);
    }
  }

  // Function to monitor command result
  async function monitorCommandResult(serverId, commandId, isComplex) {
    let tries = isComplex ? Infinity : 30;
    let output = '';
    
    while (tries-- > 0) {
      try {
        const resultRes = await fetch(`/get_result/${serverId}?command_id=${commandId}`);
        if (!resultRes.ok) throw new Error(`Помилка при отриманні результату з сервера ${serverId}`);
  
        const data = await resultRes.json();
        if (data.status !== "no_result") {
          output = data.stdout || JSON.stringify(data);
          updateOutputWindow(commandId, output, 'completed');
          break;
        }
        
        await new Promise(r => setTimeout(r, 1000));
      } catch (error) {
        updateOutputWindow(commandId, `Error: ${error.message}`, 'error');
        break;
      }
    }
  
    if (tries <= 0 && !isComplex) {
      updateOutputWindow(commandId, 'Команда не повернула результат протягом 30 секунд.', 'error');
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
      // Clear all output windows
      const outputContainer = document.getElementById('output-container');
      outputContainer.innerHTML = '';
      outputWindows.clear();
      commandCounter = 0;
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
