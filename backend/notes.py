from db import SessionLocal
from models import Note

def save_note(note):
    db = SessionLocal()

    new_note = Note(
        user_id=note.get("user_id", "default"),
        query=note["query"],
        answer=note["answer"],
        actions=note["actions"]
    )

    db.add(new_note)
    db.commit()
    db.close()


def get_notes(user_id="default"):
    db = SessionLocal()

    notes = db.query(Note).filter(Note.user_id == user_id).all()

    result = [
        {
            "query": n.query,
            "answer": n.answer,
            "actions": n.actions
        }
        for n in notes
    ]

    db.close()
    return result