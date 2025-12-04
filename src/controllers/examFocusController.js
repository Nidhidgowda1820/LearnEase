import prisma from "../config/db.js";

export const getExamFocus = async (req, res) => {
  try {
    const { subject_code } = req.params;

    // Dummy example: fetch latest 10 questions from documents table
    const questions = await prisma.documents.findMany({
      where: { subject: subject_code },
      orderBy: { id: "desc" },
      take: 10,
      select: {
        question: true,
        marks_type: true,
        module: true,
      },
    });

    res.json({ highWeightageQuestions: questions });
  } catch (error) {
    console.error("getExamFocus error:", error);
    res.status(500).json({ error: error.message });
  }
};
