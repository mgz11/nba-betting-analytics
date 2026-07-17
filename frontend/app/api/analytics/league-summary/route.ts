import { NextResponse } from "next/server";
import { getLeagueSummaryData } from "@/lib/analytics/league-summary";

export async function GET() {
  try {
    return NextResponse.json(await getLeagueSummaryData());
  } catch (error) {
    console.error("Failed to fetch league summary", error);
    return NextResponse.json(
      { error: "Failed to fetch league summary" },
      { status: 500 },
    );
  }
}
