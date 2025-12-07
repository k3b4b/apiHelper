let isFetching = false;

function cooldownButton(button, seconds) {
    button.disabled = true;
    button.classList.add("cooldown");
    button.title = `Подождите ${seconds} секунд перед повторным запросом`;

    setTimeout(() => {
        button.disabled = false;
        button.classList.remove("cooldown");
        button.title = "";
    }, seconds * 1000);
}

async function updateOrganizations(keyId) {
    if (!keyId) return;

    const refreshBtn = document.querySelector(
        "button[onclick*='updateOrganizations']"
    );

    if (refreshBtn) {
        cooldownButton(refreshBtn, TIMEOUT_SECONDS);
    }

    try {
        const response = await fetch(`/api/update_organizations/${keyId}`);

        if (!response.ok) {
            alert("Ошибка при обновлении организаций");
            return;
        }

        const result = await response.json();
        console.log("Обновление организаций:", result.message || result.status);

        await loadOrganizations(keyId);
    } catch (err) {
        console.error(err);
        alert("Ошибка соединения при обновлении организаций");
    }
}

async function refreshAll(keyId, orgId, button) {
    if (isFetching) return;
    isFetching = true;

    if (button) cooldownButton(button, TIMEOUT_SECONDS);

    try {
        const response = await fetch(`/api/refresh_all/${keyId}/${orgId}`, {
            method: "POST"
        });

        if (!response.ok) {
            alert("Ошибка при обновлении данных");
            return;
        }

        const data = await response.json();
        alert("Данные успешно обновлены!");
        console.log(data);
    } catch (error) {
        console.error(error);
        alert("Произошла ошибка при запросе");
    } finally {
        isFetching = false;
    }
}

async function refreshEntity(keyId, orgId, entity, button) {
    if (isFetching) return;
    isFetching = true;
    if (button) cooldownButton(button, TIMEOUT_SECONDS);

    try {
        const response = await fetch(
            `/api/refresh_${entity}/${keyId}/${orgId}/`,
            { method: "POST" }
        );
        if (!response.ok) {
            alert(`Ошибка при обновлении ${entity}`);
            return;
        }
        const data = await response.json();
        alert(`${entity.charAt(0).toUpperCase() + entity.slice(1)} успешно обновлены!`);
        console.log(data);
    } catch (error) {
        console.error(error);
        alert("Произошла ошибка при запросе");
    } finally {
        isFetching = false;
    }
}