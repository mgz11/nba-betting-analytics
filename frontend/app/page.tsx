import { getLeagueSummaryData } from "@/lib/analytics/league-summary";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export const dynamic = "force-dynamic";

type SummaryCardProps = {
	label: string;
	value: string;
	description: string;
};

function SummaryCard({ label, value, description }: SummaryCardProps) {
	return (
		<Card className="shadow-sm">
			<CardHeader>
				<CardDescription>{label}</CardDescription>
				<CardTitle className="text-3xl font-semibold tracking-tight">{value}</CardTitle>
			</CardHeader>
			<CardContent className="text-sm text-muted-foreground">{description}</CardContent>
		</Card>
	);
}

function formatNumber(value: unknown, digits = 1) {
	const number = Number(value);
	return Number.isFinite(number) ? number.toFixed(digits) : "—";
}

function formatInteger(value: unknown) {
	const number = Number(value);
	return Number.isFinite(number) ? Math.round(number).toLocaleString() : "—";
}

function formatPercent(value: unknown, digits = 1) {
	const number = Number(value);
	return Number.isFinite(number) ? `${(number * 100).toFixed(digits)}%` : "—";
}

function formatDate(value: unknown) {
	if (typeof value !== "string") return "—";

	return new Intl.DateTimeFormat("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
		timeZone: "UTC",
	}).format(new Date(`${value}T00:00:00Z`));
}

export default async function Home() {
	const { scoring_summary, betting_market_summary, results_by_date } = await getLeagueSummaryData();

	const scoring = scoring_summary ?? {};
	const betting = betting_market_summary ?? {};

	return (
		<main className="min-h-screen bg-slate-50 px-4 py-8 text-slate-950 sm:px-6 lg:px-8">
			<div className="mx-auto max-w-7xl space-y-10">
				<header>
					<p className="text-sm font-semibold uppercase tracking-wider text-blue-700">NBA analytics</p>
					<h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">League dashboard</h1>
					<p className="mt-2 max-w-2xl text-slate-600">
						A current snapshot of league scoring, betting markets, and favorite performance.
					</p>
				</header>

				<section aria-labelledby="scoring-heading">
					<div className="mb-4">
						<h2 id="scoring-heading" className="text-xl font-semibold">
							Scoring overview
						</h2>
						<p className="mt-1 text-sm text-slate-500">Completed games currently stored in the database.</p>
					</div>

					<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
						<SummaryCard
							label="Games played"
							value={formatInteger(scoring.games_played)}
							description="Completed games analyzed"
						/>
						<SummaryCard
							label="Average total"
							value={formatNumber(scoring.avg_total_points)}
							description="Combined points per game"
						/>
						<SummaryCard
							label="Average home score"
							value={formatNumber(scoring.avg_home_points)}
							description="Points scored by home teams"
						/>
						<SummaryCard
							label="Average home margin"
							value={formatNumber(scoring.avg_home_margin)}
							description="Home score minus away score"
						/>
					</div>
				</section>

				<section aria-labelledby="market-heading">
					<div className="mb-4">
						<h2 id="market-heading" className="text-xl font-semibold">
							Betting market
						</h2>
						<p className="mt-1 text-sm text-slate-500">
							Favorite pricing uses decimal odds and per-game implied probabilities.
						</p>
					</div>

					<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
						<SummaryCard
							label="Games with lines"
							value={formatInteger(betting.games_with_lines)}
							description="Games with at least one market"
						/>
						<SummaryCard
							label="Home favorites"
							value={formatInteger(betting.home_favorites)}
							description={`${formatInteger(betting.away_favorites)} away favorites`}
						/>
						<SummaryCard
							label="Average favorite price"
							value={formatNumber(betting.avg_favorite_decimal_odds, 2)}
							description={`${formatPercent(betting.avg_implied_probability)} average implied probability`}
						/>
						<SummaryCard
							label="Favorite win rate"
							value={formatPercent(betting.favorite_win_rate)}
							description="Completed games with a distinct favorite"
						/>
					</div>
				</section>

				<section aria-labelledby="results-heading">
					<div className="mb-4">
						<h2 id="results-heading" className="text-xl font-semibold">
							Recent league results
						</h2>
						<p className="mt-1 text-sm text-slate-500">Daily scoring and home-team performance.</p>
					</div>

					<Card className="py-0 shadow-sm">
						<Table className="min-w-2xl">
							<TableHeader className="bg-muted/60 text-xs uppercase tracking-wide text-muted-foreground">
								<TableRow>
									<TableHead className="px-5">Date</TableHead>
									<TableHead>Games</TableHead>
									<TableHead>Avg. total</TableHead>
									<TableHead>Avg. home margin</TableHead>
									<TableHead>Home wins</TableHead>
									<TableHead className="pr-5">Away wins</TableHead>
								</TableRow>
							</TableHeader>
							<TableBody>
								{results_by_date.slice(0, 10).map((result) => (
									<TableRow key={String(result.game_date)}>
										<TableCell className="px-5 py-4 font-medium">{formatDate(result.game_date)}</TableCell>
										<TableCell>{formatInteger(result.games_played)}</TableCell>
										<TableCell>{formatNumber(result.avg_total_points)}</TableCell>
										<TableCell>{formatNumber(result.avg_home_margin)}</TableCell>
										<TableCell>{formatInteger(result.home_wins)}</TableCell>
										<TableCell className="pr-5">{formatInteger(result.away_wins)}</TableCell>
									</TableRow>
								))}
							</TableBody>
						</Table>
					</Card>
				</section>
			</div>
		</main>
	);
}
