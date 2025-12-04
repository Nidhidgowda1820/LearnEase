import express from "express";
import cors from "cors";
import bodyParser from "body-parser";

// Import Routes
import aiRoutes from "./routes/aiRoutes.js";
import userRoutes from "./routes/userRoutes.js";
import subjectRoutes from "./routes/subjectRoutes.js";
import notesRoutes from "./routes/notesRoutes.js";
import syllabusRoutes from "./routes/syllabusRoutes.js";
import examFocusRoutes from "./routes/examFocusRoutes.js";
import quizRoutes from "./routes/quizRoutes.js";
import authRoutes from './routes/authRoutes.js';
import { authenticateToken } from './middleware/auth.js';

const app = express();

// Middlewares
app.use(cors());
app.use(bodyParser.json());

// Routes
app.use("/api/ai", aiRoutes);
app.use("/api/users", userRoutes);
app.use("/api/subjects", subjectRoutes);
app.use("/api/ai", aiRoutes);
app.use("/api/notes", notesRoutes);
app.use("/api/syllabus", syllabusRoutes);
app.use("/api/quizzes", quizRoutes);
app.use("/api/exam-focus", examFocusRoutes);
app.use('/api/auth', authRoutes);

app.use('/api/notes', authenticateToken);
app.use('/api/quizzes', authenticateToken);
export default app;
