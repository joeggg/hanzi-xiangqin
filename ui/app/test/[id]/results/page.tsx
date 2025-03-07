import { Text } from "@radix-ui/themes";

import client from "app/tools/client";

export default async function ResultsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const response = await client.get(`/tests/${id}/results`);
  const data = response.data;

  return response.status === 200 ? (
    <>
      <Text weight="bold" size="4" align="center">
        You know an estimated
        <br />
        <Text weight="bold" size="8" align="center">
          {data.count}
        </Text>
        <br /> characters
      </Text>
      <Text>
        Breakdown:
        <br />
        {JSON.stringify(data.breakdown, null, 2)}
      </Text>
    </>
  ) : (
    <Text>Something went wrong, try refreshing</Text>
  );
}
