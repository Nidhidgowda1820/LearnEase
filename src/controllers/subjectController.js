import prisma from "../config/db.js";

// GET /api/subjects
export const getSubjects = async (req, res) => {
  try {
    const subjects = await prisma.subject.findMany({
      include: { QPs: true }, // include question papers
    });
    res.json({ subjects });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Failed to fetch subjects" });
  }
};

// POST /api/subjects
export const createSubject = async (req, res) => {
  try {
    const { name, branch, year, syllabus } = req.body;
    const newSubject = await prisma.subject.create({
      data: { name, branch, year, syllabus },
    });
    res.json({ subject: newSubject });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Failed to create subject" });
  }
};
