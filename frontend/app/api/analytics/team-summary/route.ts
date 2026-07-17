import { NextRequest, NextResponse } from "next/server";
import { getTeamSummaryData } from "@/lib/analytics/team-summary";

export async function GET(request: NextRequest) {
  const team = request.nextUrl.searchParams.get("team")?.trim();

  if (!team) {
    return NextResponse.json(
      { error: "The team query parameter is required" },
      { status: 400 },
    );
  }

  try {
    return NextResponse.json(await getTeamSummaryData(team));
  } catch (error) {
    console.error("Failed to fetch team summary", error);
    return NextResponse.json(
      { error: "Failed to fetch team summary" },
      { status: 500 },
    );
  }
}
