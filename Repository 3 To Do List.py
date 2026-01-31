#!/usr/bin/env python3
"""
To-Do List (CLI)

Fitur:
- Simpan, edit, hapus (ke trash), dan restore data tugas/kegiatan/acara
- Lihat data tersimpan dan riwayat edit untuk revert
- Status tugas (selesai/belum selesai)

Data disimpan di `tasks.json` di direktori kerja.
"""
import json
import os
import datetime
from typing import List, Dict, Any

DATA_FILE = "tasks.json"


def now_ts() -> str:
    return datetime.datetime.now().isoformat()


def load_tasks() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks: List[Dict[str, Any]]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def next_id(tasks: List[Dict[str, Any]]) -> int:
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


def add_task(tasks: List[Dict[str, Any]]) -> None:
    title = input("📝 Judul: ").strip()
    if not title:
        print("❌ Judul tidak boleh kosong")
        return
    kind = input("🏷️ Tipe (tugas/kegiatan/acara) [tugas]: ").strip() or "tugas"
    desc = input("🗒️ Deskripsi (opsional): ").strip()
    due = input("🕒 Tanggal/Jam (opsional, contoh 2026-01-31 15:00): ").strip()
    task = {
        "id": next_id(tasks),
        "title": title,
        "description": desc,
        "type": kind,
        "due": due,
        "status": "belum",
        "deleted": False,
        "created_at": now_ts(),
        "updated_at": now_ts(),
        "history": []  # menyimpan snapshot sebelum edit
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"✅ Tambah tugas berhasil (id={task['id']})")


def find_task(tasks: List[Dict[str, Any]], tid: int) -> Dict[str, Any] | None:
    for t in tasks:
        if t["id"] == tid:
            return t
    return None


def edit_task(tasks: List[Dict[str, Any]]) -> None:
    try:
        tid = int(input("ID tugas yang diedit: ").strip())
    except ValueError:
        print("ID tidak valid")
        return
    t = find_task(tasks, tid)
    if not t:
        print("Tugas tidak ditemukan")
        return
    if t.get("deleted"):
        print("🗑️ Tugas sudah dihapus. Restore dulu jika ingin edit.")
        return
    # simpan snapshot ke history
    snapshot = {k: t[k] for k in t if k not in ("history",)}
    snapshot["snapshot_at"] = now_ts()
    t.setdefault("history", []).append(snapshot)
    print("(Biarkan kosong untuk mempertahankan nilai lama)")
    title = input(f"📝 Judul [{t['title']}]: ").strip() or t["title"]
    desc = input(f"🗒️ Deskripsi [{t.get('description','')}]: ").strip() or t.get("description","")
    kind = input(f"🏷️ Tipe [{t.get('type','tugas')}]: ").strip() or t.get("type","tugas")
    due = input(f"🕒 Tanggal/Jam [{t.get('due','')}]: ").strip() or t.get("due","")
    status = input(f"✅ Status (selesai/belum) [{t.get('status','belum')}]: ").strip() or t.get("status","belum")
    t.update({
        "title": title,
        "description": desc,
        "type": kind,
        "due": due,
        "status": status,
        "updated_at": now_ts()
    })
    save_tasks(tasks)
    print("✅ Edit disimpan. Riwayat edit tersedia untuk revert.")


def delete_task(tasks: List[Dict[str, Any]]) -> None:
    try:
        tid = int(input("ID tugas yang dihapus: ").strip())
    except ValueError:
        print("ID tidak valid")
        return
    t = find_task(tasks, tid)
    if not t:
        print("Tugas tidak ditemukan")
        return
    if t.get("deleted"):
        print("ℹ️ Tugas sudah dihapus")
        return
    confirm = input("🗑️ Pindah ke trash? (y/n): ").strip().lower()
    if confirm != "y":
        print("✖️ Dibatalkan")
        return
    t["deleted"] = True
    t["updated_at"] = now_ts()
    save_tasks(tasks)
    print("🗑️ Tugas dipindah ke trash")


def restore_task(tasks: List[Dict[str, Any]]) -> None:
    try:
        tid = int(input("ID tugas yang direstore: ").strip())
    except ValueError:
        print("ID tidak valid")
        return
    t = find_task(tasks, tid)
    if not t:
        print("Tugas tidak ditemukan")
        return
    if not t.get("deleted"):
        print("ℹ️ Tugas tidak berada di trash")
        return
    t["deleted"] = False
    t["updated_at"] = now_ts()
    save_tasks(tasks)
    print("♻️ Tugas berhasil direstore")


def list_tasks(tasks: List[Dict[str, Any]], show_deleted: bool = False) -> None:
    found = [t for t in tasks if (show_deleted or not t.get("deleted"))]
    if not found:
        print("Tidak ada tugas.")
        return
    type_emoji = {"tugas": "🛠️", "kegiatan": "🎯", "acara": "📅"}
    for t in sorted(found, key=lambda x: x["id"]):
        del_mark = " 🗑️" if t.get("deleted") else ""
        status = "✅" if t.get("status") == "selesai" else "⏳"
        kind_icon = type_emoji.get(t.get("type","tugas"), "🏷️")
        due = f" | 🕒 {t.get('due')}" if t.get('due') else ""
        print(f"ID:{t['id']:3}{del_mark} {status} {kind_icon} {t['title']}{due}")
        if t.get("description"):
            print(f"    {t['description']}")


def mark_complete(tasks: List[Dict[str, Any]]) -> None:
    try:
        tid = int(input("ID tugas yang diubah status: ").strip())
    except ValueError:
        print("ID tidak valid")
        return
    t = find_task(tasks, tid)
    if not t:
        print("Tugas tidak ditemukan")
        return
    if t.get("deleted"):
        print("🗑️ Tugas di trash — restore dahulu")
        return
    t["status"] = "selesai" if t.get("status") != "selesai" else "belum"
    t["updated_at"] = now_ts()
    save_tasks(tasks)
    print(f"🔁 Status diubah menjadi: {t['status']}")


def view_history(tasks: List[Dict[str, Any]]) -> None:
    try:
        tid = int(input("ID tugas untuk melihat riwayat: ").strip())
    except ValueError:
        print("ID tidak valid")
        return
    t = find_task(tasks, tid)
    if not t:
        print("Tugas tidak ditemukan")
        return
    history = t.get("history", [])
    if not history:
        print("ℹ️ Belum ada riwayat edit untuk tugas ini.")
        return
    for i, h in enumerate(reversed(history), 1):
        print(f"Versi {len(history)-i+1} (snapshot_at={h.get('snapshot_at')}):")
        print(f"  Judul: {h.get('title')}")
        print(f"  Deskripsi: {h.get('description')}")
        print(f"  Tipe: {h.get('type')}")
        print(f"  Due: {h.get('due')}")
        print(f"  Status: {h.get('status')}")


def revert_edit(tasks: List[Dict[str, Any]]) -> None:
    try:
        tid = int(input("ID tugas untuk revert: ").strip())
    except ValueError:
        print("ID tidak valid")
        return
    t = find_task(tasks, tid)
    if not t:
        print("Tugas tidak ditemukan")
        return
    history = t.get("history", [])
    if not history:
        print("ℹ️ Tidak ada versi untuk direvert")
        return
    # tampilkan versi
    for idx, h in enumerate(history, 1):
        print(f"{idx}. {h.get('title')} (snapshot_at={h.get('snapshot_at')})")
    try:
        sel = int(input("Pilih nomor versi untuk restore (0 untuk batal): ").strip())
    except ValueError:
        print("Pilihan tidak valid")
        return
    if sel <= 0 or sel > len(history):
        print("✖️ Dibatalkan")
        return
    snap = history[sel - 1]
    # simpan current ke history sebelum mengganti
    current_snapshot = {k: t[k] for k in t if k not in ("history",)}
    current_snapshot["snapshot_at"] = now_ts()
    t.setdefault("history", []).append(current_snapshot)
    # restore
    for key in ("title", "description", "type", "due", "status"):
        t[key] = snap.get(key)
    t["updated_at"] = now_ts()
    save_tasks(tasks)
    print("✅ Revert berhasil")


def purge_deleted(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    confirm = input("🧹 Hapus permanen semua item di trash? (y/n): ").strip().lower()
    if confirm != "y":
        print("✖️ Dibatalkan")
        return tasks
    new_tasks = [t for t in tasks if not t.get("deleted")]
    save_tasks(new_tasks)
    print("🧹 Trash dikosongkan")
    return new_tasks


def print_menu() -> None:
    print("\n📋 === To-Do List ===")
    print("1. ➕ Tambah tugas")
    print("2. ✏️ Edit tugas")
    print("3. 🗑️ Hapus (ke trash)")
    print("4. ♻️ Restore dari trash")
    print("5. 📄 List tugas")
    print("6. 📁 List termasuk trash")
    print("7. ✅ Tandai selesai/belum selesai")
    print("8. 🕘 Lihat riwayat edit")
    print("9. 🔁 Revert edit")
    print("10. 🧹 Kosongkan trash (hapus permanen)")
    print("0. ❌ Keluar")


def main():
    tasks = load_tasks()
    while True:
        print_menu()
        cmd = input("Pilih: ").strip()
        if cmd == "1":
            add_task(tasks)
        elif cmd == "2":
            edit_task(tasks)
        elif cmd == "3":
            delete_task(tasks)
        elif cmd == "4":
            restore_task(tasks)
        elif cmd == "5":
            list_tasks(tasks, show_deleted=False)
        elif cmd == "6":
            list_tasks(tasks, show_deleted=True)
        elif cmd == "7":
            mark_complete(tasks)
        elif cmd == "8":
            view_history(tasks)
        elif cmd == "9":
            revert_edit(tasks)
        elif cmd == "10":
            tasks = purge_deleted(tasks)
        elif cmd == "0":
            print("Sampai jumpa!")
            break
        else:
            print("Perintah tidak dikenali")


if __name__ == "__main__":
    main()
