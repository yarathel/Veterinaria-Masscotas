// admin_vets.js
// Requiere: que el usuario esté autenticado y sea admin.
// Este fichero usa fetch() con mismas credenciales (same-origin).

document.addEventListener('DOMContentLoaded', () => {
  const tableBody = document.querySelector('#vets-table tbody');
  const btnRefresh = document.getElementById('btn-refresh');
  const btnOpenAdd = document.getElementById('btn-open-add');
  const addModal = document.getElementById('add-modal');
  const addForm = document.getElementById('add-form');
  const btnCancelAdd = document.getElementById('btn-cancel-add');

  const confirmModal = document.getElementById('confirm-modal');
  const confirmInput = document.getElementById('confirm-input');
  const btnDoDelete = document.getElementById('btn-do-delete');
  const btnCancelConfirm = document.getElementById('btn-cancel-confirm');

  let selectedDeleteId = null;

  async function loadVets() {
    tableBody.innerHTML = '<tr><td colspan="6" class="muted">Cargando...</td></tr>';
    try {
      const res = await fetch('/admin/veterinarios/lista', { credentials: 'same-origin' });
      if (!res.ok) throw new Error('Error al cargar veterinarios');
      const data = await res.json();
      renderTable(data);
    } catch (err) {
      tableBody.innerHTML = `<tr><td colspan="6" class="muted">Error al cargar: ${err.message}</td></tr>`;
    }
  }

  function renderTable(data) {
    if (!data || data.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="6" class="muted">No hay veterinarios registrados.</td></tr>';
      return;
    }
    tableBody.innerHTML = '';
    data.forEach(row => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${row.id}</td>
        <td>${escapeHtml(row.nombre||'')}</td>
        <td>${escapeHtml(row.telefono||'')}</td>
        <td>${escapeHtml(row.especialidad||'')}</td>
        <td>${escapeHtml(row.correo||'')}</td>
        <td>
          <button class="btn btn-del" data-id="${row.id}">Eliminar</button>
        </td>
      `;
      tableBody.appendChild(tr);
    });

    // attach delete handlers
    document.querySelectorAll('.btn-del').forEach(b => {
      b.addEventListener('click', (e) => {
        selectedDeleteId = e.currentTarget.dataset.id;
        openConfirmModal();
      });
    });
  }

  function escapeHtml(unsafe) {
    return String(unsafe)
      .replaceAll('&','&amp;')
      .replaceAll('<','&lt;')
      .replaceAll('>','&gt;')
      .replaceAll('"','&quot;')
      .replaceAll("'","&#039;");
  }

  // Add modal controls
  btnOpenAdd.addEventListener('click', () => openAddModal());
  btnCancelAdd.addEventListener('click', () => closeAddModal());

  addForm.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const fd = new FormData(addForm);
    try {
      const res = await fetch('/admin/veterinarios/agregar', {
        method: 'POST',
        body: fd,
        credentials: 'same-origin'
      });
      if (!res.ok) {
        const text = await res.text();
        alert('Error al agregar: ' + text);
        return;
      }
      closeAddModal();
      await loadVets();
    } catch (err) {
      alert('Error de red: ' + err.message);
    }
  });

  function openAddModal() {
    addModal.classList.remove('hidden');
  }
  function closeAddModal() {
    addModal.classList.add('hidden');
    addForm.reset();
  }

  // Confirm delete
  function openConfirmModal() {
    confirmModal.classList.remove('hidden');
    confirmInput.value = '';
    btnDoDelete.disabled = true;
    confirmInput.focus();
  }
  function closeConfirmModal() {
    confirmModal.classList.add('hidden');
    selectedDeleteId = null;
    confirmInput.value = '';
    btnDoDelete.disabled = true;
  }

  confirmInput.addEventListener('input', (e) => {
    btnDoDelete.disabled = e.target.value.trim() !== 'CONFIRMAR';
  });

  btnCancelConfirm.addEventListener('click', () => closeConfirmModal());

  btnDoDelete.addEventListener('click', async () => {
    if (!selectedDeleteId) return;
    try {
      const res = await fetch(`/admin/veterinarios/eliminar/${selectedDeleteId}`, {
        method: 'DELETE',
        credentials: 'same-origin'
      });
      if (!res.ok) {
        const text = await res.text();
        alert('No se pudo eliminar: ' + text);
        closeConfirmModal();
        return;
      }
      closeConfirmModal();
      await loadVets();
    } catch (err) {
      alert('Error de red: ' + err.message);
      closeConfirmModal();
    }
  });

  btnRefresh.addEventListener('click', () => loadVets());

  // close modals on outside click (optional)
  window.addEventListener('click', (ev) => {
    if (ev.target === addModal) closeAddModal();
    if (ev.target === confirmModal) closeConfirmModal();
  });

  // inicial
  loadVets();
});
