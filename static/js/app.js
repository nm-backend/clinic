const API = '/api';

async function apiRequest(method, path, body = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' },
    };
    if (body) {
        options.body = JSON.stringify(body);
    }
    const response = await fetch(API + path, options);
    let data = null;
    if (response.status === 204) {
        data = { detail: 'Успешно (204 No Content)' };
    } else {
        data = await response.json();
    }
    return { ok: response.ok, status: response.status, data };
}

function showOutput(elementId, result) {
    const el = document.getElementById(elementId);
    // API отдаёт serializer.data напрямую — без обёртки {success, data}
    el.textContent = JSON.stringify(result.data, null, 2);
    el.classList.remove('error', 'success');
    el.classList.add(result.ok ? 'success' : 'error');
}

function buildQuery(params) {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
            qs.set(key, value);
        }
    });
    const str = qs.toString();
    return str ? '?' + str : '';
}

document.getElementById('btn-load-clinics').addEventListener('click', async () => {
    const result = await apiRequest('GET', '/clinics/');
    showOutput('out-clinics', result);
});

document.getElementById('btn-load-doctors').addEventListener('click', async () => {
    const clinicId = document.getElementById('filter-clinic-id').value;
    const specialty = document.getElementById('filter-specialty').value;
    const query = buildQuery({ clinic_id: clinicId, specialty });
    const result = await apiRequest('GET', '/doctors/' + query);
    showOutput('out-doctors', result);
});

document.getElementById('btn-load-services').addEventListener('click', async () => {
    const clinicId = document.getElementById('filter-service-clinic').value;
    const query = buildQuery({ clinic_id: clinicId });
    const result = await apiRequest('GET', '/services/' + query);
    showOutput('out-services', result);
});

document.getElementById('form-appointment').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const scheduledLocal = form.scheduled_at.value;
    const scheduledAt = new Date(scheduledLocal).toISOString();

    const body = {
        patient_first_name: form.patient_first_name.value,
        patient_last_name: form.patient_last_name.value,
        patient_phone: form.patient_phone.value,
        patient_email: form.patient_email.value,
        doctor_id: Number(form.doctor_id.value),
        service_id: Number(form.service_id.value),
        scheduled_at: scheduledAt,
        notes: form.notes.value,
    };

    const result = await apiRequest('POST', '/appointments/', body);
    showOutput('out-create', result);
});

document.getElementById('btn-load-appointments').addEventListener('click', async () => {
    const phone = document.getElementById('search-phone').value;
    const query = buildQuery({ patient_phone: phone });
    const result = await apiRequest('GET', '/appointments/' + query);
    showOutput('out-appointments', result);
});

document.getElementById('btn-get-appointment').addEventListener('click', async () => {
    const id = document.getElementById('appointment-id').value;
    if (!id) return;
    const result = await apiRequest('GET', '/appointments/' + id + '/');
    showOutput('out-manage', result);
});

document.getElementById('btn-cancel-appointment').addEventListener('click', async () => {
    const id = document.getElementById('appointment-id').value;
    if (!id) return;
    const result = await apiRequest('DELETE', '/appointments/' + id + '/');
    showOutput('out-manage', result);
});

document.getElementById('form-update').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('appointment-id').value;
    if (!id) return;

    const form = e.target;
    const body = {};

    if (form.doctor_id.value) body.doctor_id = Number(form.doctor_id.value);
    if (form.service_id.value) body.service_id = Number(form.service_id.value);
    if (form.scheduled_at.value) {
        body.scheduled_at = new Date(form.scheduled_at.value).toISOString();
    }
    if (form.status.value) body.status = form.status.value;

    const result = await apiRequest('PATCH', '/appointments/' + id + '/', body);
    showOutput('out-manage', result);
});
