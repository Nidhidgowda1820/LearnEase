import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

export const getSyllabus = async (req, res) => {
  try {
    const { semester } = req.query;

    let syllabus;

    if (semester) {
      syllabus = await prisma.syllabus.findMany({
        where: { semester: Number(semester) }
      });
    } else {
      syllabus = await prisma.syllabus.findMany();
    }

    res.json({ syllabus });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
