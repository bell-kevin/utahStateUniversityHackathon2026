import { NextResponse } from "next/server";
import { evaluateInspection } from "@/lib/smartAsset";

export async function POST(request: Request) {
  const body = (await request.json()) as { note?: string };

  if (!body.note || body.note.trim().length < 5) {
    return NextResponse.json(
      { error: "Inspection note must be at least 5 characters long." },
      { status: 400 }
    );
  }

  const assessment = evaluateInspection(body.note);
  return NextResponse.json(assessment);
}
