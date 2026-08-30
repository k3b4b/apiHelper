// ---- TomSelect ----
const apiKeySelectControl = new TomSelect('#api-key-select', {
    create: false,
    sortField: {
        field: "text",
        direction: "asc"
    }
});

const FAVORITE_API_KEYS_STORAGE = "favoriteApiKeys";

function getFavoriteApiKeys() {
    try {
        const favorites = JSON.parse(localStorage.getItem(FAVORITE_API_KEYS_STORAGE) || "[]");
        return Array.isArray(favorites) ? favorites : [];
    } catch (err) {
        console.error("Не удалось прочитать избранные API-ключи", err);
        return [];
    }
}

function saveFavoriteApiKeys(favorites) {
    localStorage.setItem(FAVORITE_API_KEYS_STORAGE, JSON.stringify(favorites));
}

function updateFavoriteToggle() {
    const button = document.getElementById("favorite-toggle-btn");
    const keyId = document.getElementById("api-key-select").value;
    const isFavorite = getFavoriteApiKeys().some(item => item.id === keyId);

    button.disabled = !keyId;
    button.textContent = isFavorite ? "★" : "☆";
    button.title = isFavorite ? "Удалить из избранного" : "Добавить в избранное";
    button.setAttribute("aria-label", button.title);
}

function renderFavoriteApiKeys() {
    const list = document.getElementById("favorite-api-key-list");
    const favorites = getFavoriteApiKeys().filter(item => apiKeySelectControl.options[item.id]);

    saveFavoriteApiKeys(favorites);
    list.innerHTML = "";

    if (!favorites.length) {
        const emptyState = document.createElement("span");
        emptyState.className = "favorites-empty";
        emptyState.textContent = "Здесь пока нет избранных ключей";
        list.appendChild(emptyState);
        return;
    }

    favorites.forEach(favorite => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "favorite-api-key-btn";
        if (favorite.id === document.getElementById("api-key-select").value) {
            button.classList.add("active");
        }
        button.textContent = favorite.name;
        button.addEventListener("click", () => apiKeySelectControl.setValue(favorite.id));
        list.appendChild(button);
    });
}

document.getElementById("favorite-toggle-btn").addEventListener("click", () => {
    const select = document.getElementById("api-key-select");
    const keyId = select.value;
    if (!keyId) return;

    const keyName = select.options[select.selectedIndex]?.textContent.trim() || keyId;
    const favorites = getFavoriteApiKeys();
    const favoriteIndex = favorites.findIndex(item => item.id === keyId);

    if (favoriteIndex >= 0) {
        favorites.splice(favoriteIndex, 1);
    } else {
        favorites.push({ id: keyId, name: keyName });
    }

    saveFavoriteApiKeys(favorites);
    renderFavoriteApiKeys();
    updateFavoriteToggle();
});

function setKeyEditMode(enabled) {
    const panel = document.getElementById("select_api_key");
    const controls = document.getElementById("key-edit-controls");
    const input = document.getElementById("key-name-input");
    const keyId = document.getElementById("api-key-select").value;

    panel.classList.toggle("editing-key", enabled);
    controls.hidden = !enabled;
    if (enabled && keyId) {
        input.value = document.getElementById("api-key-select").options[
            document.getElementById("api-key-select").selectedIndex
        ]?.textContent.trim() || "";
        input.focus();
        input.select();
    }
}

document.getElementById("edit-api-key-btn").addEventListener("click", () => {
    setKeyEditMode(!document.getElementById("select_api_key").classList.contains("editing-key"));
});

document.getElementById("save-key-name-btn").addEventListener("click", async () => {
    const keyId = document.getElementById("api-key-select").value;
    const input = document.getElementById("key-name-input");
    const description = input.value.trim();
    if (!keyId || !description) {
        alert("Введите название ключа");
        return;
    }

    try {
        const response = await fetch(`/api/update_api_key/${keyId}`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({ description }),
        });
        if (!response.ok) throw new Error((await response.json()).detail || "Не удалось сохранить название");

        apiKeySelectControl.updateOption(keyId, { value: keyId, text: description });
        const favorites = getFavoriteApiKeys().map(item =>
            item.id === keyId ? { ...item, name: description } : item
        );
        saveFavoriteApiKeys(favorites);
        renderFavoriteApiKeys();
        setKeyEditMode(false);
    } catch (err) {
        console.error(err);
        alert(err.message);
    }
});

document.getElementById("delete-api-key-btn").addEventListener("click", async () => {
    const keyId = document.getElementById("api-key-select").value;
    const keyName = getSelectedKeyName();
    if (!keyId || !confirm(`Удалить API-ключ «${keyName}» полностью?`)) return;

    try {
        const response = await fetch(`/api/delete_api_key/${keyId}`, { method: "DELETE" });
        if (!response.ok) throw new Error((await response.json()).detail || "Не удалось удалить API-ключ");
        window.location.reload();
    } catch (err) {
        console.error(err);
        alert(err.message);
    }
});

apiKeySelectControl.on("change", keyId => {
    updateFavoriteToggle();
    renderFavoriteApiKeys();
    document.getElementById("edit-api-key-btn").disabled = !keyId;
    setKeyEditMode(false);
    if (keyId) loadOrganizations(keyId);
});

renderFavoriteApiKeys();
updateFavoriteToggle();

// ---- Организации ----
async function loadOrganizations(keyId) {
    if (!keyId) {
        console.log("API key is empty");
        return;
    }

    const response = await fetch(`/api/get_organizations/${keyId}`);
    if (!response.ok) {
        alert("Ошибка при получении организаций");
        return;
    }

    const data = await response.json();
    const tbody = document.querySelector("#org-table tbody");

    document.getElementById("tabs-container").style.display = "none";
    const detailsTable = document.getElementById("details-table");
    detailsTable.style.display = "none";
    detailsTable.dataset.orgId = "";

    tbody.innerHTML = "";

    data.forEach(org => {
        const tr = document.createElement("tr");
        tr.dataset.orgId = org.internal_id;

        tr.innerHTML = `
            <td>${org.id}</td>
            <td>${org.name}</td>
            <td class="center-col"><button onclick="selectOrganization(this)">Выбрать</button></td>
        `;

        tbody.appendChild(tr);
    });
}

function selectOrganization(button) {
    const tr = button.closest("tr");
    const orgId = parseInt(tr.dataset.orgId, 10);

    document.querySelectorAll("#org-table tbody tr").forEach(r => r.classList.remove("selected-row"));
    tr.classList.add("selected-row");

    const tabsContainer = document.getElementById("tabs-container");
    tabsContainer.style.display = "flex";

    const detailsTable = document.getElementById("details-table");
    detailsTable.style.display = "table";
    detailsTable.dataset.orgId = orgId;

    detailsTable.querySelector("thead tr").innerHTML = "";
    detailsTable.querySelector("tbody").innerHTML = "";
}

function getDetailsTableText() {
    const detailsTable = document.getElementById("details-table");
    const headers = Array.from(detailsTable.querySelectorAll("thead th"))
        .slice(1)
        .map(cell => cell.textContent.trim());
    const rows = [headers];

    detailsTable.querySelectorAll("tbody tr").forEach(row => {
        const values = Array.from(row.querySelectorAll("td"))
            .slice(1)
            .map(cell => cell.textContent.trim().replace(/[\t\r\n]+/g, " "));
        rows.push(values);
    });

    if (!headers.length) return "";

    const columnWidths = headers.map((_, columnIndex) =>
        Math.max(...rows.map(row => (row[columnIndex] || "").length))
    );

    return rows
        .map(row => row
            .map((value, columnIndex) =>
                columnIndex === row.length - 1
                    ? value
                    : value.padEnd(columnWidths[columnIndex] + 2, " ")
            )
            .join("")
            .trimEnd()
        )
        .join("\r\n");
}

function getSelectedKeyName() {
    const keySelect = document.getElementById("api-key-select");
    return keySelect.options[keySelect.selectedIndex]?.textContent.trim() || "api-key";
}

function sanitizeFileName(fileName) {
    return fileName
        .replace(/[<>:\"/\\|?*\x00-\x1F]/g, "_")
        .replace(/[. ]+$/g, "") || "api-key";
}

async function copyDetailsRow(button) {
    const cells = Array.from(button.closest("tr").querySelectorAll("td")).slice(1);
    const text = cells.map(cell => cell.textContent.trim()).join("\t");

    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
        } else {
            const textarea = document.createElement("textarea");
            textarea.value = text;
            textarea.style.position = "fixed";
            textarea.style.opacity = "0";
            document.body.appendChild(textarea);
            textarea.select();
            const copied = document.execCommand("copy");
            textarea.remove();
            if (!copied) throw new Error("Copy command was rejected");
        }
        const originalText = button.textContent;
        button.textContent = "✓";
        button.title = "Строка скопирована";
        setTimeout(() => {
            button.textContent = originalText;
            button.title = "Копировать строку";
        }, 1200);
    } catch (err) {
        console.error(err);
        alert("Не удалось скопировать строку");
    }
}

document.getElementById("download-details-btn").addEventListener("click", () => {
    const text = getDetailsTableText();
    if (!text) {
        alert("Таблица пуста");
        return;
    }

    const detailsTable = document.getElementById("details-table");
    const tableName = detailsTable.dataset.tableName || "Таблица";
    const safeFileName = sanitizeFileName(`${tableName} ${getSelectedKeyName()}`);
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = `${safeFileName}.txt`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
});

// ---- Кнопка "Обновить всё" ----
document.getElementById("refresh-all-btn").addEventListener("click", () => {
    const detailsTable = document.getElementById("details-table");
    const orgId = parseInt(detailsTable.dataset.orgId, 10);

    const keyId = document.getElementById("api-key-select").value;

    if (!keyId || !orgId) {
        alert("Выберите ключ и организацию");
        return;
    }

    refreshAll(keyId, orgId, document.getElementById("refresh-all-btn"));
});



// ---- Вкладки ----
document.querySelectorAll(".tab-button").forEach(btn => {
    btn.addEventListener("click", async () => {
        const orgId = parseInt(document.getElementById("details-table").dataset.orgId, 10);
        const type = btn.dataset.type;

        const detailsTable = document.getElementById("details-table");
        detailsTable.dataset.tableName = btn.textContent.trim();
        const thead = detailsTable.querySelector("thead tr");
        const tbody = detailsTable.querySelector("tbody");

        tbody.innerHTML = "";
        thead.innerHTML = "";

        document.querySelectorAll(".tab-button").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        try {
            let response;
            let data;

            if (type === "terminals") {
                response = await fetch(`/api/get_terminals/${orgId}`, { method: "POST" });
                thead.innerHTML = '<th class="copy-column" aria-label="Копирование"></th><th>ID</th><th>Название</th>';
            } else if (type === "payment_types") {
                response = await fetch(`/api/get_payment_types/${orgId}`, { method: "POST" });
                thead.innerHTML = '<th class="copy-column" aria-label="Копирование"></th><th>ID</th><th>Название</th><th>Вид</th><th>Код</th>';
            } else if (type === "order_types") {
                response = await fetch(`/api/get_order_types/${orgId}`, { method: "POST" });
                thead.innerHTML = '<th class="copy-column" aria-label="Копирование"></th><th>ID</th><th>Название</th><th>Тип</th>';
            } else if (type === "discounts") {
                response = await fetch(`/api/get_discount_types/${orgId}`, { method: "POST" });
                thead.innerHTML = '<th class="copy-column" aria-label="Копирование"></th><th>ID</th><th>Название</th>';
            }

            if (!response.ok) throw new Error("Ошибка загрузки данных");

            data = await response.json();

            data.forEach(item => {
                const tr = document.createElement("tr");
                const copyCell = document.createElement("td");
                const copyButton = document.createElement("button");

                copyCell.className = "copy-column";
                copyButton.type = "button";
                copyButton.className = "copy-row-btn";
                copyButton.textContent = "⧉";
                copyButton.title = "Копировать строку";
                copyButton.setAttribute("aria-label", "Копировать строку");
                copyButton.addEventListener("click", () => copyDetailsRow(copyButton));
                copyCell.appendChild(copyButton);
                tr.appendChild(copyCell);

                Object.values(item).forEach(value => {
                    const cell = document.createElement("td");
                    cell.textContent = value ?? "";
                    tr.appendChild(cell);
                });
                tbody.appendChild(tr);
            });

        } catch (err) {
            alert(err.message);
            console.error(err);
        }
    });
});

// ---- Скачать номенклатуру ----
document.getElementById("download-nomenclature-btn").addEventListener("click", async () => {
    const keyId = document.getElementById("api-key-select").value;
    const detailsTable = document.getElementById("details-table");
    const orgId = parseInt(detailsTable.dataset.orgId, 10);

    if (!keyId || !orgId) {
        alert("Выберите ключ и организацию");
        return;
    }

    try {
        const response = await fetch(`/api/get/nomenclature/${keyId}/${orgId}`);
        if (!response.ok) throw new Error("Ошибка при получении файла");

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = `${sanitizeFileName(`Номенклатура ${getSelectedKeyName()}`)}.txt`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

    } catch (err) {
        console.error(err);
        alert(err.message);
    }
});

// ---- Тема ----
document.getElementById("theme-toggle").addEventListener("click", () => {
    const body = document.body;
    const isDark = body.dataset.theme === "dark";

    body.dataset.theme = isDark ? "light" : "dark";
    localStorage.setItem("theme", body.dataset.theme);

    document.getElementById("theme-toggle").textContent =
        isDark ? "🌙 Тёмная тема" : "☀️ Светлая тема";
});

window.addEventListener("load", () => {
    const saved = localStorage.getItem("theme") || "light";
    document.body.dataset.theme = saved;
    document.getElementById("theme-toggle").textContent =
        saved === "dark" ? "☀️ Светлая тема" : "🌙 Тёмная тема";
});

// ---- Автозагрузка ----
document.addEventListener("DOMContentLoaded", () => {
    const keySelect = document.getElementById("api-key-select");
    if (keySelect.value) {
        loadOrganizations(keySelect.value);
    }
});
