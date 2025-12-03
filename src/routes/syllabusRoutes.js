import express from "express";
import { getSyllabus } from "../controllers/syllabusController.js";

const router = express.Router();

// GET all syllabus OR by semester
router.get("/", getSyllabus);

export default router;
