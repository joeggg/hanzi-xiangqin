import { Text } from "@radix-ui/themes";

export default async function ResultsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_BASE_URL}/tests/${id}/results`,
  );
  const data = await response.json();

  return response.ok ? (
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
