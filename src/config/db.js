import { PrismaClient } from "@prisma/client";

let prisma;

try {
  prisma = new PrismaClient();
  console.log("🧠 Prisma client initialized");
} catch (error) {
  console.warn("⚠️ Prisma initialization skipped (no DB URL)");
}

export const connectDB = async () => {
  if (process.env.DATABASE_URL) {
    try {
      await prisma.$connect();
      console.log("✅ Database connected successfully");
    } catch (err) {
      console.error("❌ Database connection failed:", err.message);
    }
  } else {
    console.log("⚠️ No DATABASE_URL found — DB connection skipped");
  }
};

export default prisma;
