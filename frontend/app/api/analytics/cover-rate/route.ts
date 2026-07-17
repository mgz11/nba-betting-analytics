import { NextResponse } from "next/server";
import { getCoverRateData } from "@/lib/analytics/cover-rate";

export async function GET() {
  try {
    return NextResponse.json(await getCoverRateData());
  } catch (error) {
    console.error("Failed to fetch cover-rate analytics", error);
    return NextResponse.json(
      { error: "Failed to fetch cover-rate analytics" },
      { status: 500 },
    );
  }
}
