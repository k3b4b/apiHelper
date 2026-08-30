// ---- TomSelect ----
new TomSelect('#api-key-select', {
    create: false,
    sortField: {
        field: "text",
        direction: "asc"
    }
});

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
    if (headers.length) rows.push(headers.join("\t"));

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
