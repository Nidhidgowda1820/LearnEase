import prisma from "../config/db.js";

// CREATE NOTE
export const createNote = async (req, res) => {
  try {
    const { content, subject_code, user_id } = req.body;

    const noteRow = await prisma.notes.create({
      data: {
        note: content,        // maps to `note` column
        subject_code,         // optional
        user_id               // optional
      },
    });

    res.status(201).json(noteRow);
  } catch (error) {
    console.error("createNote error:", error);
    res.status(500).json({ error: error.message });
  }
};

export const getNoteById = async (req, res) => {
  try {
    const { id } = req.params;

    const note = await prisma.notes.findUnique({
      where: { id: Number(id) },
    });

    if (!note) {
      return res.status(404).json({ error: "Note not found" });
    }

    res.json(note);
  } catch (error) {
    console.error("getNoteById error:", error);
    res.status(500).json({ error: error.message });
  }
};

// UPDATE NOTE     -> PUT /api/notes/:id
export const updateNote = async (req, res) => {
  try {
    const { id } = req.params;
    const { content } = req.body;

    const note = await prisma.notes.update({
      where: { id: Number(id) },
      data: { note: content },
    });

    res.json(note);
  } catch (error) {
    console.error("updateNote error:", error);
    res.status(500).json({ error: error.message });
  }
};

// DELETE NOTE     -> DELETE /api/notes/:id
export const deleteNote = async (req, res) => {
  try {
    const { id } = req.params;

    await prisma.notes.delete({
      where: { id: Number(id) },
    });

    res.json({ message: "Note deleted" });
  } catch (error) {
    console.error("deleteNote error:", error);
    res.status(500).json({ error: error.message });
  }
};