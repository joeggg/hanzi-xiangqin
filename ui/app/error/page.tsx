import { Text } from "@radix-ui/themes";

export default async function ErrorPage({
  searchParams,
}: {
  searchParams: Promise<{ code: string }>;
}) {
  const { code } = await searchParams;

  return code === "notfound" ? (
    <Text>Test does not exist</Text>
  ) : (
    <Text>An unexpected error occurred</Text>
  );
}
