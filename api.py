from fastapi import APIRouter, Request
from models import Equipment, Movement, TechIssue

router = APIRouter()

equipment_list = []
movement_list  = []
issue_list     = []

eq_id    = 1
mov_id   = 1
issue_id = 1

equipment_list.append(Equipment(1, "Комп'ютер Dell",  "computer",  "SN-001", "101", "working",      "Основний ПК"))
equipment_list.append(Equipment(2, "Принтер HP",      "printer",   "SN-002", "101", "working",      "Лазерний принтер"))
equipment_list.append(Equipment(3, "Проектор Epson",  "projector", "SN-003", "102", "faulty",       "Не працює лампа"))
equipment_list.append(Equipment(4, "Монітор Samsung", "monitor",   "SN-004", "103", "working",      "Full HD"))
equipment_list.append(Equipment(5, "Ноутбук ASUS",    "computer",  "SN-005", "104", "under_repair", "Замінюється диск"))
eq_id = 6


@router.get("/equipment")
async def get_all_equipment(request: Request):
    params   = dict(request.query_params)
    status   = params.get("status")
    category = params.get("category")
    room     = params.get("room")
    search   = params.get("search")

    result = equipment_list
    if status:
        result = [e for e in result if e.status == status]
    if category:
        result = [e for e in result if e.category == category]
    if room:
        result = [e for e in result if e.room == room]
    if search:
        result = [e for e in result if search.lower() in e.name.lower()]

    return [e.to_dict() for e in result]


@router.get("/equipment/faulty")
def get_faulty():
    return [e.to_dict() for e in equipment_list if e.status == "faulty"]


@router.get("/equipment/{eid}")
def get_equipment(eid: int):
    for e in equipment_list:
        if e.eq_id == eid:
            return e.to_dict()
    return {"message": "Not found"}


@router.post("/equipment/add")
async def add_equipment(request: Request):
    global eq_id
    data = await request.json()

    name          = data.get("name")
    serial_number = data.get("serial_number")
    room          = data.get("room")

    if not name or not serial_number or not room:
        return {"message": "name, serial_number and room are required"}

    for e in equipment_list:
        if e.serial_number == serial_number:
            return {"message": "Serial number already exists"}

    obj = Equipment(eq_id, name, data.get("category", "other"),
                    serial_number, room, data.get("status", "working"),
                    data.get("description", ""))
    equipment_list.append(obj)
    eq_id += 1
    return obj.to_dict()


@router.patch("/equipment/{eid}/status")
async def update_status(eid: int, request: Request):
    data = await request.json()
    for e in equipment_list:
        if e.eq_id == eid:
            if data.get("status"):
                e.change_status(data["status"])
            if data.get("description"):
                e.description = data["description"]
            return e.to_dict()
    return {"message": "Not found"}


@router.post("/equipment/move")
async def move_equipment(request: Request):
    global mov_id
    data     = await request.json()
    eid      = data.get("eq_id")
    new_room = data.get("new_room")

    for e in equipment_list:
        if e.eq_id == eid:
            record = Movement(mov_id, eid, e.room, new_room, data.get("reason", ""))
            movement_list.append(record)
            mov_id += 1
            e.change_room(new_room)
            return record.to_dict()
    return {"message": "Not found"}


@router.get("/movements")
def get_movements():
    return [m.to_dict() for m in reversed(movement_list)]


@router.get("/equipment/{eid}/movements")
def get_equipment_movements(eid: int):
    return [m.to_dict() for m in reversed(movement_list) if m.eq_id == eid]


@router.post("/issues/add")
async def add_issue(request: Request):
    global issue_id
    data = await request.json()
    eid  = data.get("eq_id")

    if not any(e.eq_id == eid for e in equipment_list):
        return {"message": "Equipment not found"}

    obj = TechIssue(issue_id, eid, data.get("description"), data.get("severity", "medium"))
    issue_list.append(obj)
    issue_id += 1
    return obj.to_dict()


@router.get("/equipment/{eid}/issues")
def get_equipment_issues(eid: int):
    return [i.to_dict() for i in reversed(issue_list) if i.eq_id == eid]


@router.get("/statistics")
def get_statistics():
    statuses = [e.status for e in equipment_list]
    by_cat, by_room = {}, {}
    for e in equipment_list:
        by_cat[e.category] = by_cat.get(e.category, 0) + 1
        by_room[e.room]    = by_room.get(e.room, 0) + 1
    return {
        "total": len(equipment_list),
        "working": statuses.count("working"),
        "faulty": statuses.count("faulty"),
        "under_repair": statuses.count("under_repair"),
        "by_category": by_cat,
        "by_room": by_room,
        "total_movements": len(movement_list),
        "unresolved_issues": sum(1 for i in issue_list if not i.resolved)
    }