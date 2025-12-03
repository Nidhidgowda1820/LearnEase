import express from "express";
import cors from "cors";
import bodyParser from "body-parser";

// Import Routes
import aiRoutes from "./routes/aiRoutes.js";
import userRoutes from "./routes/userRoutes.js";
import subjectRoutes from "./routes/subjectRoutes.js";
import notesRoutes from "./routes/notesRoutes.js";
import syllabusRoutes from "./routes/syllabusRoutes.js";

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

export default app;
