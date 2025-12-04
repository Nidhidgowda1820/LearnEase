/*
  Warnings:

  - You are about to drop the `modules` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `questions` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `subjects` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `syllabus_items` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `users` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "public"."modules" DROP CONSTRAINT "modules_subject_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."questions" DROP CONSTRAINT "questions_module_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."questions" DROP CONSTRAINT "questions_subject_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."syllabus_items" DROP CONSTRAINT "syllabus_items_module_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."syllabus_items" DROP CONSTRAINT "syllabus_items_subject_id_fkey";

-- DropTable
DROP TABLE "public"."modules";

-- DropTable
DROP TABLE "public"."questions";

-- DropTable
DROP TABLE "public"."subjects";

-- DropTable
DROP TABLE "public"."syllabus_items";

-- DropTable
DROP TABLE "public"."users";

-- CreateTable
CREATE TABLE "embeddings" (
    "subject" TEXT NOT NULL,
    "module" SMALLINT NOT NULL,
    "vector" DOUBLE PRECISION,
    "content" TEXT,

    CONSTRAINT "embeddings_pkey" PRIMARY KEY ("subject")
);

-- CreateTable
CREATE TABLE "notes" (
    "id" SERIAL NOT NULL,
    "user_id" UUID,
    "subject_code" VARCHAR(16),
    "note" TEXT,
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "notes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "profiles" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "name" VARCHAR(80),
    "email" VARCHAR(120),
    "created_at" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
    "password" VARCHAR(255) NOT NULL,

    CONSTRAINT "profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "syllabus" (
    "id" SERIAL NOT NULL,
    "subject_code" VARCHAR(16),
    "subject" VARCHAR(128),
    "semester" INTEGER,

    CONSTRAINT "syllabus_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "User" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "password" TEXT NOT NULL,
    "branch" TEXT,
    "year" INTEGER,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "documents" (
    "id" BIGSERIAL NOT NULL,
    "subject" TEXT,
    "module" TEXT,
    "marks_type" TEXT,
    "question" TEXT,
    "answer" TEXT,
    "embedding" vector,
    "created_at" TIMESTAMPTZ(6) DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "documents_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "profiles_email_key" ON "profiles"("email");

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- CreateIndex
CREATE INDEX "documents_embedding_idx" ON "documents"("embedding");

-- AddForeignKey
ALTER TABLE "notes" ADD CONSTRAINT "notes_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "profiles"("id") ON DELETE SET NULL ON UPDATE CASCADE;
