import express from "express";
import { getExamFocus } from "../controllers/examFocusController.js";

const router = express.Router();

router.get("/:subject_code", getExamFocus);

export default router;
