"""
Лабораторна робота №2
Міграція на PostgreSQL + psycopg2
Запуск: uvicorn main:app --reload
"""
from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import engine, get_db
import models

models.Base.metadata.create_all(bind=engine)

# Решта коду аналогічна лабораторній роботі №1
# Імпортуємо app з lab1 для повторного використання логіки
from fastapi import FastAPI
app = FastAPI(
    title="Стоматологічний кабінет - PostgreSQL",
    description="ІС з використанням PostgreSQL та psycopg2",
    version="2.0.0"
)

STYLE = """
<style>
  body { font-family: Arial, sans-serif; margin: 30px; background: #f0f8ee; }
  h1 { color: #1e6b2e; }
  table { border-collapse: collapse; width: 100%; background: white; }
  th { background: #1e6b2e; color: white; padding: 8px 12px; }
  td { border: 1px solid #ccc; padding: 8px 12px; }
  tr:nth-child(even) { background: #eafaee; }
  a { color: #1e6b2e; text-decoration: none; margin: 0 4px; }
  input, select, textarea { padding: 6px; width: 300px; border: 1px solid #aaa; border-radius: 4px; }
  button, input[type=submit] { background: #1e6b2e; color: white; padding: 8px 20px; border: none; border-radius: 4px; cursor: pointer; }
  .nav { margin-bottom: 20px; }
  .nav a { background: #1e6b2e; color: white; padding: 6px 14px; border-radius: 4px; margin-right: 6px; }
</style>
"""

def nav_bar(role: str) -> str:
    return f"""
    <div class='nav'>
      <a href='/?role={role}'>🏠 Головна</a>
      <a href='/doctors?role={role}'>👨‍⚕️ Лікарі</a>
      <a href='/patients?role={role}'>🧑 Пацієнти</a>
      <a href='/appointments?role={role}'>📅 Прийоми</a>
      <span style='float:right'><b>PostgreSQL</b> | Роль: {role.upper()}</span>
    </div><hr>"""


@app.get("/", response_class=HTMLResponse)
async def home(role: str = "user"):
    html = STYLE + nav_bar(role)
    html += "<h1>🦷 Стоматологічний кабінет (PostgreSQL)</h1>"
    html += "<p>Версія 2.0 — база даних PostgreSQL з використанням бібліотеки psycopg2 та SQLAlchemy ORM.</p>"
    html += f"<ul><li><a href='/doctors?role={role}'>Лікарі</a></li>"
    html += f"<li><a href='/patients?role={role}'>Пацієнти</a></li>"
    html += f"<li><a href='/appointments?role={role}'>Прийоми</a></li></ul>"
    html += "<hr><p>Зміна ролі: <a href='/?role=admin'>Адміністратор</a> | <a href='/?role=user'>Користувач</a></p>"
    return HTMLResponse(content=html)


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
            html += f"<td><a href='/doctors/{d.id}/edit?role=admin'>✏️</a> | <a href='/doctors/{d.id}/delete?role=admin' onclick=\"return confirm('Видалити?')\">🗑️</a></td>"
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
        <label>Ім'я:<br><input name='name' required></label><br>
        <label>Прізвище:<br><input name='surname' required></label><br>
        <label>Спеціалізація:<br><input name='specialization' required></label><br>
        <label>Телефон:<br><input name='phone'></label><br><br>
        <input type='submit' value='Зберегти'>
    </form><br><a href='/doctors?role=admin'>← Назад</a>"""
    return HTMLResponse(content=html)


@app.post("/doctors")
async def create_doctor(
    name: str = Form(...), surname: str = Form(...),
    specialization: str = Form(...), phone: str = Form(""),
    role: str = "admin", db: Session = Depends(get_db)
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    db.add(models.Doctor(name=name, surname=surname, specialization=specialization, phone=phone))
    db.commit()
    return RedirectResponse(url="/doctors?role=admin", status_code=303)


@app.get("/doctors/{did}/edit", response_class=HTMLResponse)
async def edit_doctor_form(did: int, role: str = "admin", db: Session = Depends(get_db)):
    if role != "admin":
        raise HTTPException(status_code=403)
    d = db.query(models.Doctor).get(did)
    html = STYLE + nav_bar(role) + "<h1>✏️ Редагувати лікаря</h1>"
    html += f"""<form method='post' action='/doctors/{did}/edit?role=admin'>
        <label>Ім'я:<br><input name='name' value='{d.name}' required></label><br>
        <label>Прізвище:<br><input name='surname' value='{d.surname}' required></label><br>
        <label>Спеціалізація:<br><input name='specialization' value='{d.specialization}'></label><br>
        <label>Телефон:<br><input name='phone' value='{d.phone or ""}'></label><br><br>
        <input type='submit' value='Зберегти'></form><br><a href='/doctors?role=admin'>← Назад</a>"""
    return HTMLResponse(content=html)


@app.post("/doctors/{did}/edit")
async def update_doctor(did: int, name: str = Form(...), surname: str = Form(...),
    specialization: str = Form(...), phone: str = Form(""), role: str = "admin", db: Session = Depends(get_db)):
    if role != "admin": raise HTTPException(status_code=403)
    d = db.query(models.Doctor).get(did)
    d.name = name; d.surname = surname; d.specialization = specialization; d.phone = phone
    db.commit()
    return RedirectResponse(url="/doctors?role=admin", status_code=303)


@app.get("/doctors/{did}/delete")
async def delete_doctor(did: int, role: str = "admin", db: Session = Depends(get_db)):
    if role != "admin": raise HTTPException(status_code=403)
    db.delete(db.query(models.Doctor).get(did)); db.commit()
    return RedirectResponse(url="/doctors?role=admin", status_code=303)


@app.get("/patients", response_class=HTMLResponse)
async def list_patients(role: str = "user", db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    html = STYLE + nav_bar(role) + f"<h1>🧑 Пацієнти ({role.upper()})</h1>"
    html += "<table><tr><th>ID</th><th>Ім'я</th><th>Прізвище</th><th>Дата нар.</th><th>Телефон</th>"
    if role == "admin": html += "<th>Дії</th>"
    html += "</tr>"
    for p in patients:
        html += f"<tr><td>{p.id}</td><td>{p.name}</td><td>{p.surname}</td><td>{p.birth_date or '—'}</td><td>{p.phone or '—'}</td>"
        if role == "admin":
            html += f"<td><a href='/patients/{p.id}/edit?role=admin'>✏️</a> | <a href='/patients/{p.id}/delete?role=admin' onclick=\"return confirm('?')\">🗑️</a></td>"
        html += "</tr>"
    html += "</table><br>"
    if role == "admin": html += "<a href='/patients/add?role=admin'>➕ Додати пацієнта</a>"
    return HTMLResponse(content=html)


@app.get("/patients/add", response_class=HTMLResponse)
async def add_patient_form(role: str = "admin"):
    html = STYLE + nav_bar(role) + "<h1>➕ Пацієнт</h1>"
    html += f"""<form method='post' action='/patients?role=admin'>
        <label>Ім'я:<br><input name='name' required></label><br>
        <label>Прізвище:<br><input name='surname' required></label><br>
        <label>Дата нар.:<br><input name='birth_date' type='date'></label><br>
        <label>Телефон:<br><input name='phone'></label><br>
        <label>Адреса:<br><input name='address'></label><br><br>
        <input type='submit' value='Зберегти'></form><br><a href='/patients?role=admin'>← Назад</a>"""
    return HTMLResponse(content=html)


@app.post("/patients")
async def create_patient(name: str = Form(...), surname: str = Form(...),
    birth_date: str = Form(""), phone: str = Form(""), address: str = Form(""),
    role: str = "admin", db: Session = Depends(get_db)):
    if role != "admin": raise HTTPException(status_code=403)
    db.add(models.Patient(name=name, surname=surname, birth_date=birth_date, phone=phone, address=address))
    db.commit()
    return RedirectResponse(url="/patients?role=admin", status_code=303)


@app.get("/patients/{pid}/edit", response_class=HTMLResponse)
async def edit_patient_form(pid: int, role: str = "admin", db: Session = Depends(get_db)):
    p = db.query(models.Patient).get(pid)
    html = STYLE + nav_bar(role) + "<h1>✏️ Редагувати пацієнта</h1>"
    html += f"""<form method='post' action='/patients/{pid}/edit?role=admin'>
        <label>Ім'я:<br><input name='name' value='{p.name}' required></label><br>
        <label>Прізвище:<br><input name='surname' value='{p.surname}' required></label><br>
        <label>Дата нар.:<br><input name='birth_date' type='date' value='{p.birth_date or ""}'></label><br>
        <label>Телефон:<br><input name='phone' value='{p.phone or ""}'></label><br>
        <label>Адреса:<br><input name='address' value='{p.address or ""}'></label><br><br>
        <input type='submit' value='Зберегти'></form><br><a href='/patients?role=admin'>← Назад</a>"""
    return HTMLResponse(content=html)


@app.post("/patients/{pid}/edit")
async def update_patient(pid: int, name: str = Form(...), surname: str = Form(...),
    birth_date: str = Form(""), phone: str = Form(""), address: str = Form(""),
    role: str = "admin", db: Session = Depends(get_db)):
    p = db.query(models.Patient).get(pid)
    p.name = name; p.surname = surname; p.birth_date = birth_date; p.phone = phone; p.address = address
    db.commit()
    return RedirectResponse(url="/patients?role=admin", status_code=303)


@app.get("/patients/{pid}/delete")
async def delete_patient(pid: int, role: str = "admin", db: Session = Depends(get_db)):
    db.delete(db.query(models.Patient).get(pid)); db.commit()
    return RedirectResponse(url="/patients?role=admin", status_code=303)


@app.get("/appointments", response_class=HTMLResponse)
async def list_appointments(role: str = "user", db: Session = Depends(get_db)):
    appointments = db.query(models.Appointment).all()
    html = STYLE + nav_bar(role) + f"<h1>📅 Прийоми ({role.upper()})</h1>"
    html += "<table><tr><th>ID</th><th>Пацієнт</th><th>Лікар</th><th>Дата</th><th>Статус</th>"
    if role == "admin": html += "<th>Дії</th>"
    html += "</tr>"
    for a in appointments:
        pname = f"{a.patient.name} {a.patient.surname}" if a.patient else "—"
        dname = f"{a.doctor.name} {a.doctor.surname}" if a.doctor else "—"
        html += f"<tr><td>{a.id}</td><td>{pname}</td><td>{dname}</td><td>{a.appointment_date}</td><td>{a.status}</td>"
        if role == "admin":
            html += f"<td><a href='/appointments/{a.id}/edit?role=admin'>✏️</a> | <a href='/appointments/{a.id}/delete?role=admin' onclick=\"return confirm('?')\">🗑️</a></td>"
        html += "</tr>"
    html += "</table><br>"
    if role == "admin": html += "<a href='/appointments/add?role=admin'>➕ Додати прийом</a>"
    return HTMLResponse(content=html)


@app.get("/appointments/add", response_class=HTMLResponse)
async def add_appointment_form(role: str = "admin", db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    doctors = db.query(models.Doctor).all()
    po = "".join([f"<option value='{p.id}'>{p.name} {p.surname}</option>" for p in patients])
    do_ = "".join([f"<option value='{d.id}'>{d.name} {d.surname}</option>" for d in doctors])
    html = STYLE + nav_bar(role) + "<h1>➕ Прийом</h1>"
    html += f"""<form method='post' action='/appointments?role=admin'>
        <label>Пацієнт:<br><select name='patient_id'>{po}</select></label><br>
        <label>Лікар:<br><select name='doctor_id'>{do_}</select></label><br>
        <label>Дата:<br><input name='appointment_date' type='datetime-local'></label><br>
        <label>Опис:<br><textarea name='description'></textarea></label><br>
        <label>Статус:<br><select name='status'>
          <option>заплановано</option><option>виконано</option><option>скасовано</option>
        </select></label><br><br>
        <input type='submit' value='Зберегти'></form><br><a href='/appointments?role=admin'>← Назад</a>"""
    return HTMLResponse(content=html)


@app.post("/appointments")
async def create_appointment(patient_id: int = Form(...), doctor_id: int = Form(...),
    appointment_date: str = Form(...), description: str = Form(""), status: str = Form("заплановано"),
    role: str = "admin", db: Session = Depends(get_db)):
    if role != "admin": raise HTTPException(status_code=403)
    db.add(models.Appointment(patient_id=patient_id, doctor_id=doctor_id,
        appointment_date=appointment_date, description=description, status=status))
    db.commit()
    return RedirectResponse(url="/appointments?role=admin", status_code=303)


@app.get("/appointments/{aid}/edit", response_class=HTMLResponse)
async def edit_appointment_form(aid: int, role: str = "admin", db: Session = Depends(get_db)):
    a = db.query(models.Appointment).get(aid)
    patients = db.query(models.Patient).all()
    doctors = db.query(models.Doctor).all()
    po = "".join([f"<option value='{p.id}' {'selected' if p.id==a.patient_id else ''}>{p.name} {p.surname}</option>" for p in patients])
    do_ = "".join([f"<option value='{d.id}' {'selected' if d.id==a.doctor_id else ''}>{d.name} {d.surname}</option>" for d in doctors])
    html = STYLE + nav_bar(role) + "<h1>✏️ Редагувати прийом</h1>"
    html += f"""<form method='post' action='/appointments/{aid}/edit?role=admin'>
        <label>Пацієнт:<br><select name='patient_id'>{po}</select></label><br>
        <label>Лікар:<br><select name='doctor_id'>{do_}</select></label><br>
        <label>Дата:<br><input name='appointment_date' type='datetime-local' value='{a.appointment_date}'></label><br>
        <label>Опис:<br><textarea name='description'>{a.description or ""}</textarea></label><br>
        <label>Статус:<br><select name='status'>
          <option {'selected' if a.status=='заплановано' else ''}>заплановано</option>
          <option {'selected' if a.status=='виконано' else ''}>виконано</option>
          <option {'selected' if a.status=='скасовано' else ''}>скасовано</option>
        </select></label><br><br>
        <input type='submit' value='Зберегти'></form><br><a href='/appointments?role=admin'>← Назад</a>"""
    return HTMLResponse(content=html)


@app.post("/appointments/{aid}/edit")
async def update_appointment(aid: int, patient_id: int = Form(...), doctor_id: int = Form(...),
    appointment_date: str = Form(...), description: str = Form(""), status: str = Form("заплановано"),
    role: str = "admin", db: Session = Depends(get_db)):
    a = db.query(models.Appointment).get(aid)
    a.patient_id = patient_id; a.doctor_id = doctor_id; a.appointment_date = appointment_date
    a.description = description; a.status = status
    db.commit()
    return RedirectResponse(url="/appointments?role=admin", status_code=303)


@app.get("/appointments/{aid}/delete")
async def delete_appointment(aid: int, role: str = "admin", db: Session = Depends(get_db)):
    db.delete(db.query(models.Appointment).get(aid)); db.commit()
    return RedirectResponse(url="/appointments?role=admin", status_code=303)
