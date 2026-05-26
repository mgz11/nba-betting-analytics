async function getGames() {
	const res = await fetch("http://localhost:3000/api/games", {
		cache: "no-store",
	});

	if (!res.ok) {
		throw new Error("Failed to fetch games");
	}

	return res.json();
}

export default async function Home() {
	const games = await getGames();

	return (
		<main className="min-h-screen bg-slate-950 text-white p-8">
			<section className="max-w-6xl mx-auto space-y-6">
				<div>
					<h1 className="text-3xl font-bold">Sports Betting Analytics</h1>
					<p className="text-slate-400 mt-2">Analyze how NBA teams perform relative to sportsbook expectations.</p>
				</div>

				<div className="rounded-xl border border-slate-800 overflow-hidden">
					<table className="w-full text-sm">
						<thead className="bg-slate-900">
							<tr>
								<th className="text-left p-3">Date</th>
								<th className="text-left p-3">Matchup</th>
								<th className="text-left p-3">Home Spread</th>
								<th className="text-left p-3">Total</th>
							</tr>
						</thead>
						<tbody>
							{games.map((game: any) => (
								<tr key={game.id} className="border-t border-slate-800">
									<td className="p-3">{new Date(game.game_date).toLocaleDateString()}</td>
									<td className="p-3">
										{game.away_team} @ {game.home_team}
									</td>
									<td className="p-3">{game.spread_home}</td>
									<td className="p-3">{game.total}</td>
								</tr>
							))}
						</tbody>
					</table>
				</div>
			</section>
		</main>
	);
}
