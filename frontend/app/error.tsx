"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <Card className="w-full max-w-lg text-center shadow-sm">
        <CardHeader>
          <CardDescription className="font-semibold uppercase tracking-wider text-red-700">
            Dashboard unavailable
          </CardDescription>
          <CardTitle className="text-2xl font-bold">
            Analytics could not be loaded
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Check the database connection and try loading the dashboard again.
          </p>
          <Button type="button" onClick={reset} className="mt-6">
            Try again
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}
