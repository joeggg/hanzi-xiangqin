import { Box, Text } from "@radix-ui/themes";
import { redirect } from "next/navigation";

import ResultsChart from "@/app/components/chart";
import client from "@/app/tools/client";

export default async function ResultsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const response = await client.get(`/tests/${id}/results`);
  const data = response.data;

  if (response.status === 404) {
    redirect(`/error`);
  }

  return response.status === 200 ? (
    <>
      <Text weight="bold" size="4" align="center">
        You know an estimated
        <br />
        <Text weight="bold" size="8" align="center">
          {data.count}+
        </Text>
        <br /> characters
      </Text>
      <Text>
        Breakdown:
        <br />
      </Text>
      <ResultsChart breakdown={data.breakdown} style={{ height: "auto" }} />
    </>
  ) : (
    <Text>Something went wrong, try refreshing</Text>
  );
}
