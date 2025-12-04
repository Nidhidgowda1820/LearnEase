import prisma from "../config/db.js";

export const getSubjects = async (req, res) => {
  try {
    const subjects = await prisma.syllabus.findMany({
      select: { 
        id: true,
        subject_code: true, 
        subject: true, 
        semester: true 
      },
      orderBy: { semester: 'asc' }
    });
    res.json(subjects);
  } catch (error) {
    console.error("getSubjects error:", error);
    res.status(500).json({ error: error.message });
  }
};
