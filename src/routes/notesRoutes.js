import express from "express";
import {
  createNote,
  getNoteById,
  updateNote,
  deleteNote
} from "../controllers/notesController.js";

const router = express.Router();

router.post("/", createNote);
router.get("/:id", getNoteById);  
router.put("/:id", updateNote);
router.delete("/:id", deleteNote);

export default router;
