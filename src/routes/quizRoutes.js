import express from "express";
import { 
  createQuiz, 
  getQuizByTopic, 
  updateQuiz, 
  deleteQuiz 
} from "../controllers/quizController.js";

const router = express.Router();

// List quizzes by topic
router.get("/:subject_code/:topic", getQuizByTopic);

// CRUD operations
router.post("/", createQuiz);
router.put("/:id", updateQuiz);
router.delete("/:id", deleteQuiz);

export default router;
