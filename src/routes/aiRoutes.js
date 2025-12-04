import express from "express";
import { generateSummary } from "../controllers/aiController.js";

const router = express.Router();

router.post("/summarize", generateSummary);

export default router;
