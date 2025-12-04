import { HfInference } from "@huggingface/inference";
import dotenv from "dotenv";
dotenv.config();

const hf = new HfInference(process.env.HUGGINGFACE_API_KEY);
export default hf;
