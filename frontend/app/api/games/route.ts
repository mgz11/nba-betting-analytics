import { NextResponse } from "next/server";
import pool from "@/lib/db";

export async function GET() {
	try {
		const result = await pool.query(`
            SELECT
                id,
                external_game_id,
                game_date,
                home_team,
                away_team,
                home_score,
                away_score,
                spread_home,
                spread_away,
                moneyline_home,
                moneyline_away,
                total
                FROM games
                ORDER BY game_date DESC
            `);

		return NextResponse.json(result.rows);
	} catch (error) {
		console.error(error);
		return NextResponse.json({ error: "Failed to fetch games" }, { status: 500 });
	}
}
