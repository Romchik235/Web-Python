"""
Лабораторна робота №3
Використання СУБД MongoDB при створенні вебзастосунку мовою Python
Фреймворк: FastAPI + pymongo
"""
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional
import uvicorn

# ============ MongoDB Connection ============
client = MongoClient("mongodb://localhost:27017/")
db_mongo = client["dental_db"]

doctors_col = db_mongo["doctors"]
patients_col = db_mongo["patients"]
appointments_col = db_mongo["appointments"]

app = FastAPI(
    title="Стоматологічний кабінет - MongoDB",
    description="ІС з використанням MongoDB та pymongo",
    version="3.0.0"
)

STYLE = """
<style>
  body { font-family: Arial, sans-serif; margin: 30px; background: #fef9f0; }
  h1 { color: #7b3f00; }
  table { border-collapse: collapse; width: 100%; background: white; }
  th { background: #c0392b; color: white; padding: 8px 12px; }
  td { border: 1px solid #ccc; padding: 8px 12px; }
  tr:nth-child(even) { background: #fef5e7; }
  a { color: #c0392b; text-decoration: none; margin: 0 4px; }
  input, select, textarea { padding: 6px; width: 300px; border: 1px solid #aaa; border-radius: 4px; }
  button, input[type=submit] { background: #c0392b; color: white; padding: 8px 20px; border: none; border-radius: 4px; cursor: pointer; }
  .nav { margin-bottom: 20px; }
  .nav a { background: #c0392b; color: white; padding: 6px 14px; border-radius: 4px; margin-right: 6px; }
</style>
"""


def nav_bar(role: str) -> str:
    return f"""<div class='nav'>
      <a href='/?role={role}'>🏠 Головна</a>
      <a href='/doctors?role={role}'>👨‍⚕️ Лікарі</a>
      <a href='/patients?role={role}'>🧑 Пацієнти</a>
      <a href='/appointments?role={role}'>📅 Прийоми</a>
      <span style='float:right'><b>MongoDB</b> | Роль: {role.upper()}</span>
    </div><hr>"""


# ============ HOME ============
@app.get("/", response_class=HTMLResponse)
async def home(role: str = "user"):
    html = STYLE + nav_bar(role)
    html += "<h1>🦷 Стоматологічний кабінет (MongoDB)</h1>"
    html += "<p>Версія 3.0 — документно-орієнтована БД MongoDB з використанням pymongo.</p>"
    html += f"<ul><li><a href='/doctors?role={role}'>Лікарі</a></li>"
    html += f"<li><a href='/patients?role={role}'>Пацієнти</a></li>"
    html += f"<li><a href='/appointments?role={role}'>Прийоми</a></li></ul>"
    html += "<hr><a href='/?role=admin'>Адміністратор</a> | <a href='/?role=user'>Користувач</a>"
    return HTMLResponse(content=html)


# ============ DOCTORS ============
@app.get("/doctors", response_class=HTMLResponse)
async def list_doctors(role: str = "user"):
    doctors = list(doctors_col.find())
    html = STYLE + nav_bar(role) + f"<h1>👨‍⚕️ Лікарі ({role.upper()})</h1>"
    html += "<table><tr><th>ID</th><th>Ім'я</th><th>Прізвище</th><th>Спеціалізація</th><th>Телефон</th>"
    if role == "admin": html += "<th>Дії</th>"
    html += "</tr>"
    for d in doctors:
        html += f"<tr><td>{str(d['_id'])[-6:]}</td><td>{d['name']}</td><td>{d['surname']}</td><td>{d['specialization']}</td><td>{d.get('phone','—')}</td>"
        if role == "admin":
            html += f"<td><a href='/doctors/{d['_id']}/edit?role=admin'>✏️</a> | <a href='/doctors/{d['_id']}/delete?role=admin' onclick=\"return confirm('Видалити?')\">🗑️</a></td>"
        html += "</tr>"
    html += "</table><br>"
    if role == "admin": html += "<a href='/doctors/add?role=admin'>➕ Додати лікаря</a>"
    return HTMLResponse(content=html)


@app.get("/doctors/add", response_class=HTMLResponse)
async def add_doctor_form(role: str = "admin"):
    html = STYLE + nav_bar(role) + "<h1>➕ Додати лікаря</h1>"
    html += f"""<form method='post' action='/doctors?role=admin'>
        <label>Ім'я:<br><input name='name' required></label><br>
        <label>Прізвище:<br><input name='surname' required></label><br>
        <label>Спеціалізація:<br><input name='specialization' required></label><br>
        <label>Телефон:<br><input name='phone'></label><br><br>
        <input type='submit' value='Зберегти'></form>
    <br><a href='/doctors?role=admin'>← Назад</a>"""
    return HTMLResponse(content=html)


@app.post("/doctors")
async def create_doctor(name: str = Form(...), surname: str = Form(...),
    specialization: str = Form(...), phone: str = Form(""), role: str = "admin"):
    if role != "admin": raise HTTPException(status_code=403)
    doctors_col.insert_one({"name": name, "surname": surname, "specialization": specialization, "phone": phone})
    return RedirectResponse(url="/doctors?role=admin", status_code=303)


@app.get("/doctors/{doc_id}/edit", response_class=HTMLResponse)
async def edit_doctor_form(doc_id: str, role: str = "admin"):
    d = doctors_col.find_one({"_id": ObjectId(doc_id)})
    if not d: raise HTTPException(status_code=404)
    html = STYLE + nav_bar(role) + "<h1>✏️ Редагувати лікаря</h1>"
    html += f"""<form method='post' action='/doctors/{doc_id}/edit?role=admin'>
        <label>Ім'я:<br><input name='name' value='{d["name"]}' required></label><br>
        <label>Прізвище:<br><input name='surname' value='{d["surname"]}' required></label><br>
        <label>Спеціалізація:<br><input name='specialization' value='{d["specialization"]}'></label><br>
        <label>Телефон:<br><input name='phone' value='{d.get("phone","")}'></label><br><br>
        <input type='submit' value='Зберегти'></form><br><a href='/doctors?role=admin'>← Назад</a>"""
    return HTMLResponse(content=html)


@app.post("/doctors/{doc_id}/edit")
async def update_doctor(doc_id: str, name: str = Form(...), surname: str = Form(...),
    specialization: str = Form(...), phone: str = Form(""), role: str = "admin"):
    doctors_col.update_one({"_id": ObjectId(doc_id)}, {"$set": {"name": name, "surname": surname,
        "specialization": specialization, "phone": phone}})
    return RedirectResponse(url="/doctors?role=admin", status_code=303)


@app.get("/doctors/{doc_id}/delete")
async def delete_doctor(doc_id: str, role: str = "admin"):
    doctors_col.delete_one({"_id": ObjectId(doc_id)})
    return RedirectResponse(url="/doctors?role=admin", status_code=303)


# ============ PATIENTS ============
@app.get("/patients", response_class=HTMLResponse)
async def list_patients(role: str = "user"):
    patients = list(patients_col.find())
    html = STYLE + nav_bar(role) + f"<h1>🧑 Пацієнти ({role.upper()})</h1>"
    html += "<table><tr><th>ID</th><th>Ім'я</th><th>Прізвище</th><th>Дата нар.</th><th>Телефон</th>"
    if role == "admin": html += "<th>Дії</th>"
    html += "</tr>"
    for p in patients:
        html += f"<tr><td>{str(p['_id'])[-6:]}</td><td>{p['name']}</td><td>{p['surname']}</td><td>{p.get('birth_date','—')}</td><td>{p.get('phone','—')}</td>"
        if role == "admin":
            html += f"<td><a href='/patients/{p['_id']}/edit?role=admin'>✏️</a> | <a href='/patients/{p['_id']}/delete?role=admin' onclick=\"return confirm('?')\">🗑️</a></td>"
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

@app.get("/search", response_class=HTMLResponse)
async def search_patients(q: str = ""):
    html = STYLE + "<h1>🔍 Пошук пацієнтів</h1>"

    html += """
    <form method='get'>
        <input name='q' placeholder='Введіть прізвище'>
        <input type='submit' value='Шукати'>
    </form><br>
    """

    if q:
        patients = list(patients_col.find({
            "surname": {"$regex": q, "$options": "i"}
        }))

        html += "<h2>Результати:</h2>"

        for p in patients:
            html += f"""
            <div>
                {p['name']} {p['surname']} |
                {p.get('phone', '—')}
            </div>
            """

    return HTMLResponse(content=html)


@app.post("/patients")
async def create_patient(name: str = Form(...), surname: str = Form(...),
    birth_date: str = Form(""), phone: str = Form(""), address: str = Form(""), role: str = "admin"):
    if role != "admin": raise HTTPException(status_code=403)
    patients_col.insert_one({"name": name, "surname": surname, "birth_date": birth_date, "phone": phone, "address": address})
    return RedirectResponse(url="/patients?role=admin", status_code=303)


@app.get("/patients/{pid}/edit", response_class=HTMLResponse)
async def edit_patient_form(pid: str, role: str = "admin"):
    p = patients_col.find_one({"_id": ObjectId(pid)})
    html = STYLE + nav_bar(role) + "<h1>✏️ Редагувати пацієнта</h1>"
    html += f"""<form method='post' action='/patients/{pid}/edit?role=admin'>
        <label>Ім'я:<br><input name='name' value='{p["name"]}' required></label><br>
        <label>Прізвище:<br><input name='surname' value='{p["surname"]}' required></label><br>
        <label>Дата нар.:<br><input name='birth_date' type='date' value='{p.get("birth_date","")}'></label><br>
        <label>Телефон:<br><input name='phone' value='{p.get("phone","")}'></label><br>
        <label>Адреса:<br><input name='address' value='{p.get("address","")}'></label><br><br>
        <input type='submit' value='Зберегти'></form><br><a href='/patients?role=admin'>← Назад</a>"""
    return HTMLResponse(content=html)


@app.post("/patients/{pid}/edit")
async def update_patient(pid: str, name: str = Form(...), surname: str = Form(...),
    birth_date: str = Form(""), phone: str = Form(""), address: str = Form(""), role: str = "admin"):
    patients_col.update_one({"_id": ObjectId(pid)}, {"$set": {"name": name, "surname": surname,
        "birth_date": birth_date, "phone": phone, "address": address}})
    return RedirectResponse(url="/patients?role=admin", status_code=303)


@app.get("/patients/{pid}/delete")
async def delete_patient(pid: str, role: str = "admin"):
    patients_col.delete_one({"_id": ObjectId(pid)})
    return RedirectResponse(url="/patients?role=admin", status_code=303)


# ============ APPOINTMENTS ============
@app.get("/appointments", response_class=HTMLResponse)
async def list_appointments(role: str = "user"):
    appointments = list(appointments_col.find())
    html = STYLE + nav_bar(role) + f"<h1>📅 Прийоми ({role.upper()})</h1>"
    html += "<table><tr><th>ID</th><th>Пацієнт</th><th>Лікар</th><th>Дата</th><th>Статус</th>"
    if role == "admin": html += "<th>Дії</th>"
    html += "</tr>"
    for a in appointments:
        html += f"<tr><td>{str(a['_id'])[-6:]}</td><td>{a.get('patient_name','—')}</td><td>{a.get('doctor_name','—')}</td><td>{a.get('appointment_date','—')}</td><td>{a.get('status','—')}</td>"
        if role == "admin":
            html += f"<td><a href='/appointments/{a['_id']}/edit?role=admin'>✏️</a> | <a href='/appointments/{a['_id']}/delete?role=admin' onclick=\"return confirm('?')\">🗑️</a></td>"
    html += "</table><br>"
    if role == "admin": html += "<a href='/appointments/add?role=admin'>➕ Додати прийом</a>"
    return HTMLResponse(content=html)


@app.get("/appointments/add", response_class=HTMLResponse)
async def add_appointment_form(role: str = "admin"):
    patients = list(patients_col.find())
    doctors = list(doctors_col.find())
    po = "".join([f"<option value='{p['_id']}'>{p['name']} {p['surname']}</option>" for p in patients])
    do_ = "".join([f"<option value='{d['_id']}'>{d['name']} {d['surname']}</option>" for d in doctors])
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
async def create_appointment(patient_id: str = Form(...), doctor_id: str = Form(...),
    appointment_date: str = Form(...), description: str = Form(""), status: str = Form("заплановано"), role: str = "admin"):
    if role != "admin": raise HTTPException(status_code=403)
    patient = patients_col.find_one({"_id": ObjectId(patient_id)})
    doctor = doctors_col.find_one({"_id": ObjectId(doctor_id)})
    appointments_col.insert_one({
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "patient_name": f"{patient['name']} {patient['surname']}" if patient else "—",
        "doctor_name": f"{doctor['name']} {doctor['surname']}" if doctor else "—",
        "appointment_date": appointment_date,
        "description": description,
        "status": status
    })
    return RedirectResponse(url="/appointments?role=admin", status_code=303)


@app.get("/appointments/{aid}/edit", response_class=HTMLResponse)
async def edit_appointment_form(aid: str, role: str = "admin"):
    a = appointments_col.find_one({"_id": ObjectId(aid)})
    html = STYLE + nav_bar(role) + "<h1>✏️ Редагувати прийом</h1>"
    html += f"""<form method='post' action='/appointments/{aid}/edit?role=admin'>
        <label>Дата:<br><input name='appointment_date' type='datetime-local' value='{a.get("appointment_date","")}'></label><br>
        <label>Опис:<br><textarea name='description'>{a.get("description","")}</textarea></label><br>
        <label>Статус:<br><select name='status'>
          <option {'selected' if a.get('status')=='заплановано' else ''}>заплановано</option>
          <option {'selected' if a.get('status')=='виконано' else ''}>виконано</option>
          <option {'selected' if a.get('status')=='скасовано' else ''}>скасовано</option>
        </select></label><br><br>
        <input type='submit' value='Зберегти'></form><br><a href='/appointments?role=admin'>← Назад</a>"""
    return HTMLResponse(content=html)


@app.post("/appointments/{aid}/edit")
async def update_appointment(aid: str, appointment_date: str = Form(...),
    description: str = Form(""), status: str = Form("заплановано"), role: str = "admin"):
    appointments_col.update_one({"_id": ObjectId(aid)}, {"$set": {"appointment_date": appointment_date,
        "description": description, "status": status}})
    return RedirectResponse(url="/appointments?role=admin", status_code=303)


@app.get("/appointments/{aid}/delete")
async def delete_appointment(aid: str, role: str = "admin"):
    appointments_col.delete_one({"_id": ObjectId(aid)})
    return RedirectResponse(url="/appointments?role=admin", status_code=303)


# ============ SEED ============
@app.on_event("startup")
async def seed_data():
    if doctors_col.count_documents({}) == 0:
        doctors_col.insert_many([
            {"name": "Іван", "surname": "Петренко", "specialization": "Терапевт", "phone": "0671234567"},
            {"name": "Олена", "surname": "Коваль", "specialization": "Хірург", "phone": "0507654321"},
        ])
        patients_col.insert_many([
            {"name": "Марія", "surname": "Іваненко", "birth_date": "1990-05-15", "phone": "0931112233", "address": "Київ, вул. Хрещатик 1"},
            {"name": "Василь", "surname": "Сидоренко", "birth_date": "1985-08-20", "phone": "0664445566", "address": "Київ, вул. Шевченка 5"},
        ])
        appointments_col.insert_many([
            {"patient_name": "Марія Іваненко", "doctor_name": "Іван Петренко",
             "appointment_date": "2026-05-15T10:00", "description": "Болить зуб", "status": "заплановано"},
        ])
