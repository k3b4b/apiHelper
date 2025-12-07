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
                thead.innerHTML = "<th>ID</th><th>Название</th>";
            } else if (type === "payment_types") {
                response = await fetch(`/api/get_payment_types/${orgId}`, { method: "POST" });
                thead.innerHTML = "<th>ID</th><th>Название</th><th>Вид</th><th>Код</th>";
            } else if (type === "order_types") {
                response = await fetch(`/api/get_order_types/${orgId}`, { method: "POST" });
                thead.innerHTML = "<th>ID</th><th>Название</th><th>Тип</th>";
            } else if (type === "discounts") {
                response = await fetch(`/api/get_discount_types/${orgId}`, { method: "POST" });
                thead.innerHTML = "<th>ID</th><th>Название</th>";
            }

            if (!response.ok) throw new Error("Ошибка загрузки данных");

            data = await response.json();

            data.forEach(item => {
                const tr = document.createElement("tr");
                tr.innerHTML = Object.values(item).map(v => `<td>${v}</td>`).join("");
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
        a.download = "nomenclature.txt";
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
