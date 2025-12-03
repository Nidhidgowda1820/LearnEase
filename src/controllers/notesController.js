import { PrismaClient } from "@prisma/client";
const prisma = new PrismaClient();

// ===============================
// CREATE NOTE
// ===============================
export const createNote = async (req, res) => {
  try {
    const { subject_code, note } = req.body;

    const newNote = await prisma.notes.create({
      data: {
        user_id: req.user.id,
        subject_code,
        note,
      },
    });

    res.json({ message: "Note created", note: newNote });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

// ===============================
// GET ALL NOTES OF USER
// ===============================
export const getNotes = async (req, res) => {
  try {
    const notes = await prisma.notes.findMany({
      where: { user_id: req.user.id },
    });

    res.json({ notes });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

export const updateNote = async (req, res) => {
  try {
    const id = Number(req.params.id);  // FIX: Convert to Number

    const note = await prisma.notes.findUnique({
      where: { id }
    });

    if (!note) {
      return res.status(404).json({ message: "Note not found" });
    }

    const updated = await prisma.notes.update({
      where: { id },
      data: {
        subject_code: req.body.subject_code,
        note: req.body.note
      }
    });

    res.json({ message: "Note updated", updated });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};


export const deleteNote = async (req, res) => {
  try {
    const id = Number(req.params.id);  // FIX: Convert to Number

    const note = await prisma.notes.findUnique({
      where: { id }
    });

    if (!note) {
      return res.status(404).json({ message: "Note not found" });
    }

    await prisma.notes.delete({
      where: { id }
    });

    res.json({ message: "Note deleted successfully" });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
