import prisma from "../config/db.js";

export const createQuiz = async (req, res) => {
  try {
    const { subject_code, topic, question, options, correct } = req.body;
    
    const quiz = await prisma.quizzes.create({
      data: { subject_code, topic, question, options, correct }
    });
    res.status(201).json(quiz);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const getQuizByTopic = async (req, res) => {
  try {
    const { subject_code, topic } = req.params;
    const quizzes = await prisma.quizzes.findMany({
      where: { subject_code, topic }
    });
    res.json(quizzes);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const updateQuiz = async (req, res) => {
  try {
    const { id } = req.params;
    const data = req.body;
    
    const quiz = await prisma.quizzes.update({
      where: { id: Number(id) },
      data
    });
    res.json(quiz);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const deleteQuiz = async (req, res) => {
  try {
    const { id } = req.params;
    
    await prisma.quizzes.delete({
      where: { id: Number(id) }
    });
    res.json({ message: "Quiz deleted" });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
