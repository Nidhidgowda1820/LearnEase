
// src/routes/syllabusRoutes.js
import express from "express";
import { getSubjects } from "../controllers/syllabusController.js";

const router = express.Router();

router.get("/", getSubjects);

export default router;
