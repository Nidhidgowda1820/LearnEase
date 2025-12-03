import axios from "axios";
import dotenv from "dotenv";
dotenv.config();

const AI_ENDPOINT = process.env.AI_ENDPOINT; // Provided by AI member
const AI_API_KEY = process.env.AI_API_KEY;   // Provided by AI member

export const generateAnswer = async (req, res) => {
  try {
    const { question, subject } = req.body;

    if (!question || !subject) {
      return res.status(400).json({ error: "Question and subject are required" });
    }

    // Call AI API (from AI member)
    const response = await axios.post(
      AI_ENDPOINT,
      { question, subject },
      { headers: { "Authorization": `Bearer ${AI_API_KEY}` } }
    );

    res.json({ answer: response.data.answer });
  } catch (error) {
    console.error(error.message);
    res.status(500).json({ error: "Failed to get AI answer" });
  }
};
