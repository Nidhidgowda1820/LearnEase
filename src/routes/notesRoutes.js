import express from "express";
import { auth } from "../middleware/auth.js";
import { PrismaClient } from "@prisma/client";
import {
  createNote,
  getNotes,
  updateNote,
  deleteNote
} from "../controllers/notesController.js";


const prisma = new PrismaClient();
const router = express.Router();

// Create a note
router.post("/", auth, async (req, res) => {
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
});

// Get all notes of user
router.get("/", auth, async (req, res) => {
  try {
    const notes = await prisma.notes.findMany({
      where: { user_id: req.user.id },
    });

    res.json(notes);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
router.get("/", auth, getNotes);
router.put("/:id", auth, updateNote);


router.put("/:id", auth, updateNote);
router.delete("/:id", auth, deleteNote);
