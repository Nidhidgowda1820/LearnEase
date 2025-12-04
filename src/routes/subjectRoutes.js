import express from "express";
const router = express.Router();

// Test route
router.get("/", (req, res) => {
  res.json({ message: "Subject routes working!" });
});

export default router;
