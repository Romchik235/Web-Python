from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import engine, get_db
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Стоматологічний кабінет",
    description="Інформаційна система управління стоматологічним кабінетом",
    version="1.0.0"
)

STYLE = """
<style>
  body { font-family: Arial, sans-serif; margin: 30px; background: #f5f9fc; }
  h1 { color: #1a5276; }
  h2 { color: #2874a6; }
  table { border-collapse: collapse; width: 100%; background: white; }
  th { background: #2874a6; color: white; padding: 8px 12px; }
  td { border: 1px solid #ccc; padding: 8px 12px; }
  tr:nth-child(even) { background: #eaf4fb; }
  a { color: #2874a6; text-decoration: none; margin: 0 4px; }
  a:hover { text-decoration: underline; }
  input, select, textarea { padding: 6px; width: 300px; margin: 4px 0; border: 1px solid #aaa; border-radius: 4px; }
  button, input[type=submit] { background: #2874a6; color: white; padding: 8px 20px; border: none; border-radius: 4px; cursor: pointer; }
  .nav { margin-bottom: 20px; }
  .nav a { background: #2874a6; color: white; padding: 6px 14px; border-radius: 4px; margin-right: 6px; }
  .badge-plan { color: #1a5276; background: #d6eaf8; padding: 2px 8px; border-radius: 8px; }
  .badge-done { color: #1e8449; background: #d5f5e3; padding: 2px 8px; border-radius: 8px; }
  .badge-cancel { color: #922b21; background: #fadbd8; padding: 2px 8px; border-radius: 8px; }
</style>
"""


def nav_bar(role: str) -> str:
    return f"""
    <div class='nav'>
      <a href='/?role={role}'>🏠 Головна</a>
      <a href='/doctors?role={role}'>👨‍⚕️ Лікарі</a>
      <a href='/patients?role={role}'>🧑‍🤝‍🧑 Пацієнти</a>
      <a href='/appointments?role={role}'>📅 Прийоми</a>
      <span style='float:right; color:#555'>Роль: <b>{role.upper()}</b></span>
    </div>
    <hr>
    """


# ============ HEAD PAGE ============

@app.get("/", response_class=HTMLResponse)
async def home(role: str = "user"):
    html = STYLE + nav_bar(role)
    html += "<h1>🦷 Стоматологічний кабінет (SQLite)</h1>"
    html += "<p>Ласкаво просимо до інформаційної системи управління стоматологічним кабінетом.</p>"
    html += "<ul>"
    html += f"<li><a href='/doctors?role={role}'>Переглянути лікарів</a></li>"
    html += f"<li><a href='/patients?role={role}'>Переглянути пацієнтів</a></li>"
    html += f"<li><a href='/appointments?role={role}'>Переглянути прийоми</a></li>"
    html += "</ul>"
    html += "<hr><p>Змінити роль: "
    html += "<a href='/?role=admin'>Адміністратор</a> | <a href='/?role=user'>Користувач</a></p>"
    return HTMLResponse(content=html)


# ============ DOCTORS ============

@app.get("/doctors", response_class=HTMLResponse)
async def list_doctors(role: str = "user", db: Session = Depends(get_db)):
    doctors = db.query(models.Doctor).all()
    html = STYLE + nav_bar(role)
    html += f"<h1>👨‍⚕️ Лікарі (Режим: {role.upper()})</h1>"
    html += "<table><tr><th>ID</th><th>Ім'я</th><th>Прізвище</th><th>Спеціалізація</th><th>Телефон</th>"
    if role == "admin":
        html += "<th>Дії</th>"
    html += "</tr>"
    for d in doctors:
        html += f"<tr><td>{d.id}</td><td>{d.name}</td><td>{d.surname}</td><td>{d.specialization}</td><td>{d.phone or '—'}</td>"
        if role == "admin":
            html += f"<td><a href='/doctors/{d.id}/edit?role=admin'>✏️ Редагувати</a> | <a href='/doctors/{d.id}/delete?role=admin' onclick=\"return confirm('Видалити лікаря?')\">🗑️ Видалити</a></td>"
        html += "</tr>"
    html += "</table><br>"
    if role == "admin":
        html += f"<a href='/doctors/add?role=admin'>➕ Додати лікаря</a>"
    return HTMLResponse(content=html)


@app.get("/doctors/add", response_class=HTMLResponse)
async def add_doctor_form(role: str = "admin"):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    html = STYLE + nav_bar(role)
    html += "<h1>➕ Додати лікаря</h1>"
    html += f"""<form method='post' action='/doctors?role=admin'>
        <label>Ім'я: <br><input name='name' required></label><br>
        <label>Прізвище: <br><input name='surname' required></label><br>
        <label>Спеціалізація: <br><input name='specialization' required></label><br>
        <label>Телефон: <br><input name='phone'></label><br><br>
        <input type='submit' value='Зберегти'>
    </form>
    <br><a href='/doctors?role=admin'>← Назад до списку</a>"""
    return HTMLResponse(content=html)


@app.post("/doctors", response_class=HTMLResponse)
async def create_doctor(
    name: str = Form(...), surname: str = Form(...),
    specialization: str = Form(...), phone: str = Form(""),
    role: str = "admin", db: Session = Depends(get_db)
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    doctor = models.Doctor(name=name, surname=surname, specialization=specialization, phone=phone)
    db.add(doctor)
    db.commit()
    return RedirectResponse(url=f"/doctors?role=admin", status_code=303)


@app.get("/doctors/{doctor_id}/edit", response_class=HTMLResponse)
async def edit_doctor_form(doctor_id: int, role: str = "admin", db: Session = Depends(get_db)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Лікаря не знайдено")
    html = STYLE + nav_bar(role)
    html += "<h1>✏️ Редагувати лікаря</h1>"
    html += f"""<form method='post' action='/doctors/{doctor_id}/edit?role=admin'>
        <label>Ім'я: <br><input name='name' value='{doctor.name}' required></label><br>
        <label>Прізвище: <br><input name='surname' value='{doctor.surname}' required></label><br>
        <label>Спеціалізація: <br><input name='specialization' value='{doctor.specialization}' required></label><br>
        <label>Телефон: <br><input name='phone' value='{doctor.phone or ""}'></label><br><br>
        <input type='submit' value='Зберегти зміни'>
    </form>
    <br><a href='/doctors?role=admin'>← Назад до списку</a>"""
    return HTMLResponse(content=html)


@app.post("/doctors/{doctor_id}/edit", response_class=HTMLResponse)
async def update_doctor(
    doctor_id: int,
    name: str = Form(...), surname: str = Form(...),
    specialization: str = Form(...), phone: str = Form(""),
    role: str = "admin", db: Session = Depends(get_db)
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Лікаря не знайдено")
    doctor.name = name
    doctor.surname = surname
    doctor.specialization = specialization
    doctor.phone = phone
    db.commit()
    return RedirectResponse(url=f"/doctors?role=admin", status_code=303)


@app.get("/doctors/{doctor_id}/delete")
async def delete_doctor(doctor_id: int, role: str = "admin", db: Session = Depends(get_db)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Лікаря не знайдено")
    db.delete(doctor)
    db.commit()
    return RedirectResponse(url=f"/doctors?role=admin", status_code=303)


# ============ PATIENTS ============

@app.get("/patients", response_class=HTMLResponse)
async def list_patients(role: str = "user", db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    html = STYLE + nav_bar(role)
    html += f"<h1>🧑 Пацієнти (Режим: {role.upper()})</h1>"
    html += "<table><tr><th>ID</th><th>Ім'я</th><th>Прізвище</th><th>Дата нар.</th><th>Телефон</th>"
    if role == "admin":
        html += "<th>Дії</th>"
    html += "</tr>"
    for p in patients:
        html += f"<tr><td>{p.id}</td><td>{p.name}</td><td>{p.surname}</td><td>{p.birth_date or '—'}</td><td>{p.phone or '—'}</td>"
        if role == "admin":
            html += f"<td><a href='/patients/{p.id}/edit?role=admin'>✏️</a> | <a href='/patients/{p.id}/delete?role=admin' onclick=\"return confirm('Видалити?')\">🗑️</a></td>"
        html += "</tr>"
    html += "</table><br>"
    if role == "admin":
        html += f"<a href='/patients/add?role=admin'>➕ Додати пацієнта</a>"
    return HTMLResponse(content=html)


@app.get("/patients/add", response_class=HTMLResponse)
async def add_patient_form(role: str = "admin"):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    html = STYLE + nav_bar(role)
    html += "<h1>➕ Додати пацієнта</h1>"
    html += f"""<form method='post' action='/patients?role=admin'>
        <label>Ім'я: <br><input name='name' required></label><br>
        <label>Прізвище: <br><input name='surname' required></label><br>
        <label>Дата народження (РРРР-ММ-ДД): <br><input name='birth_date' type='date'></label><br>
        <label>Телефон: <br><input name='phone'></label><br>
        <label>Адреса: <br><input name='address'></label><br><br>
        <input type='submit' value='Зберегти'>
    </form>
    <br><a href='/patients?role=admin'>← Назад до списку</a>"""
    return HTMLResponse(content=html)


@app.post("/patients")
async def create_patient(
    name: str = Form(...), surname: str = Form(...),
    birth_date: str = Form(""), phone: str = Form(""), address: str = Form(""),
    role: str = "admin", db: Session = Depends(get_db)
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    patient = models.Patient(name=name, surname=surname, birth_date=birth_date, phone=phone, address=address)
    db.add(patient)
    db.commit()
    return RedirectResponse(url=f"/patients?role=admin", status_code=303)


@app.get("/patients/{patient_id}/edit", response_class=HTMLResponse)
async def edit_patient_form(patient_id: int, role: str = "admin", db: Session = Depends(get_db)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    p = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Пацієнта не знайдено")
    html = STYLE + nav_bar(role)
    html += "<h1>✏️ Редагувати пацієнта</h1>"
    html += f"""<form method='post' action='/patients/{patient_id}/edit?role=admin'>
        <label>Ім'я: <br><input name='name' value='{p.name}' required></label><br>
        <label>Прізвище: <br><input name='surname' value='{p.surname}' required></label><br>
        <label>Дата народження: <br><input name='birth_date' type='date' value='{p.birth_date or ""}'></label><br>
        <label>Телефон: <br><input name='phone' value='{p.phone or ""}'></label><br>
        <label>Адреса: <br><input name='address' value='{p.address or ""}'></label><br><br>
        <input type='submit' value='Зберегти зміни'>
    </form>
    <br><a href='/patients?role=admin'>← Назад до списку</a>"""
    return HTMLResponse(content=html)


@app.post("/patients/{patient_id}/edit")
async def update_patient(
    patient_id: int,
    name: str = Form(...), surname: str = Form(...),
    birth_date: str = Form(""), phone: str = Form(""), address: str = Form(""),
    role: str = "admin", db: Session = Depends(get_db)
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    p = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Пацієнта не знайдено")
    p.name = name; p.surname = surname; p.birth_date = birth_date
    p.phone = phone; p.address = address
    db.commit()
    return RedirectResponse(url=f"/patients?role=admin", status_code=303)


@app.get("/patients/{patient_id}/delete")
async def delete_patient(patient_id: int, role: str = "admin", db: Session = Depends(get_db)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    p = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Пацієнта не знайдено")
    db.delete(p)
    db.commit()
    return RedirectResponse(url=f"/patients?role=admin", status_code=303)


# ============ APPOINTMENTS ============

@app.get("/appointments", response_class=HTMLResponse)
async def list_appointments(role: str = "user", db: Session = Depends(get_db)):
    appointments = db.query(models.Appointment).all()
    html = STYLE + nav_bar(role)
    html += f"<h1>📅 Прийоми (Режим: {role.upper()})</h1>"
    html += "<table><tr><th>ID</th><th>Пацієнт</th><th>Лікар</th><th>Дата</th><th>Опис</th><th>Статус</th>"
    if role == "admin":
        html += "<th>Дії</th>"
    html += "</tr>"
    for a in appointments:
        patient_name = f"{a.patient.name} {a.patient.surname}" if a.patient else "—"
        doctor_name = f"{a.doctor.name} {a.doctor.surname}" if a.doctor else "—"
        status_class = {"заплановано": "badge-plan", "виконано": "badge-done", "скасовано": "badge-cancel"}.get(a.status, "")
        html += f"<tr><td>{a.id}</td><td>{patient_name}</td><td>{doctor_name}</td><td>{a.appointment_date}</td><td>{a.description or '—'}</td>"
        html += f"<td><span class='{status_class}'>{a.status}</span></td>"
        if role == "admin":
            html += f"<td><a href='/appointments/{a.id}/edit?role=admin'>✏️</a> | <a href='/appointments/{a.id}/delete?role=admin' onclick=\"return confirm('Видалити?')\">🗑️</a></td>"
        html += "</tr>"
    html += "</table><br>"
    if role == "admin":
        html += f"<a href='/appointments/add?role=admin'>➕ Додати прийом</a>"
    return HTMLResponse(content=html)


@app.get("/appointments/add", response_class=HTMLResponse)
async def add_appointment_form(role: str = "admin", db: Session = Depends(get_db)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    patients = db.query(models.Patient).all()
    doctors = db.query(models.Doctor).all()
    html = STYLE + nav_bar(role)
    html += "<h1>➕ Додати прийом</h1>"
    patient_options = "".join([f"<option value='{p.id}'>{p.name} {p.surname}</option>" for p in patients])
    doctor_options = "".join([f"<option value='{d.id}'>{d.name} {d.surname} ({d.specialization})</option>" for d in doctors])
    html += f"""<form method='post' action='/appointments?role=admin'>
        <label>Пацієнт: <br><select name='patient_id'>{patient_options}</select></label><br>
        <label>Лікар: <br><select name='doctor_id'>{doctor_options}</select></label><br>
        <label>Дата прийому: <br><input name='appointment_date' type='datetime-local' required></label><br>
        <label>Опис / скарги: <br><textarea name='description' rows='3' style='width:300px'></textarea></label><br>
        <label>Статус: <br>
          <select name='status'>
            <option value='заплановано'>Заплановано</option>
            <option value='виконано'>Виконано</option>
            <option value='скасовано'>Скасовано</option>
          </select>
        </label><br><br>
        <input type='submit' value='Зберегти'>
    </form>
    <br><a href='/appointments?role=admin'>← Назад до списку</a>"""
    return HTMLResponse(content=html)


@app.post("/appointments")
async def create_appointment(
    patient_id: int = Form(...), doctor_id: int = Form(...),
    appointment_date: str = Form(...), description: str = Form(""),
    status: str = Form("заплановано"), role: str = "admin",
    db: Session = Depends(get_db)
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    a = models.Appointment(patient_id=patient_id, doctor_id=doctor_id,
                           appointment_date=appointment_date, description=description, status=status)
    db.add(a)
    db.commit()
    return RedirectResponse(url=f"/appointments?role=admin", status_code=303)


@app.get("/appointments/{appt_id}/edit", response_class=HTMLResponse)
async def edit_appointment_form(appt_id: int, role: str = "admin", db: Session = Depends(get_db)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    a = db.query(models.Appointment).filter(models.Appointment.id == appt_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Прийом не знайдено")
    patients = db.query(models.Patient).all()
    doctors = db.query(models.Doctor).all()
    patient_options = "".join([f"<option value='{p.id}' {'selected' if p.id==a.patient_id else ''}>{p.name} {p.surname}</option>" for p in patients])
    doctor_options = "".join([f"<option value='{d.id}' {'selected' if d.id==a.doctor_id else ''}>{d.name} {d.surname}</option>" for d in doctors])
    html = STYLE + nav_bar(role)
    html += "<h1>✏️ Редагувати прийом</h1>"
    html += f"""<form method='post' action='/appointments/{appt_id}/edit?role=admin'>
        <label>Пацієнт: <br><select name='patient_id'>{patient_options}</select></label><br>
        <label>Лікар: <br><select name='doctor_id'>{doctor_options}</select></label><br>
        <label>Дата прийому: <br><input name='appointment_date' type='datetime-local' value='{a.appointment_date}' required></label><br>
        <label>Опис: <br><textarea name='description' rows='3' style='width:300px'>{a.description or ""}</textarea></label><br>
        <label>Статус: <br>
          <select name='status'>
            <option value='заплановано' {'selected' if a.status=='заплановано' else ''}>Заплановано</option>
            <option value='виконано' {'selected' if a.status=='виконано' else ''}>Виконано</option>
            <option value='скасовано' {'selected' if a.status=='скасовано' else ''}>Скасовано</option>
          </select>
        </label><br><br>
        <input type='submit' value='Зберегти зміни'>
    </form>
    <br><a href='/appointments?role=admin'>← Назад до списку</a>"""
    return HTMLResponse(content=html)


@app.post("/appointments/{appt_id}/edit")
async def update_appointment(
    appt_id: int,
    patient_id: int = Form(...), doctor_id: int = Form(...),
    appointment_date: str = Form(...), description: str = Form(""),
    status: str = Form("заплановано"), role: str = "admin",
    db: Session = Depends(get_db)
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    a = db.query(models.Appointment).filter(models.Appointment.id == appt_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Прийом не знайдено")
    a.patient_id = patient_id; a.doctor_id = doctor_id
    a.appointment_date = appointment_date; a.description = description; a.status = status
    db.commit()
    return RedirectResponse(url=f"/appointments?role=admin", status_code=303)


@app.get("/appointments/{appt_id}/delete")
async def delete_appointment(appt_id: int, role: str = "admin", db: Session = Depends(get_db)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    a = db.query(models.Appointment).filter(models.Appointment.id == appt_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Прийом не знайдено")
    db.delete(a)
    db.commit()
    return RedirectResponse(url=f"/appointments?role=admin", status_code=303)


# ============ SEED DATA ============

@app.on_event("startup")
async def seed_data():
    db = next(get_db())
    if db.query(models.Doctor).count() == 0:
        doctors = [
            models.Doctor(name="Іван", surname="Петренко", specialization="Терапевт", phone="0671234567"),
            models.Doctor(name="Олена", surname="Коваль", specialization="Хірург", phone="0507654321"),
        ]
        db.add_all(doctors)
        patients = [
            models.Patient(name="Марія", surname="Іваненко", birth_date="1990-05-15", phone="0931112233"),
            models.Patient(name="Василь", surname="Сидоренко", birth_date="1985-08-20", phone="0664445566"),
        ]
        db.add_all(patients)
        db.commit()
        appointments = [
            models.Appointment(patient_id=1, doctor_id=1, appointment_date="2026-05-15T10:00",
                               description="Болить зуб", status="заплановано"),
            models.Appointment(patient_id=2, doctor_id=2, appointment_date="2026-05-16T11:00",
                               description="Видалення зуба мудрості", status="виконано"),
        ]
        db.add_all(appointments)
        db.commit()
    db.close()
