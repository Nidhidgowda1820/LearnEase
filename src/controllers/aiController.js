import { genAI } from "../config/gemini.js";

export const generateSummary = async (req, res) => {
  try {
    const { subject_code, topic, content } = req.body;
    if (!topic) return res.status(400).json({ error: "topic is required" });

    // Use stable 2025 model name
    const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });

    const prompt = `
You are a VTU exam tutor.
Subject: ${subject_code || "N/A"}
Topic: ${topic}

Generate a concise 10-marks exam summary:
${content || "Please use your knowledge"}.
`;

    const result = await model.generateContent(prompt);
    const text = await result.response.text();

    res.json({ topic, subject_code, summary: text });
  } catch (error) {
    console.error("generateSummary error:", error);
    res.status(500).json({ error: error.message });
  }
};
